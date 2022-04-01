# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 09:38:12 2021

@author: ruy
"""
from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property as property
import numpy as np
from dataclass_tools.tools import (
    DESERIALIZER_OPTIONS,
    DeSerializerOptions,
    NamePrint,
    PrintMetadata,
    serialize_dataclass,
)

from pylatex import NoEscape, Quantity

from .abrevitation_registry import abv_registry
from .common_field_options import NAME_OPTIONS
from .constants import GRAVITY


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


SPEED_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(long_name="Speed", abreviation="S", units="kt")
)
abv_registry.append(SPEED_OPTIONS)
DISPLACEMENT_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Displacement", abreviation=NoEscape(r"$\Delta$"), units="t"
    )
)
abv_registry.append(DISPLACEMENT_OPTIONS)
LENGTH_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(long_name="Length", abreviation="L", units="m")
)
abv_registry.append(LENGTH_OPTIONS)
BEAM_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(long_name="Beam", abreviation="B", units="m")
)
abv_registry.append(BEAM_OPTIONS)
FWD_PERP_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Foward Perpendicular",
        abreviation=NoEscape(r"F\textsubscript{P}"),
        units="m",
    )
)
abv_registry.append(FWD_PERP_OPTIONS)
AFT_PERP_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Aft Perpendicular",
        abreviation=NoEscape(r"A\textsubscript{P}"),
        units="m",
    )
)
abv_registry.append(AFT_PERP_OPTIONS)
DRAFT_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Draft",
        abreviation="H",
        units="m",
    )
)
abv_registry.append(DRAFT_OPTIONS)
Z_BASELINE_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Z from base line",
        abreviation=NoEscape(r"z\textsubscript{BL}"),
        units="m",
    )
)
abv_registry.append(Z_BASELINE_OPTIONS)
BLOCK_COEF_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Block coefficient",
        abreviation=NoEscape(r"C\textsubscript{B}"),
        units="",
    )
)
abv_registry.append(BLOCK_COEF_OPTIONS)
WATER_PLANE_AREA_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Water plane area",
        abreviation=NoEscape(r"WP\textsubscript{A}"),
        units="m**2",
    )
)
abv_registry.append(WATER_PLANE_AREA_OPTIONS)
LCG_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Longitudinal center of gravity",
        abreviation=NoEscape(r"L\textsubscript{cg}"),
        units="m",
    )
)
abv_registry.append(LCG_OPTIONS)
DEADRISE_LCG_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Deadrise at longitudinal center of gravity",
        abreviation=NoEscape(r"$\alpha$\textsubscript{d}"),
        units="degree",
    )
)
abv_registry.append(DEADRISE_LCG_OPTIONS)
DIST_HULL_CL_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Distance between hulls centerline",
        abreviation=NoEscape(r"B\textsubscript{CL}"),
        units="m",
    )
)
abv_registry.append(DIST_HULL_CL_OPTIONS)
TYPE_OF_SERVICE_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Type of service",
        abreviation="ToS",
    )
)
abv_registry.append(TYPE_OF_SERVICE_OPTIONS)
SERVICE_RANGE_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Service range",
        abreviation="SR",
    )
)
abv_registry.append(SERVICE_RANGE_OPTIONS)
VERT_ACG_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Center of gravity's vertical acceleration",
        abreviation=NoEscape(r"a\textsubscript{CG}"),
        units="g",
    )
)
abv_registry.append(VERT_ACG_OPTIONS)
SHEAR_FORCE_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Transverse shear force",
        abreviation=NoEscape(r"T\textsubscript{bt}"),
        units="kN",
    )
)
abv_registry.append(SHEAR_FORCE_OPTIONS)
TRANSVERSE_BENDING_MOMENT_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Transverse bending moment",
        abreviation=NoEscape(r"M\textsubscript{bt}"),
        units="kN*m",
    )
)
abv_registry.append(TRANSVERSE_BENDING_MOMENT_OPTIONS)
TRANSVERSE_TORSIONAL_MOMENT_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Transverse torsional moment",
        abreviation=NoEscape(r"M\textsubscript{tt}"),
        units="kN*m",
    )
)
abv_registry.append(TRANSVERSE_TORSIONAL_MOMENT_OPTIONS)


@dataclass
class VesselLoads:
    vert_acg: float = field(metadata={DESERIALIZER_OPTIONS: VERT_ACG_OPTIONS})
    shear_force: float = field(metadata={DESERIALIZER_OPTIONS: SHEAR_FORCE_OPTIONS})
    trans_bend_moment: float = field(
        metadata={DESERIALIZER_OPTIONS: TRANSVERSE_BENDING_MOMENT_OPTIONS}
    )
    trans_tors_moment: float = field(
        metadata={DESERIALIZER_OPTIONS: TRANSVERSE_TORSIONAL_MOMENT_OPTIONS}
    )


@dataclass
class Monohull:
    """Vessel for the 2012 German Lloyds High Speed Craft
    scantling rules.
    """

    name: str = field(metadata={DESERIALIZER_OPTIONS: NAME_OPTIONS})
    speed: float = field(metadata={DESERIALIZER_OPTIONS: SPEED_OPTIONS})
    displacement: float = field(metadata={DESERIALIZER_OPTIONS: DISPLACEMENT_OPTIONS})
    length: float = field(metadata={DESERIALIZER_OPTIONS: LENGTH_OPTIONS})
    beam: float = field(metadata={DESERIALIZER_OPTIONS: BEAM_OPTIONS})
    fwd_perp: float = field(metadata={DESERIALIZER_OPTIONS: FWD_PERP_OPTIONS})
    aft_perp: float = field(metadata={DESERIALIZER_OPTIONS: AFT_PERP_OPTIONS})
    draft: float = field(metadata={DESERIALIZER_OPTIONS: DRAFT_OPTIONS})
    z_baseline: float = field(metadata={DESERIALIZER_OPTIONS: Z_BASELINE_OPTIONS})
    block_coef: float = field(metadata={DESERIALIZER_OPTIONS: BLOCK_COEF_OPTIONS})
    water_plane_area: float = field(
        metadata={DESERIALIZER_OPTIONS: WATER_PLANE_AREA_OPTIONS}
    )
    lcg: float = field(metadata={DESERIALIZER_OPTIONS: LCG_OPTIONS})
    deadrise_lcg: float = field(metadata={DESERIALIZER_OPTIONS: DEADRISE_LCG_OPTIONS})

    type_of_service: TypeOfService = field(
        metadata={DESERIALIZER_OPTIONS: TYPE_OF_SERVICE_OPTIONS},
        default=TypeOfService.PASSENGER,
    )
    service_range: ServiceRange = field(
        metadata={DESERIALIZER_OPTIONS: SERVICE_RANGE_OPTIONS},
        default=ServiceRange.USR,
    )

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
            ServiceRange.USR: 1.0,
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
    def sp_len_ratio(self) -> float:
        return self.speed / self.length**0.5

    # C3.3.1
    @property
    def vert_acg(self):
        """Vertical acceletation at LCGm, output in g (9.81 m/s2)"""
        acg = self.serv_type_coef * self.serv_range_coef * self.sp_len_ratio
        if self.type_of_service == TypeOfService.PASSENGER:
            return min([1.0, acg])
        return acg

    @property
    def max_wave_height(self):
        """C3.3.3 Assessment of limit operating conditions"""
        return (
            5
            * np.max([self.vert_acg, 1])
            / self.speed
            * self.length**1.5
            / (6 + 0.14 * self.length)
        )

    @property
    def sig_wave_height(self):
        """C3.3.3.2 Limitation imposed by vertical acceleration at LCG"""
        return 10.9 * self.vert_acg * self.coef_kcat * self.coef_kh / self.coef_kf**2

    # C3.3.3.2
    @property
    def coef_kcat(self):
        return 1.0

    # C3.3.3.2
    @property
    def coef_kf(self):
        return 3.23 / self.length * (2.43 * self.length**0.5 + self.speed)

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
        return self.coef_k**0.35 * ((1 / self.coef_k**2 - 0.11) ** 2 + 1) ** 0.5


@dataclass
class Catamaran(Monohull):
    dist_hull_cl: float = field(
        metadata={DESERIALIZER_OPTIONS: DIST_HULL_CL_OPTIONS}, default=0
    )

    # C3.3.3.2
    @property
    def coef_kcat(self):
        return np.max(
            [1 + (self.dist_hull_cl - self.max_wave_height) / self.length, 1.0]
        )

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
        loads = VesselLoads(
            vert_acg=self.vert_acg,
            shear_force=self.transverse_shear_force,
            trans_bend_moment=self.transverse_bending_moment,
            trans_tors_moment=self.transverse_torsional_moment,
        )
        return serialize_dataclass(loads, printing_format=True, include_names=True)
