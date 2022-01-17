# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 09:38:12 2021

@author: ruy
"""
from abc import ABC
from dataclasses import asdict, field
from enum import Enum

import numpy as np
from marshmallow import Schema, fields
from pylatex import NoEscape, Quantity

from .constants import GRAVITY
from .dc import dataclass
from .report import (
    Data,
    NamePrint,
    _data_to_dict,
    _input_data_dict,
    _print_wrapper_builder,
)

# from typing import dict


# metadata = {
#     "speed": NamePrint("Speed", "S", "kt"),
#     "vert_acg": NamePrint(
#         "Vertical acceleration", NoEscape(r"a\textsubscript{CG}"), "g"
#     ),
#     "transverse_bending_moment": NamePrint(
#         "Transverse bending moment", NoEscape(r"M\textsubscript{bt}"), " kN"
#     ),
#     "transverse_torsional_moment": NamePrint(
#         "Transverse torsional moment", NoEscape(r"M\textsubscript{tt}"), " kN"
#     ),
#     "shear_force": NamePrint("Shear force", NoEscape(r"T\textsubscript{bt}"), "kN"),
#     "length": NamePrint("Length", "L", " m"),
#     "displacement": NamePrint("Displacement", NoEscape(r"$\Delta$"), " t"),
#     "beam": NamePrint("Beam", "B", " m"),
#     "draft": NamePrint("Draft", "H", " m"),
# }


class TypeOfService(str, Enum):
    """Vessels service type in accordance to GL HSC 2012 rules."""

    PASSENGER = "PASSENGER"
    FERRY = "FERRY"
    CARGO = "CARGO"
    SUPPLY = "SUPPLY"
    PILOT = "PILOT"
    RESCUE = "RESCUE"


class ServiceRange(str, Enum):
    """
    Vessels service range in accordance to GL HSC 2012 rules.
    USR - Unrestricted service range
    RSA_200 - 200 nm range
    RSA_50 - 50 nm range
    RSA_20 - 20 nm range
    RSA_SW - sheltered waters
    """

    USR = "USR"
    RSA_200 = "RSA (200)"
    RSA_50 = "RSA (50)"
    RSA_20 = "RSA (20)"
    RSA_SW = "RSA (SW)"


# vert_acg: float = field(
#         metadata={
#             'long': "Vertical acceleration",
#             'abbr': NoEscape(r"a\textsubscript{CG}"),
#             'unit': 'g',
#             'round_precision': 2,
#         }
#     )


# @dataclass
# class VesselLoads:
#     vert_acg: float = field(
#         metadata={
#             # 'long': "Vertical acceleration",
#             # 'abbr': NoEscape(r"a\textsubscript{CG}"),
#             "unit": "g",
#             # 'round_precision': 2,
#         }
#     )
#     shear_force: float = field(
#         metadata={
#             "long": "Shear force",
#             "abbr": NoEscape(r"T\textsubscript{bt}"),
#             "unit": "kN",
#             "round_precision": 2,
#         }
#     )
#     transverse_bending_moment: float = field(
#         metadata={
#             "long": "Transverse bending moment",
#             "abbr": NoEscape(r"T\textsubscript{bt}"),
#             "unit": "kN",
#             "round_precision": 2,
#         }
#     )
#     transverse_torsional_moment: float = field(
#         metadata={
#             "long": "Transverse torsional moment",
#             "abbr": NoEscape(r"M\textsubscript{tt}"),
#             "unit": "kN",
#             "round_precision": 2,
#         }
#     )

#     # def __post_init__(self):


@dataclass
class Vessel(Data):
    """Vessel for the 2012 German Lloyds High Speed Craft
    scantling rules.
    """

    name: str
    speed: float
    displacement: float
    length: float
    beam: float
    fwd_perp: float
    aft_perp: float
    draft: float
    z_baseline: float
    block_coef: float
    water_plane_area: float
    lcg: float
    deadrise_lcg: float
    dist_hull_cl: float
    type_of_service: TypeOfService = TypeOfService.PASSENGER
    service_range: ServiceRange = ServiceRange.USR

    # Table C3.3.1
    @property
    def serv_type_coef(self):
        table = {
            TypeOfService.PASSENGER: 0.24,
            TypeOfService.FERRY: 0.24,
            TypeOfService.CARGO: 0.24,
            TypeOfService.SUPPLY: 0.36,
            TypeOfService.PILOT: 0.5,
            TypeOfService.RESCUE: 0.6,
        }
        return table[self.type_of_service]

    # Table C3.3.1
    @property
    def serv_range_coef(self):
        table = {
            ServiceRange.USR: 1,
            ServiceRange.RSA_200: 0.9,
            ServiceRange.RSA_50: 0.75,
            ServiceRange.RSA_20: 0.66,
            ServiceRange.RSA_SW: 0.6,
        }
        return table[self.service_range]

    @property
    def z_waterline(self):
        return self.z_baseline + self.draft

    @property
    def midship(self):
        return (self.fwd_perp + self.aft_perp) / 2

    @property
    def x_pos_cg(self):
        return (self.lcg - self.aft_perp) / (self.fwd_perp - self.aft_perp)

    @property
    def sp_len_ratio(self):
        return self.speed / self.length ** 0.5

    # C3.3.1
    @property
    def vert_acg(self):
        """Vertical acceletation at LCGm, output in g (9.81 m/s2)"""
        acg = self.serv_type_coef * self.serv_range_coef * self.sp_len_ratio
        if self.type_of_service == TypeOfService.PASSENGER:
            return min([1, acg])
        return acg

    # C3.4.2.3
    @property
    def transverse_bending_moment(self):
        """Transverse bending moment in kN*m."""
        return self.displacement * self.dist_hull_cl * self.vert_acg * GRAVITY / 5

    # C3.4.2.3
    @property
    def transverse_shear_force(self):
        """Transverse shear force in kN."""
        return self.displacement * self.vert_acg * GRAVITY / 4

    # C3.4.2.4
    @property
    def transverse_torsional_moment(self):
        """Transverse torsional moment in kN*m."""
        return 0.125 * self.displacement * self.length * self.vert_acg * GRAVITY

    @property
    def loads_names(self):
        return [
            "vert_acg",
            "shear_force",
            "transverse_bending_moment",
            "transverse_torsional_moment",
        ]

    @property
    def loads_asdict(self):
        return _data_to_dict(self, self.loads_names)

    @property
    def max_wave_height(self):
        """C3.3.3 Assessment of limit operating conditions"""
        return (
            5
            * np.max([self.vert_acg, 1])
            / self.speed
            * self.length ** 1.5
            / (6 + 0.14 * self.length)
        )

    @property
    def sig_wave_height(self):
        """C3.3.3.2 Limitation imposed by vertical acceleration at LCG"""
        return 10.9 * self.vert_acg * self.coef_kcat * self.coef_kh / self.coef_kf ** 2

    # C3.3.3.2
    @property
    def coef_kcat(self):
        return np.max([1 + (self.dist_hull_cl - self.max_wave_height) / self.length, 1])

    # C3.3.3.2
    @property
    def coef_kf(self):
        return 3.23 / self.length * (2.43 * self.length ** 0.5 + self.speed)

    # C3.3.3.2
    @property
    def coef_kt(self):
        return (
            4.6 * self.water_plane_area / self.displacement * (self.x_pos_cg) ** 0.5
        ) ** 0.5

    # C3.3.3.2
    @property
    def coef_k(self):
        return self.coef_kf / self.coef_kt

    # C3.3.3.2
    @property
    def coef_kh(self):
        return self.coef_k ** 0.35 * ((1 / self.coef_k ** 2 - 0.11) ** 2 + 1) ** 0.5
