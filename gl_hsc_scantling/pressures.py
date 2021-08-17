# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 12:19:42 2021

@author: ruy
"""
from functools import cached_property
from enum import Enum

import numpy as np
from marshmallow_dataclass import dataclass

from .vessel import Vessel


def _pressure_sea_f(z_baseline, draft, preassure_sea_min, factor_S):
    if z_baseline <= draft:
        return np.max(
                [
                    preassure_sea_min,
                    (
                        10
                        * (
                            draft
                            + 0.75 * factor_S
                            - (1 - 0.25 * factor_S / .draft)
                            * z_baseline
                        )
                    ),
                ]
            )
    else:
        return np.max(
                [
                    preassure_sea_min,
                    (10 * (draft +_factor_S - z_baseline)),
                ]

class Pressures:
    def __init__(self, vessel: Vessel, elmt):
        self.vessel = vessel
        self.elmt = elmt


class Sea(Pressures):
    """C3.5.5.1 Sea pressure on bottom and side shell"""

    @property
    def _pressure_sea(self):
        """C3.5.5.1"""
        if self.elmt.z_baseline <= self.vessel.draft:
            return np.max(
                [
                    self._preassure_sea_min,
                    (
                        10
                        * (
                            self.vessel.draft
                            + 0.75 * self._factor_S
                            - (1 - 0.25 * self._factor_S / self.vessel.draft)
                            * self.elmt.z_baseline
                        )
                    ),
                ]
            )
        else:
            return np.max(
                [
                    self._preassure_sea_min,
                    (10 * (self.vessel.draft + self._factor_S - self.elmt.z_baseline)),
                ]
            )

    @property
    def _factor_S_fwd(self):
        """Table C3.5.2"""
        return np.max(
            [
                np.min(
                    [
                        (
                            0.36
                            * self.vessel.vert_acg
                            * self.vessel.length ** 0.5
                            / np.min([self.vessel.block_coef, 0.5])
                        ),
                        3.5 * self.vessel.draft,
                    ]
                ),
                self.vessel.draft,
            ]
        )

    @property
    def _factor_S_aft(self):
        """Table C3.5.2"""
        return np.max(
            [
                np.min(
                    [
                        0.60 * self.vessel.vert_acg * self.vessel.length ** 0.5,
                        2.5 * self.vessel.draft,
                    ]
                ),
                self.vessel.draft,
            ]
        )

    @property
    def _factor_S(self):
        """Table C3.5.2"""
        xp = [0, 0.5, 0.9, 1]
        fp = [
            self._factor_S_aft,
            self._factor_S_aft,
            self._factor_S_fwd,
            self._factor_S_fwd,
        ]
        return np.interp(self.elmt.x_pos, xp, fp)

    @property
    def _preassure_sea_min_fwd(self):
        return np.max([20, np.min([(self.vessel.length + 75) / 5, 35])])

    @property
    def _preassure_sea_min_aft(self):
        return np.max([10, np.min([(self.vessel.length + 75) / 10, 20])])

    @property
    def _preassure_sea_min(self):
        xp = [0, 0.5, 0.9, 1]
        fp = [
            self._preassure_sea_min_aft,
            self._preassure_sea_min_aft,
            self._preassure_sea_min_fwd,
            self._preassure_sea_min_fwd,
        ]
        return np.interp(self.elmt.x_pos, xp, fp)


class Impact(Pressures):
    """C3.5.3 Impact pressure on the bottom hull parameters and calculation."""

    """Table C3.5.1"""

    @property
    def _min_acg_froude_limit_inf(self):
        return 4.5

    @property
    def _min_acg_froude_limit_sup(self):
        return 5

    @property
    def _x_lim(self):
        if self.vessel.vert_acg <= 1:
            return self._x_lim_Froude_n_min
        elif self.vessel.vert_acg <= 1.5:
            return self._x_lim_Froude_n_max
        else:
            return 0

    @property
    def _max_acg_froude_limit(self):
        return 5

    @property
    def _x_lim_Froude_n_min(self):
        if self.vessel.froude_n < self._min_acg_froude_limit_inf:
            return self._x_lim_min_acg_inf
        elif self.vessel.froude_n <= self._min_acg_froude_limit_sup:
            return self._x_lim_min_acg_sup
        else:
            return 0

    @property
    def _x_lim_Froude_n_max(self):
        if self.vessel.froude_n < self._max_acg_froude_limit_inf:
            return self._x_lim_max_acg_inf
        elif self.vessel.froude_n <= self._max_acg_froude_limit:
            return self._x_lim_max_acg
        else:
            return 0

    """Table C3.5.1"""

    @property
    def _ref_area(self):
        return 0.7 * (self.vessel.displacement / 2) / self.vessel.draft

    @property
    def _area(self):
        return self.elmt.span * self.elmt.spacing

    @property
    def _coef_k3(self):
        return (70 - self.elmt._deadrise_eff) / (70 - self.vessel.deadrise_lcg_eff)

    @property
    def _param_u(self):
        return 100 * self._area / self._ref_area

    @property
    def _coef_k2(self):
        return 0.455 - 0.35 * (
            (self._param_u ** 0.75 - 1.7) / (self._param_u ** 0.75 + 1.7)
        )

    @property
    def _pressure_impact(self):
        if self.elmt.x_pos > self._x_lim:
            return self._pressure_impact_
        elif self.elmt.x_pos > self._x_lim - 0.1:
            xp = [0, 0.1]
            fp = [self._pressure_impact_, self._pressure_sea]
            return np.interp(self.elmt.x_pos - self._x_lim, xp, fp)
        else:
            return 0


class ImpactBottom(Impact):
    """Table C3.5.1."""

    @property
    def _x_lim_min_acg_inf(self):
        return 0.7

    @property
    def _x_lim_min_acg_sup(self):
        return 0.5

    @property
    def _x_lim_max_acg(self):
        return 0.5

    """Table C3.5.1"""

    @property
    def _coef_k1(self):
        xp = [0, 0.5, 0.8, 1]
        fp = [0.5, 1, 1, 0.5]
        return np.interp(self.elmt.x_pos, xp, fp)

    @property
    def _pressure_impact_(self):
        return (
            100
            * self.vessel.draft
            * self._coef_k1
            * self._coef_k2
            * self._coef_k3
            * self.vessel.vert_acg
        )


class ImpactWetDeck(Impact):
    """Table C3.5.1"""

    @property
    def _x_lim_min_acg_inf(self):
        return 0.8

    @property
    def _x_lim_min_acg_sup(self):
        return 0.7

    @property
    def _x_lim_max_acg(self):
        return 0.7

    """Table C3.5.1"""

    """C3.5.4 Impact pressure on wet deck"""

    @property
    def _coef_kwd(self):
        xp = [0, 0.2, 0.7, 0.8, 1]
        fp = [0.5, 0.4, 0.4, 1, 1]
        return np.interp(self.elmt.x_pos, xp, fp)

    @property
    def _rel_impact_vel(self):
        return 4 * self.vessel.sig_wave_height / self.vessel.length ** 0.5 + 1

    def _pressure_impact_(self):
        return (
            3
            * self._coef_k2
            * self._coef_k3
            * self._coef_kwd
            * self.vessel.speed
            * self._rel_impact_vel
            * (1 - 0.85 * self.elmt.air_gap / self.vessel.sig_wave_height)
        )


class Bottom(Sea, ImpactBottom):
    @property
    def pressures(self):
        return {
            "sea": self._pressure_sea,
            "impact": self._pressure_impact,
        }


class Side(Sea):
    @property
    def pressures(self):
        return {
            "sea": self._pressure_sea,
        }


class WetDeck(Sea, ImpactWetDeck):
    @property
    def pressures(self):
        return {
            "sea": self._pressure_sea,
            "impact": self._pressure_impact,
        }


class Deck(Pressures):
    """C3.5.8.2 Weather decks and exposed areas."""

    def _pressure_deck(self):
        xp = [0, 2, 3, 4]
        fp = [6, 6, 3, 3]
        return np.interp(self.elmt.z_waterline, xp, fp)

    @property
    def pressures(self):
        return {"deck": self._pressure_deck}


class DeckHouse(Pressures):
    """C3.5.5.5 Sea pressures on deckhouses."""

    @property
    def _x1(self):
        if self.elmt.x_pos > self.vessel.midship:
            return np.abs(self.elmt.x - self.vessel.midship)
        else:
            return 0

    @property
    def _coef_ksu(self):
        return np.max(
            [3, np.min([5, 1.5 + 3.5 * self.elmt.deckhouse_breadth / self.vessel.beam])]
        )

    def _pressure_walls(self):
        return np.max(
            [
                (
                    self._coef_ksu
                    * (
                        1
                        + self._x1
                        / (2 * self.vessel.length * (self.vessel.block_coef + 0.1))
                    )
                    * (1 + 0.045 * self.vessel.length - 0.38 * self.elmt.z_waterline)
                ),
                self._pressure_walls_min,
            ]
        )


class DeckHouseMainFront(DeckHouse):
    @property
    def _pressure_walls_min(self):
        return 6.5 + 0.06 * self.vessel.length


class DeckHouseMainSide(DeckHouse):
    @property
    def _pressure_walls_min(self):
        return 4


class DeckHouseOther(DeckHouse):
    @property
    def _pressure_walls_min(self):
        return 3
