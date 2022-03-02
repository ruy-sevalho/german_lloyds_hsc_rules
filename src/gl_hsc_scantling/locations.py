# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 12:19:42 2021

@author: ruy
"""


from abc import abstractmethod
from typing import TYPE_CHECKING


from dataclasses import dataclass, field

import numpy as np
from dataclass_tools.tools import DESERIALIZER_OPTIONS

from gl_hsc_scantling.vessel import Vessel

from .locations_abc import Location, Pressure
from .panels import Panel
from .stiffeners import Stiffener
from .common_field_options import (
    AIR_GAP_OPTIONS,
    DEADRISE_OPTIONS,
    DECKHOUSE_BREADTH_OPTIONS,
)

if TYPE_CHECKING:
    from .elements import StructuralElement
# Helper functions, all 'pure'.
def _pressure_sea_f(z_baseline, draft, p_sea_min, factor_S):
    if z_baseline <= draft:
        p = 10 * (draft + 0.75 * factor_S - (1 - 0.25 * factor_S / draft) * z_baseline)
    else:
        p = 10 * (draft + factor_S - z_baseline)
    return np.max([p_sea_min, p])


def _pressure_sea_interpolate_f(
    x_pos: float, pressure_below_05: float, pressure_above_09: float
) -> float:
    xp = [0.5, 0.9]
    fp = [pressure_below_05, pressure_above_09]
    return np.interp(x_pos, xp, fp)


def _factor_S_fwd_f(vert_acg, length, block_coef, draft):
    """Table C3.5.2"""
    return np.max(
        [
            np.min(
                [
                    0.36 * vert_acg * length**0.5 / np.min([block_coef, 0.5]),
                    3.5 * draft,
                ]
            ),
            draft,
        ]
    )


def _factor_S_aft_f(vert_acg, length, draft):
    """Table C3.5.2"""
    return np.max(
        [
            np.min(
                [
                    0.60 * vert_acg * length**0.5,
                    2.5 * draft,
                ]
            ),
            draft,
        ]
    )


def _preassure_sea_min_aft_f(length):
    return np.max([10, np.min([(length + 75) / 10, 20])])


def _preassure_sea_min_f(preassure_sea_min_aft, preassure_sea_min_fwd, x_pos):
    xp = [0, 0.5, 0.9, 1]
    fp = [
        preassure_sea_min_aft,
        preassure_sea_min_aft,
        preassure_sea_min_fwd,
        preassure_sea_min_fwd,
    ]
    return np.interp(x_pos, xp, fp)


def _preassure_sea_min_fwd_f(length):
    return np.max([20, np.min([(length + 75) / 5, 35])])


def _x_lim_f(vert_acg, x_lim_Froude_n_min, x_lim_Froude_n_max):
    if vert_acg <= 1:
        return x_lim_Froude_n_min
    elif vert_acg <= 1.5:
        return x_lim_Froude_n_max
    else:
        return 0


def _x_lim_sp_len_ratio_min_f(
    sp_len_ratio,
    x_lim_min_acg_inf,
    x_lim_min_acg_sup,
):
    if sp_len_ratio < 4.5:
        return x_lim_min_acg_inf
    elif sp_len_ratio <= 5:
        return x_lim_min_acg_sup
    else:
        return 0


def _x_lim_sp_len_ratio_max_f(
    sp_len_ratio,
    x_lim_max_acg,
):
    if sp_len_ratio < 5:
        return x_lim_max_acg
    else:
        return 0


def _ref_area_f(displacement, draft):
    return 0.7 * (displacement / 2) / draft


def _area_f(span, spacing):
    return span * spacing


def _effective_deadrise(deadrise):
    return np.max([10, np.min([deadrise, 30])])


def _coef_k3_f(deadrise_eff, deadrise_lcg_eff):
    return (70 - deadrise_eff) / (70 - deadrise_lcg_eff)


def _param_u_f(area, ref_area):
    return 100 * area / ref_area


def _coef_k2_f(param_u, k2_min) -> float:
    k2 = 0.455 - 0.35 * ((param_u**0.75 - 1.7) / (param_u**0.75 + 1.7))
    return np.max([k2_min, k2])


def _pressure_impact_f(
    x_pos,
    x_lim,
    pressure_impact_pre,
    pressure_impact_limit,
    pressure_sea_lim,
):
    if x_pos > x_lim:
        return pressure_impact_pre
    elif x_pos > x_lim - 0.1:
        xp = [0, 0.1]
        fp = [pressure_sea_lim, pressure_impact_limit]
        corrected_x = x_pos - x_lim + 0.1
        return np.interp(corrected_x, xp, fp)
    else:
        return 0


def _coef_k1_f(x_pos):
    xp = [0, 0.5, 0.8, 1]
    fp = [0.5, 1, 1, 0.5]
    return np.interp(x_pos, xp, fp)


def _pressure_impact_bottom_pre_f(draft, vert_acg, coef_k1, coef_k2, coef_k3):
    return 100 * draft * coef_k1 * coef_k2 * coef_k3 * vert_acg


def _coef_kwd_f(x_pos):
    xp = [0, 0.2, 0.7, 0.8, 1]
    fp = [0.5, 0.4, 0.4, 1, 1]
    return np.interp(x_pos, xp, fp)


def _rel_impact_vel_f(sig_wave_height, length):
    return 4 * sig_wave_height / length**0.5 + 1


def _pressure_impact_wet_deck_pre_f(
    speed, sig_wave_height, air_gap, coef_k2, coef_k3, coef_kwd, rel_impact_vel
):
    return (
        3
        * coef_k2
        * coef_k3
        * coef_kwd
        * speed
        * rel_impact_vel
        * (1 - 0.85 * air_gap / sig_wave_height)
    )


def _pressure_deck_f(z_waterline):
    xp = [0, 2, 3, 4]
    fp = [6, 6, 3, 3]
    return np.interp(z_waterline, xp, fp)


def _x1_f(midship, x_pos, x):
    if x_pos > midship:
        return np.abs(x - midship)
    else:
        return 0


def _coef_ksu_f(beam, deckhouse_breadth):
    return np.max([3, np.min([5, 1.5 + 3.5 * deckhouse_breadth / beam])])


def _pressure_walls_f(
    length, block_coef, z_waterline, coef_ksu, x1, pressure_walls_min
):
    return np.max(
        [
            (
                coef_ksu
                * (1 + x1 / (2 * length * (block_coef + 0.1)))
                * (1 + 0.045 * length - 0.38 * z_waterline)
            ),
            pressure_walls_min,
        ]
    )


def _pressure_walls_min_f(length):
    return 6.5 + 0.06 * length


# Pressures
class Sea(Pressure):
    """C3.5.5.1 Sea pressure on bottom and side shell"""

    name = "sea"

    def calc(self, elmt: "StructuralElement") -> float:
        return self._pressure(elmt)

    def _pressure_limit(self, elmt: "StructuralElement", x_lim: float) -> float:
        return _pressure_sea_interpolate_f(
            x_pos=x_lim,
            pressure_below_05=self._pressure_below_05L(elmt=elmt),
            pressure_above_09=self._pressure_above_09L(elmt=elmt),
        )

    def _pressure(self, elmt: "StructuralElement") -> float:
        """C3.5.5.1"""
        return _pressure_sea_interpolate_f(
            x_pos=elmt.x_pos,
            pressure_below_05=self._pressure_below_05L(elmt=elmt),
            pressure_above_09=self._pressure_above_09L(elmt=elmt),
        )

    def _pressure_below_05L(self, elmt: "StructuralElement") -> float:
        return _pressure_sea_f(
            z_baseline=elmt.z_baseline,
            draft=elmt.vessel.draft,
            p_sea_min=self._preassure_sea_min_aft(elmt=elmt),
            factor_S=self._factor_S_aft(elmt=elmt),
        )

    def _pressure_above_09L(self, elmt: "StructuralElement") -> float:
        return _pressure_sea_f(
            z_baseline=elmt.z_baseline,
            draft=elmt.vessel.draft,
            p_sea_min=self._preassure_sea_min_fwd(elmt=elmt),
            factor_S=self._factor_S_fwd(elmt=elmt),
        )

    def _factor_S_fwd(self, elmt):
        """Table C3.5.2"""
        return _factor_S_fwd_f(
            vert_acg=elmt.vessel.draft,
            length=elmt.vessel.length,
            block_coef=elmt.vessel.block_coef,
            draft=elmt.vessel.draft,
        )

    def _factor_S_aft(self, elmt):
        """Table C3.5.2"""
        return _factor_S_aft_f(
            vert_acg=elmt.vessel.vert_acg,
            length=elmt.vessel.length,
            draft=elmt.vessel.draft,
        )

    def _preassure_sea_min_fwd(self, elmt):
        return _preassure_sea_min_fwd_f(length=elmt.vessel.length)

    def _preassure_sea_min_aft(self, elmt):
        return _preassure_sea_min_aft_f(elmt.vessel.length)

    def _preassure_sea_min(self, elmt) -> float:
        return _preassure_sea_min_f(
            preassure_sea_min_aft=self._preassure_sea_min_aft(elmt),
            preassure_sea_min_fwd=self._preassure_sea_min_fwd(elmt),
            x_pos=elmt.x_pos,
        )


class ImpactPressure(Pressure):
    """C3.5.3 Impact pressure on the bottom hull parameters and calculation."""

    name = "impact"
    sea_pressure = Sea()
    _coef_k2_min_table = {Panel: 0.5, Stiffener: 0.45}

    def calc(self, elmt) -> float:
        return self._pressure_impact(elmt)

    def _x_lim(self, elmt: "StructuralElement") -> float:
        return _x_lim_f(
            vert_acg=elmt.vessel.vert_acg,
            x_lim_Froude_n_min=self._x_lim_sp_len_ratio_min(elmt),
            x_lim_Froude_n_max=self._x_lim_sp_len_ratio_max(elmt),
        )

    def _x_lim_sp_len_ratio_min(self, elmt: "StructuralElement") -> float:
        return _x_lim_sp_len_ratio_min_f(
            sp_len_ratio=elmt.vessel.sp_len_ratio,
            x_lim_min_acg_inf=self._x_lim_min_acg_inf,
            x_lim_min_acg_sup=self._x_lim_min_acg_sup,
        )

    def _x_lim_sp_len_ratio_max(self, elmt: "StructuralElement") -> float:
        return _x_lim_sp_len_ratio_max_f(
            sp_len_ratio=elmt.vessel.sp_len_ratio,
            x_lim_max_acg=self._x_lim_max_acg,
        )

    def _ref_area(self, elmt: "StructuralElement"):
        return _ref_area_f(
            displacement=elmt.vessel.displacement, draft=elmt.vessel.draft
        )

    def _coef_k3(self, elmt: "StructuralElement"):
        return _coef_k3_f(
            deadrise_eff=_effective_deadrise(elmt.location.deadrise),
            deadrise_lcg_eff=_effective_deadrise(elmt.vessel.deadrise_lcg),
        )

    def _param_u(self, elmt: "StructuralElement"):
        return _param_u_f(area=elmt.model.area, ref_area=self._ref_area(elmt))

    def _coef_k2(self, elmt: "StructuralElement"):
        return _coef_k2_f(
            self._param_u(elmt), self._coef_k2_min_table[type(elmt.model)]
        )

    def _pressure_sea_limit(self, elmt: "StructuralElement") -> float:
        return self.sea_pressure._pressure_limit(
            elmt=elmt, x_lim=self._x_lim(elmt) - 0.1
        )

    def _pressure_impact(self, elmt: "StructuralElement"):
        return _pressure_impact_f(
            x_pos=elmt.x_pos,
            x_lim=self._x_lim(elmt),
            pressure_impact_pre=self._pressure_impact_pre(elmt),
            pressure_impact_limit=self._pressure_impact_limit(elmt),
            pressure_sea_lim=self._pressure_sea_limit(elmt=elmt),
        )

    @abstractmethod
    def _pressure_impact_pre(self, elmt: "StructuralElement"):
        pass

    @abstractmethod
    def _pressure_impact_limit(self, elmt: "StructuralElement"):
        pass


class ImpactBottomPressure(ImpactPressure):
    """C3.5.3 Impact pressure on the bottom of hull"""

    _x_lim_min_acg_inf = 0.7
    _x_lim_min_acg_sup = 0.5
    _x_lim_max_acg = 0.5

    def _coef_k1(self, elmt) -> float:
        return _coef_k1_f(x_pos=elmt.x_pos)

    def _coef_k1_limit(self, elmt: "StructuralElement") -> float:
        return _coef_k1_f(x_pos=self._x_lim(elmt))

    def _pressure_impact_pre(self, elmt: "StructuralElement") -> float:
        return _pressure_impact_bottom_pre_f(
            draft=elmt.vessel.draft,
            vert_acg=elmt.vessel.vert_acg,
            coef_k1=self._coef_k1(elmt),
            coef_k2=self._coef_k2(elmt),
            coef_k3=self._coef_k3(elmt),
        )

    def _pressure_impact_limit(self, elmt: "StructuralElement") -> float:
        return _pressure_impact_bottom_pre_f(
            draft=elmt.vessel.draft,
            vert_acg=elmt.vessel.vert_acg,
            coef_k1=self._coef_k1_limit(elmt),
            coef_k2=self._coef_k2(elmt),
            coef_k3=self._coef_k3(elmt),
        )


class ImpactWetDeckPressure(ImpactPressure):
    """C3.5.4 Impact pressure on wet deck"""

    _x_lim_min_acg_inf = 0.8
    _x_lim_min_acg_sup = 0.7
    _x_lim_max_acg = 0.7

    def _coef_kwd(self, elmt: "StructuralElement"):
        return _coef_kwd_f(x_pos=elmt.x_pos)

    def _rel_impact_vel(self, elmt: "StructuralElement"):
        return _rel_impact_vel_f(
            sig_wave_height=elmt.vessel.sig_wave_height, length=elmt.vessel.length
        )

    def _pressure_impact_pre(self, elmt: "StructuralElement"):
        return _pressure_impact_wet_deck_pre_f(
            speed=elmt.vessel.speed,
            sig_wave_height=elmt.vessel.sig_wave_height,
            air_gap=elmt.location.air_gap,
            coef_k2=self._coef_k2(elmt),
            coef_k3=self._coef_k3(elmt),
            coef_kwd=self._coef_kwd(elmt),
            rel_impact_vel=self._rel_impact_vel(elmt),
        )

    def _coef_kwd_limit(self, elmt: "StructuralElement") -> float:
        return _coef_kwd_f(self._x_lim(elmt))

    def _pressure_impact_limit(self, elmt):
        return _pressure_impact_wet_deck_pre_f(
            speed=elmt.vessel.speed,
            sig_wave_height=elmt.vessel.sig_wave_height,
            air_gap=elmt.location.air_gap,
            coef_k2=self._coef_k2(elmt),
            coef_k3=self._coef_k3(elmt),
            coef_kwd=self._coef_kwd_limit(elmt),
            rel_impact_vel=self._rel_impact_vel(elmt),
        )


class DeckPressure(Pressure):
    """C3.5.8.2 Weather decks and exposed areas."""

    name = "deck"

    def calc(self, elmt: "StructuralElement"):
        return self._pressure_deck(elmt)

    def _pressure_deck(self, elmt: "StructuralElement"):
        return _pressure_deck_f(z_waterline=elmt.z_waterline)


class DeckHousePressure(Pressure):
    """C3.5.5.5 Sea pressures on deckhouses."""

    name = "deckhouse"

    def calc(self, elmt: "StructuralElement"):
        return self._pressure_walls(elmt)

    def _x1(self, elmt: "StructuralElement"):
        return _x1_f(midship=elmt.vessel.midship, x_pos=elmt.x_pos, x=elmt.x)

    def _coef_ksu(self, elmt: "StructuralElement"):
        return _coef_ksu_f(
            beam=elmt.vessel.beam, deckhouse_breadth=elmt.location.deckhouse_breadth
        )

    def _pressure_walls(self, elmt: "StructuralElement"):
        return _pressure_walls_f(
            length=elmt.vessel.lenght,
            block_coef=elmt.vessel.block_coef,
            z_waterline=elmt.z_waterline,
            coef_ksu=self._coef_ksu(elmt),
            x1=self._x1(elmt),
            pressure_walls_min=self._pressure_walls_min(elmt),
        )

    @abstractmethod
    def _pressure_walls_min(self, elmt: "StructuralElement"):
        pass


class DeckHouseMainFrontPressure(DeckHousePressure):
    name = "deckhouse main front"

    def _pressure_walls_min(self, elmt: "StructuralElement"):
        return _pressure_walls_min_f(length=elmt.vessel.length)


class DeckHouseMainSidePressure(DeckHousePressure):
    name = "deckhouse main side"

    def _pressure_walls_min(self, elmt: "StructuralElement"):
        return 4


class DeckHouseOtherPressure(DeckHousePressure):
    name = "deckhouse other"

    def _pressure_walls_min(self, elmt: "StructuralElement"):
        return 3


# Location
@dataclass
class Bottom(Location):
    deadrise: float = field(metadata={DESERIALIZER_OPTIONS: DEADRISE_OPTIONS})
    name = "bottom"

    @property
    def _pressures(self):
        return [Sea(), ImpactBottomPressure()]


@dataclass
class Side(Location):
    name = "side"

    @property
    def _pressures(self):
        return [Sea()]


@dataclass
class Deck(Location):
    name = "deck"

    @property
    def _pressures(self):
        return [DeckPressure()]


@dataclass
class WetDeck(Location):
    deadrise: float = field(metadata={DESERIALIZER_OPTIONS: DEADRISE_OPTIONS})
    air_gap: float = field(metadata={DESERIALIZER_OPTIONS: AIR_GAP_OPTIONS})

    name = "wet deck"

    @property
    def _pressures(self):
        return [Sea(), ImpactWetDeckPressure()]


@dataclass
class DeckHouseMainFront(Location):

    deckhouse_breadth: float = field(
        metadata={DESERIALIZER_OPTIONS: DECKHOUSE_BREADTH_OPTIONS}
    )

    name = "deckhouse main front"

    @property
    def _pressures(self):
        return [DeckHouseMainFrontPressure()]


@dataclass
class DeckHouseMainSide(Location):
    deckhouse_breadth: float = field(
        metadata={DESERIALIZER_OPTIONS: DECKHOUSE_BREADTH_OPTIONS}
    )
    name = "deckhouse main side"

    @property
    def _pressures(self):
        return [DeckHouseMainSidePressure()]


@dataclass
class DeckHouseOther(Location):
    deckhouse_breadth: float = field(
        metadata={DESERIALIZER_OPTIONS: DECKHOUSE_BREADTH_OPTIONS}
    )
    name = "deckhouse other"

    @property
    def _pressures(self):
        return [DeckHouseOtherPressure()]
