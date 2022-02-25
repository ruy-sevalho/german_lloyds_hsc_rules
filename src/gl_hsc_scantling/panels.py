# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 12:28:58 2021

@author: ruy
"""
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import pandas as pd
from quantities import Quantity
from dataclass_tools.tools import DESERIALIZER_OPTIONS, DeSerializerOptions

from gl_hsc_scantling.utils import Criteria

from .common_field_options import (
    BOUND_COND_OPTIONS,
    CHINE_ANGLE_OPTIONS,
    CHINE_OPTIONS,
    CURVATURE_X_OPTIONS,
    CURVATURE_Y_OPTIONS,
    DIM_X_OPTIONS,
    DIM_Y_OPTIONS,
    LAMINATE_OPTIONS,
)
from .composites import Laminate
from .structural_model import BoundaryCondition
from .vessel import Vessel

# TODO refactor panel_coef methods. Use dataclasses instead of primitive dicts
@dataclass
class Panel:

    dim_x: float = field(metadata={DESERIALIZER_OPTIONS: DIM_X_OPTIONS})
    dim_y: float = field(metadata={DESERIALIZER_OPTIONS: DIM_Y_OPTIONS})
    laminate: Laminate = field(metadata={DESERIALIZER_OPTIONS: LAMINATE_OPTIONS})
    curvature_x: float = field(
        default=0, metadata={DESERIALIZER_OPTIONS: CURVATURE_X_OPTIONS}
    )
    curvature_y: float = field(
        metadata={DESERIALIZER_OPTIONS: CURVATURE_Y_OPTIONS}, default=0
    )
    bound_cond: BoundaryCondition = field(
        metadata={DESERIALIZER_OPTIONS: BOUND_COND_OPTIONS},
        default=BoundaryCondition.FIXED,
    )
    chine: bool = field(metadata={DESERIALIZER_OPTIONS: CHINE_OPTIONS}, default=False)
    chine_angle: float = field(
        metadata={DESERIALIZER_OPTIONS: CHINE_ANGLE_OPTIONS}, default=0
    )

    direction_table = {"x": 0, "y": 1}

    @property
    def geo_asp_r(self):
        """C3.8.3.2.4"""

        return self.dim_x / self.dim_y

    @property
    def corr_asp_r_canditate(self):
        return (
            self.geo_asp_r
            * (self.laminate.bend_stiff[1] / self.laminate.bend_stiff[0]) ** 0.25
        )

    @property
    def span_direction(self):
        if self.corr_asp_r < 1:
            return "x"
        return "y"

    @property
    def corr_asp_r(self):
        if self.corr_asp_r_canditate < 1:
            return 1 / self.corr_asp_r_canditate
        return self.corr_asp_r_canditate

    @property
    def span(self):
        table_dim = {"x": self.dim_x, "y": self.dim_y}
        table_chine = {False: 1, True: self.chine_corr_factor}
        return table_dim[self.span_direction] * table_chine[self.chine]

    @property
    def spacing(self):
        table = {"x": self.dim_y, "y": self.dim_x}
        return table[self.span_direction]

    # Be careful with span and spacing definitions of panels and stiffeneres,
    # they are usually switched
    @property
    def area(self):
        return np.min([self.span * self.spacing, 3 * self.span**2])

    @property
    def curvature(self):
        table = {"x": self.curvature_x, "y": self.curvature_y}
        return table[self.span_direction]

    # From table C3.8.2
    @property
    def coef_table(self):
        """Table C3.8.2"""

        fixed = {
            "ar": [1, 1.2, 1.4, 1.6, 1.8, 2, 5],
            "beta": [0.3078, 0.3834, 0.4356, 0.468, 0.4872, 0.4974, 0.5],
            "alpha": [0.0138, 0.0188, 0.0226, 0.0251, 0.0267, 0.0277, 0.0284],
            "gamma": [0.42, 0.455, 0.478, 0.491, 0.499, 0.503, 0.5],
        }
        simp_sup = {
            "ar": [1, 1.2, 1.4, 1.6, 1.8, 2, 3, 4, 5, 100],
            "beta": [
                0.2874,
                0.3762,
                0.453,
                0.5172,
                0.5688,
                0.6102,
                0.7134,
                0.741,
                0.7476,
                0.75,
            ],
            "alpha": [
                0.0444,
                0.0616,
                0.077,
                0.0906,
                0.1017,
                0.111,
                0.1335,
                0.14,
                0.1417,
                0.1421,
            ],
            "gamma": [
                0.42,
                0.455,
                0.478,
                0.491,
                0.499,
                0.503,
                0.505,
                0.502,
                0.501,
                0.5,
            ],
        }
        table = {
            BoundaryCondition.FIXED: fixed,
            BoundaryCondition.SIMPLY_SUPPORTED: simp_sup,
        }
        return table[self.bound_cond]

    def _panel_coef(self, coef_type):
        return np.interp(
            self.corr_asp_r, self.coef_table["ar"], self.coef_table[coef_type]
        )

    @property
    def beta(self):
        return self._panel_coef("beta")

    @property
    def gamma(self):
        return self._panel_coef("gamma")

    @property
    def alpha(self):
        return self._panel_coef("alpha")

    @property
    def curve_correction(self):
        """C3.8.3.2.7"""
        ratio = np.min([0.1, np.max([0.03, self.curvature / self.span])])
        return 1.15 - 5 * ratio

    def max_bend_moment(self, pressure: float):
        """C3.8.3.3.1"""

        return self.beta * pressure * self.span**2 * self.curve_correction / 6

    def max_shear_force(self, pressure: float):
        """C3.8.3.3.2"""

        return self.gamma * pressure * self.span

    def max_lateral_deflection(self, pressure: float):
        """C3.8.3.3.3"""

        return (
            self.alpha
            * pressure
            * self.span**4
            / (12 * self.laminate.bend_stiff[self.direction_table[self.span_direction]])
        )

    @property
    def limit_deflection(self):
        """C3.8.3.3.3"""

        table = {
            "SingleSkinLaminate": 0.015 * self.span,
            "SandwichLaminate": 0.01 * self.span,
        }
        return table[type(self.laminate).__name__]

    def load_array(self, pressure: float):
        table = {"x": 3, "y": 4}
        zeros = np.zeros(6)
        zeros[table[self.span_direction]] = self.max_bend_moment(pressure)
        return zeros

    def plies_responses(self, pressure: float):
        return self.laminate.response_plies(self.load_array(pressure))

    @property
    def chine_corr_factor(self):
        xp = [50, 100, 110, 120, 130, 140, 150, 160, 170]
        fp = [1, 1.005, 1.01, 1.02, 1.037, 1.061, 1.108, 1.23, 1.545]
        return np.interp(self.chine_angle, xp, fp)

    def rule_check(self, pressure):
        laminate_check = self.laminate.panel_rule_check(self, pressure=pressure)
        deflection_check = pd.DataFrame(
            {
                "deflection": [
                    Criteria(
                        self.max_lateral_deflection(pressure=pressure),
                        self.limit_deflection,
                        1,
                    )
                ]
            }
        )
        return pd.concat([deflection_check, laminate_check], axis=1)
