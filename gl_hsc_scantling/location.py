# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 12:19:42 2021

@author: ruy
"""
from functools import cached_property
from enum import Enum
from abc import ABC, abstractmethod
from typing import List

import numpy as np
from marshmallow_dataclass import dataclass
from .vessel import Vessel

# Helper functions, all 'pure'.
def _pressure_sea_f(z_baseline, draft, p_sea_min, factor_S):
    if z_baseline <= draft:
        p = 10 * (draft + 0.75 * factor_S - (1 - 0.25 * factor_S / draft) * z_baseline)
    else:
        p = 10 * (draft + factor_S - z_baseline)
    return np.max([p_sea_min, p])


def _factor_S_fwd_f(vert_acg, length, block_coef, draft):
    """Table C3.5.2"""
    return np.max(
        [
            np.min(
                [
                    0.36 * vert_acg * length ** 0.5 / np.min([block_coef, 0.5]),
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
                    0.60 * vert_acg * length ** 0.5,
                    2.5 * draft,
                ]
            ),
            draft,
        ]
    )


def _factor_S_f(factor_S_aft, factor_S_fwd, x_pos):
    """Table C3.5.2"""
    xp = [0, 0.5, 0.9, 1]
    fp = [
        factor_S_aft,
        factor_S_aft,
        factor_S_fwd,
        factor_S_fwd,
    ]
    return np.interp(x_pos, xp, fp)


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
    min_acg_froude_limit_inf,
    min_acg_froude_limit_sup,
    x_lim_min_acg_inf,
    x_lim_min_acg_sup,
):
    if sp_len_ratio < min_acg_froude_limit_inf:
        return x_lim_min_acg_inf
    elif sp_len_ratio <= min_acg_froude_limit_sup:
        return x_lim_min_acg_sup
    else:
        return 0


def _x_lim_sp_len_ratio_max_f(
    sp_len_ratio,
    max_acg_froude_limit_inf,
    max_acg_froude_limit,
    x_lim_max_acg_inf,
    x_lim_max_acg,
):
    if sp_len_ratio < max_acg_froude_limit_inf:
        return x_lim_max_acg_inf
    elif sp_len_ratio <= max_acg_froude_limit:
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


def _coef_k2_f(param_u):
    return 0.455 - 0.35 * ((param_u ** 0.75 - 1.7) / (param_u ** 0.75 + 1.7))


def _pressure_impact_f(x_pos, x_lim, pressure_impact_pre, pressure_sea):
    if x_pos > x_lim:
        return pressure_impact_pre
    elif x_pos > x_lim - 0.1:
        xp = [0, 0.1]
        fp = [pressure_impact_pre, pressure_sea]
        return np.interp(x_pos - x_lim, xp, fp)
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
    return 4 * sig_wave_height / length ** 0.5 + 1


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


# Abstract classes
class Pressure(ABC):
    name: str

    @abstractmethod
    def calc(self, elmt) -> float:
        pass


class Location(ABC):
    _pressures: List[Pressure]

    def calc_pressures(self, elmt):
        return {pressure.name: pressure.calc(elmt=elmt) for pressure in self._pressures}


# Pressures
class Sea(Pressure):
    """C3.5.5.1 Sea pressure on bottom and side shell"""

    name = "sea"

    def calc(self, elmt) -> float:
        return self._pressure(elmt)

    def _pressure(self, elmt):
        """C3.5.5.1"""
        return _pressure_sea_f(
            z_baseline=elmt.z_baseline,
            draft=elmt.vessel.draft,
            p_sea_min=self._preassure_sea_min(elmt),
            factor_S=self._factor_S(elmt),
        )

    def _factor_S_fwd(self, elmt):
        """Table C3.5.2"""
        return _factor_S_fwd_f(
            vert_acg=self.elmt.vessel.draft,
            length=self.elmt.vessel.length,
            block_coef=self.elmt.vessel.block_coef,
            draft=self.elmt.vessel.draft,
        )

    def _factor_S_aft(self, elmt):
        """Table C3.5.2"""
        return _factor_S_aft_f(
            vert_acg=elmt.vessel.vert_acg,
            length=elmt.vessel.length,
            draft=elmt.vessel.draft,
        )

    def _factor_S(self, elmt):
        """Table C3.5.2"""
        return _factor_S_f(
            factor_S_aft=self._factor_S_aft(elmt),
            factor_S_fwd=self._factor_S_fwd(elmt),
            x_pos=elmt.x_pos,
        )

    def _preassure_sea_min_fwd(self, elmt):
        return _preassure_sea_min_fwd_f(length=elmt.vessel.length)

    def _preassure_sea_min_aft(self, elmt):
        return _preassure_sea_min_aft_f(elmt.vessel.length)

    def _preassure_sea_min(self, elmt):
        return _preassure_sea_min_f(
            preassure_sea_min_aft=self._preassure_sea_min_aft(elmt),
            preassure_sea_min_fwd=self._preassure_sea_min_fwd(elmt),
            x_pos=elmt.x_pos,
        )


class Impact(Pressure):
    """C3.5.3 Impact pressure on the bottom hull parameters and calculation."""

    name = "impact"

    # Table C3.5.1
    _min_acg_froude_limit_inf = 4.5
    _min_acg_froude_limit_sup = 5
    _max_acg_froude_limit = 5

    def calc(self, elmt):
        return self._pressure_impact(elmt)

    def _x_lim(self, elmt):
        return _x_lim_f(
            vert_acg=elmt.vessel.vert_acg,
            x_lim_Froude_n_min=self._x_lim_sp_len_ratio_min(elmt),
            x_lim_Froude_n_max=self._x_lim_sp_len_ratio_max(elmt),
        )

    def _x_lim_sp_len_ratio_min(self, elmt):
        return _x_lim_sp_len_ratio_min_f(
            sp_len_ratio=elmt.vessel.sp_len_ratio,
            min_acg_froude_limit_inf=self._min_acg_froude_limit_inf,
            min_acg_froude_limit_sup=self._min_acg_froude_limit_sup,
            x_lim_min_acg_inf=self._x_lim_min_acg_inf,
            x_lim_min_acg_sup=self._x_lim_min_acg_sup,
        )

    def _x_lim_sp_len_ratio_max(self, elmt):
        return _x_lim_sp_len_ratio_max_f(
            sp_len_ratio=elmt.vessel.sp_len_ratio,
            max_acg_froude_limit_inf=self._min_acg_froude_limit_inf,
            max_acg_froude_limit=self._max_acg_froude_limit,
            x_lim_max_acg_inf=self._x_lim_min_acg_inf,
            x_lim_max_acg=self._x_lim_max_acg,
        )

    def _ref_area(self, elmt):
        return _ref_area_f(
            displacement=elmt.vessel.displacement, draft=elmt.vessel.draf
        )

    # def _area(self, elmt):
    #     return _area_f(span=elmt.model.span, spacing=elmt.model.spancing)

    def _coef_k3(self, elmt):
        return _coef_k3_f(
            deadrise_eff=_effective_deadrise(elmt.location.deadrise),
            deadrise_lcg_eff=_effective_deadrise(elmt.vessel.deadrise_lcg_eff),
        )

    def _param_u(self, elmt):
        return _param_u_f(area=self.elmt.model.area, ref_area=self._ref_area(elmt))

    def _coef_k2(self, elmt):
        return _coef_k2_f(self._param_u(elmt))

    def _pressure_impact(self, elmt):
        return _pressure_impact_f(
            x_pos=elmt.x_pos,
            x_lim=self._x_lim(elmt),
            pressure_impact_pre=self._pressure_impact_pre(elmt),
            pressure_sea=self.elmt.pressures["sea"],
        )

    @abstractmethod
    def _pressure_impact_pre(self, elmt):
        pass


class ImpactBottom(Impact):
    """C3.5.3 Impact pressure on the bottom of hull"""

    _x_lim_min_acg_inf = 0.7
    _x_lim_min_acg_sup = 0.5
    _x_lim_max_acg = 0.5

    def _coef_k1(self, elmt):
        return _coef_k1_f(x_pos=elmt.x_pos)

    def _pressure_impact_pre(self, elmt):
        return _pressure_impact_bottom_pre_f(
            draft=elmt.vessel.draf,
            vert_acg=elmt.vessel.vert_acg,
            coef_k1=self._coef_k1(elmt),
            coef_k2=self._coef_k2(elmt),
            coef_k3=self._coef_k3(elmt),
        )


class ImpactWetDeck(Impact):
    """C3.5.4 Impact pressure on wet deck"""

    _x_lim_min_acg_inf = 0.8
    _x_lim_min_acg_sup = 0.7
    _x_lim_max_acg = 0.7

    def _coef_kwd(self, elmt):
        return _coef_kwd_f(x_pos=elmt.x_pos)

    def _rel_impact_vel(self, elmt):
        return _rel_impact_vel_f(
            sig_wave_height=elmt.vessel.sig_wave_height, length=elmt.vessel.length
        )

    def _pressure_impact_pre(self, elmt):
        return _pressure_impact_wet_deck_pre_f(
            speed=elmt.vessel.speed,
            sig_wave_height=elmt.vessel.sig_wave_height,
            air_gap=self.elmt.location.air_gap,
            coef_k2=self._coef_k2(elmt),
            coef_k3=self._coef_k3(elmt),
            coef_kwd=self._coef_kwd(elmt),
            rel_impact_vel=self._rel_impact_vel(elmt),
        )


class DeckPressure(Pressure):
    """C3.5.8.2 Weather decks and exposed areas."""

    name = "deck"

    def calc(self, elmt):
        return self._pressure_deck(elmt)

    def _pressure_deck(self, elmt):
        return _pressure_deck_f(z_waterline=self.elmt.z_waterline)


class DeckHouse(Pressure):
    """C3.5.5.5 Sea pressures on deckhouses."""

    def calc(self, elmt):
        return self._pressure_walls(elmt)

    def _x1(self, elmt):
        return _x1_f(midship=elmt.vessel.midship, elmt=elmt.x_pos, elmt=elmt.x)

    def _coef_ksu(self, elmt):
        return _coef_ksu_f(
            beam=elmt.vessel.beam, deckhouse_breadth=elmt.location.deckhouse_breadth
        )

    def _pressure_walls(self, elmt):
        return _pressure_walls_f(
            length=elmt.vessel.lenght,
            block_coef=elmt.vessel.block_coef,
            z_waterline=elmt.z_waterline,
            coef_ksu=self._coef_ksu(elmt),
            x1=self._x1(elmt),
            pressure_walls_min=self._pressure_walls_min(elmt),
        )

    @abstractmethod
    def _pressure_walls_min(self, elmt):
        pass


class DeckHouseMainFront(DeckHouse):
    name = "deck_house_main_front"

    def _pressure_walls_min(self, elmt):
        return _pressure_walls_min_f(length=elmt.vessel.lenght)


class DeckHouseMainSide(DeckHouse):
    name = "deck_house_main_side"

    def _pressure_walls_min(self, elmt):
        return 4


class DeckHouseOther(DeckHouse):
    name = "deck_house_other"

    def _pressure_walls_min(self, elmt):
        return 3


# Location
@dataclass
class Bottom(Location):
    deadrise: float

    _pressures = [Sea(), ImpactBottom()]


@dataclass
class Side(Location):
    _pressures = [Sea()]


@dataclass
class Deck(Location):
    _pressures = [DeckPressure()]


@dataclass
class WetDeck(Location):
    deadrise: float
    air_gap: float

    _pressures = [Sea(), ImpactWetDeck()]


@dataclass
class DeckHouseMainFront(Location):
    deckhouse_breadth: float

    _pressures = [DeckHouseMainFront()]


@dataclass
class DeckHouseMainSide(Location):
    deckhouse_breadth: float

    _pressures = [DeckHouseMainSide()]


@dataclass
class DeckHouseOther(Location):
    deckhouse_breadth: float

    _pressures = [DeckHouseOther()]
