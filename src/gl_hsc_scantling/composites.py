# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 11:49:36 2020

@author: ruy
"""

from abc import ABC, abstractproperty
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from functools import cache
from re import T
from typing import Optional, Protocol, Tuple

import numpy as np
from dataclass_tools.tools import (
    DESERIALIZER_OPTIONS,
    DeSerializerOptions,
    PrintMetadata,
    serialize_dataclass,
)

from .common_field_options import (
    ANTI_SYMMETRIC_OPTIONS,
    CORE_MATERIAL_OPTIONS,
    CORE_THICKNESS_OPTIONS,
    CORE_TYPE_OPTIONS,
    DENSITY_OPTIONS,
    F_AREA_DENSITY_OPTIONS,
    F_MASS_CONT_OPTIONS,
    FIBER_OPTIONS,
    MATRIX_OPTIONS,
    MAX_STRAIN_X_OPTIONS,
    MAX_STRAIN_XY_OPTIONS,
    MODULUS_COMP_OPTIONS,
    MODULUS_SHEAR_OPTIONS,
    MODULUS_TENSION_OPTIONS,
    MODULUS_X_OPTIONS,
    MODULUS_XY_OPTIONS,
    MODULUS_Y_OPTIONS,
    MULTIPLE_OPTIONS,
    NAME_OPTIONS,
    POISSON_OPTIONS,
    POISSON_XY_OPTIONS,
    RESIN_ABSORPTION_OPTIONS,
    STRENGTH_COMP_OPTIONS,
    STRENGTH_SHEAR_OPTIONS,
    STRENGTH_TENSION_OPTIONS,
    SYMMETRIC_OPTIONS,
    THICKNESS_OPTIONS,
)
from .report import Criteria


def _matrix_inv(matrix) -> np.ndarray:
    @cache
    def _cached_inv(tup):
        return np.linalg.inv(tup)

    # Cast numpy array to tuple which is hashable so function can be cached
    matrix = tuple(map(tuple, matrix))
    return _cached_inv(matrix)


class FiberArregment(str, Enum):
    """Vessels service type in accordance to GL HSC 2012 rules."""

    CSM = "CSM"
    WOVEN = "WOVEN"


@dataclass
class Matrix:
    """Generic matrix - resins -  material"""

    name: str = field(metadata={DESERIALIZER_OPTIONS: NAME_OPTIONS})
    density: float = field(metadata={DESERIALIZER_OPTIONS: DENSITY_OPTIONS})
    modulus_x: float = field(metadata={DESERIALIZER_OPTIONS: MODULUS_X_OPTIONS})
    modulus_xy: float = field(metadata={DESERIALIZER_OPTIONS: MODULUS_XY_OPTIONS})
    poisson: float = field(metadata={DESERIALIZER_OPTIONS: POISSON_OPTIONS})


@dataclass
class Fiber:
    """Generic fiber material"""

    name: str = field(metadata={DESERIALIZER_OPTIONS: NAME_OPTIONS})
    density: float = field(metadata={DESERIALIZER_OPTIONS: DENSITY_OPTIONS})
    modulus_x: float = field(metadata={DESERIALIZER_OPTIONS: MODULUS_X_OPTIONS})
    modulus_y: float = field(metadata={DESERIALIZER_OPTIONS: MODULUS_Y_OPTIONS})
    modulus_xy: float = field(metadata={DESERIALIZER_OPTIONS: MODULUS_XY_OPTIONS})
    poisson: float = field(metadata={DESERIALIZER_OPTIONS: POISSON_OPTIONS})


class LaminaData(Protocol):
    """2D lamina material propeties."""

    name: str
    modulus_x: float
    modulus_y: float
    modulus_xy: float
    poisson_xy: float
    thickness: float
    f_mass_cont: float
    f_area_density: float
    max_strain_x: float
    max_strain_xy: float


@dataclass
class LaminaMonolith:
    """Single lamina externally defiened properties"""

    name: str = field(metadata={DESERIALIZER_OPTIONS: NAME_OPTIONS})
    modulus_x: float = field(metadata={DESERIALIZER_OPTIONS: MODULUS_X_OPTIONS})
    modulus_y: float = field(metadata={DESERIALIZER_OPTIONS: MODULUS_Y_OPTIONS})
    modulus_xy: float = field(metadata={DESERIALIZER_OPTIONS: MODULUS_XY_OPTIONS})
    poisson_xy: float = field(metadata={DESERIALIZER_OPTIONS: POISSON_XY_OPTIONS})
    thickness: float = field(metadata={DESERIALIZER_OPTIONS: THICKNESS_OPTIONS})
    f_mass_cont: float = field(metadata={DESERIALIZER_OPTIONS: F_MASS_CONT_OPTIONS})
    f_area_density: float = field(
        metadata={DESERIALIZER_OPTIONS: F_AREA_DENSITY_OPTIONS}
    )
    max_strain_x: float = field(metadata={DESERIALIZER_OPTIONS: MAX_STRAIN_X_OPTIONS})
    max_strain_xy: float = field(metadata={DESERIALIZER_OPTIONS: MAX_STRAIN_XY_OPTIONS})


class ClothType(str, Enum):
    WOVEN = "WOVEN"
    CSM = "CSM"


cloth_type_options = DeSerializerOptions(
    metadata=PrintMetadata(long_name="Cloth type", abreviation="cloth")
)


@dataclass
class LaminaParts:
    """Single lamina made of woven cloth or csm (chopped stranded mat) - prop caculated
    from fiber and  matrix, in accordance to C3.8.2 Elasto-mechanical properties
    of laminated structures.
    """

    name: str = field(metadata={DESERIALIZER_OPTIONS: NAME_OPTIONS})
    fiber: Fiber = field(metadata={DESERIALIZER_OPTIONS: FIBER_OPTIONS})
    matrix: Matrix = field(metadata={DESERIALIZER_OPTIONS: MATRIX_OPTIONS})
    f_mass_cont: float = field(metadata={DESERIALIZER_OPTIONS: F_MASS_CONT_OPTIONS})
    f_area_density: float = field(
        metadata={DESERIALIZER_OPTIONS: F_AREA_DENSITY_OPTIONS}
    )
    max_strain_x: float = field(metadata={DESERIALIZER_OPTIONS: MAX_STRAIN_X_OPTIONS})
    max_strain_xy: float = field(metadata={DESERIALIZER_OPTIONS: MAX_STRAIN_XY_OPTIONS})
    cloth_type: ClothType = field(
        metadata={DESERIALIZER_OPTIONS: cloth_type_options}, default=ClothType.WOVEN
    )

    @property
    def modulus_x(self):
        table = {
            "WOVEN": self.modulus_x_,
            "CSM": self.modulus_x_csm,
        }
        return table[self.cloth_type]

    @property
    def modulus_y(self):
        table = {
            "WOVEN": self.modulus_y_,
            "CSM": self.modulus_y_csm,
        }
        return table[self.cloth_type]

    @property
    def modulus_xy(self):
        table = {
            "WOVEN": self.modulus_xy_,
            "CSM": self.modulus_xy_csm,
        }
        return table[self.cloth_type]

    @property
    def _f_vol_cont(self):
        return self.f_mass_cont / (
            self.f_mass_cont
            + (1 - self.f_mass_cont) * self.fiber.density / self.matrix.density
        )

    @property
    def modulus_x_(self):
        return (
            self._f_vol_cont * self.fiber.modulus_x
            + (1 - self._f_vol_cont) * self.matrix.modulus_x
        )

    @property
    def modulus_y_(self) -> float:
        return (
            self.matrix.modulus_x
            / (1 - self.matrix.poisson ** 2)
            * (1 + 0.85 * self._f_vol_cont ** 2)
            / (
                (1 - self._f_vol_cont) ** 1.25
                + self._f_vol_cont
                * self.matrix.modulus_x
                / (self.fiber.modulus_y * (1 - self.matrix.poisson ** 2))
            )
        )

    @property
    def modulus_y_csm(self):
        return self.modulus_x

    @property
    def modulus_xy_(self):
        return (
            self.matrix.modulus_xy
            * (1 + 0.8 * self._f_vol_cont ** 0.8)
            / (
                (1 - self._f_vol_cont) ** 1.25
                + self.matrix.modulus_xy * self._f_vol_cont / self.fiber.modulus_xy
            )
        )

    @property
    def modulus_xy_csm(self):
        return self.modulus_x / (2 * (1 + self.poisson_xy))

    @property
    def modulus_x_csm(self):
        return 3 / 8 * self.modulus_x_ + 5 / 8 * self.modulus_y_

    @property
    def poisson_xy(self):
        return (
            self._f_vol_cont * self.fiber.poisson
            + (1 - self._f_vol_cont) * self.matrix.poisson
        )

    @property
    def thickness(self):
        return self.f_area_density * (
            1 / self.fiber.density
            + (1 - self.f_mass_cont) / (self.f_mass_cont * self.matrix.density)
        )


@dataclass
class LaminaPartsCSM(LaminaParts):
    """Lamina made of chopped stranded mat prop caculated from fiber and
    matrix, in accordance to C3.8.2 Elasto-mechanical properties
    of laminated structures
    """

    @property
    def modulus_x(self):
        return 3 / 8 * super().modulus_x + 5 / 8 * super().modulus_y

    @property
    def modulus_y(self):
        return self.modulus_x

    @property
    def modulus_xy(self):
        return self.modulus_x / (2 * (1 + self.poisson_xy))


LAMINA_DATA_TYPES: list[LaminaData] = [LaminaMonolith, LaminaPartsCSM, LaminaParts]
LAMINA_TYPE_TABLE = {lamina.__name__: lamina for lamina in LAMINA_DATA_TYPES}
laminina_type_options = DeSerializerOptions(
    flatten=True,
    add_type=True,
    type_label="lamina_data_type",
    subtype_table=LAMINA_TYPE_TABLE,
    metadata=PrintMetadata(long_name="Lamina defition"),
)

# Factored data out to get composition over inheritance. Redirected the calls to the data object so the code doesnt breakdown
@dataclass
class Lamina:
    """Lamina stiffness and physical properties calculation logic."""

    data: LaminaData = field(metadata={DESERIALIZER_OPTIONS: laminina_type_options})

    @property
    def name(self):
        return self.data.name

    @property
    def modulus_x(self):
        return self.data.modulus_x

    @property
    def modulus_y(self):
        return self.data.modulus_y

    @property
    def modulus_xy(self):
        return self.data.modulus_xy

    @property
    def poisson_xy(self):
        return self.data.poisson_xy

    @property
    def thickness(self):
        return self.data.thickness

    @property
    def f_mass_cont(self):
        return self.data.f_mass_cont

    @property
    def f_area_density(self):
        return self.data.f_area_density

    @property
    def max_strain_x(self):
        return self.data.max_strain_x

    @property
    def max_strain_xy(self):
        return self.data.max_strain_xy

    @property
    def poisson_yx(self):
        return self.poisson_xy * self.modulus_y / self.modulus_x

    @property
    def Q_local(self):
        """Calculates Q matix in the ply local direction"""
        factor = 1 - self.poisson_xy * self.poisson_yx
        Qxx = self.modulus_x / factor
        Qyy = self.modulus_y / factor
        Qxy = self.poisson_xy * self.modulus_y / factor
        return np.array([[Qxx, Qxy, 0], [Qxy, Qyy, 0], [0, 0, self.modulus_xy]])

    @property
    def total_area_density(self):
        return self.f_area_density / self.f_mass_cont


@dataclass
class CoreMat:
    """Core material, with strength and modulus inputs in kPa.
    Density value should be in kg/m3 and resin absorption in kg/m2"""

    name: str = field(metadata={DESERIALIZER_OPTIONS: NAME_OPTIONS})
    strength_shear: float = field(
        metadata={DESERIALIZER_OPTIONS: STRENGTH_SHEAR_OPTIONS}
    )
    modulus_shear: float = field(metadata={DESERIALIZER_OPTIONS: MODULUS_SHEAR_OPTIONS})
    strength_tens: float = field(
        metadata={DESERIALIZER_OPTIONS: STRENGTH_TENSION_OPTIONS}
    )
    modulus_tens: float = field(
        metadata={DESERIALIZER_OPTIONS: MODULUS_TENSION_OPTIONS}
    )
    strength_comp: float = field(metadata={DESERIALIZER_OPTIONS: STRENGTH_COMP_OPTIONS})
    modulus_comp: float = field(metadata={DESERIALIZER_OPTIONS: MODULUS_COMP_OPTIONS})
    density: float = field(metadata={DESERIALIZER_OPTIONS: DENSITY_OPTIONS})
    resin_absorption: float = field(
        metadata={DESERIALIZER_OPTIONS: RESIN_ABSORPTION_OPTIONS}, default=0
    )
    core_type: str = field(
        metadata={DESERIALIZER_OPTIONS: CORE_TYPE_OPTIONS}, default="solid"
    )


@dataclass
class Core:
    """Core definied by core material and thickness (m)"""

    core_material: CoreMat = field(
        metadata={DESERIALIZER_OPTIONS: CORE_MATERIAL_OPTIONS}
    )
    core_thickness: float = field(metadata={DESERIALIZER_OPTIONS: CORE_THICKNESS_OPTIONS})


ply_material_options = DeSerializerOptions(
    subs_by_attr="name",
    subs_collection_name="laminas",
    metadata=PrintMetadata(long_name="Material"),
)
orientation_options = DeSerializerOptions(
    metadata=PrintMetadata(long_name="Orientation", units="degree")
)


@dataclass
class Ply:
    """Single ply material elastic and physical properties.
    orientation - degrees.
    """

    material: Lamina = field(metadata={DESERIALIZER_OPTIONS: ply_material_options})
    orientation: float = field(metadata={DESERIALIZER_OPTIONS: orientation_options})

    @property
    def thickness(self):
        return self.material.thickness

    @property
    def modulus(self):
        return np.array(
            [
                1 / (self.material.thickness * self.single_ABD_matrix_inv[i][i])
                for i in range(3)
            ]
        )

    @property
    def modulus_x(self):
        return self.modulus[0]

    @property
    def modulus_y(self):
        return self.modulus[1]

    @property
    def modulus_xy(self):
        return self.modulus[2]

    @property
    def rotation_matrix(self):
        return self.calc_rotation_matrix(self.orientation)

    @property
    def inv_rotation_matrix(self):
        return _matrix_inv(self.rotation_matrix)

    def calc_rotation_matrix(self, angle):
        """Calculates rotation matrix for a given angle"""
        s = np.sin(np.radians(angle))
        c = np.cos(np.radians(angle))
        return np.array(
            [
                [c ** 2, s ** 2, 2 * s * c],
                [s ** 2, c ** 2, -2 * s * c],
                [-s * c, s * c, (c ** 2 - s ** 2)],
            ]
        )

    @property
    def Q_global(self):
        """Transforms the Q matrix to the global coordinate system"""

        m = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 2]])
        m_inv = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1 / 2]])
        return np.array(
            self.inv_rotation_matrix
            @ self.material.Q_local
            @ m
            @ self.rotation_matrix
            @ m_inv
        )

    @property
    def single_ABD_matrix(self):
        A = self.Q_global * self.material.thickness
        D = self.Q_global * self.material.thickness ** 3 / 12
        B = np.zeros((3, 3))
        return np.vstack((np.hstack((A, B)), np.hstack((B, D))))

    @property
    def single_ABD_matrix_inv(self):
        return _matrix_inv(self.single_ABD_matrix)

    def stress(self, strain):
        return self.Q_global @ strain

    def strain_base_rot(self, strain, rotation_matrix):
        strain[2] /= 2
        strain = rotation_matrix @ strain
        strain[2] *= 2
        return strain

    def strain_local(self, strain):
        return self.strain_base_rot(strain, self.rotation_matrix)

    def response(self, strain):
        strain = np.array(strain)
        stress = self.stress(strain)
        strain_local = self.strain_local(strain)
        stress_local1 = self.material.Q_local @ strain_local
        strain_limit = self.material.limit_strain
        # stress_local2 for checking math is right
        # stress_local2 = self.rotation_matrix @ stress
        return {
            "strain_g_x": Criteria(value=strain[0], allowed=strain_limit[0]),
            "strain_g_y": Criteria(value=strain[0], allowed=strain_limit[1]),
            "ratio_g_y": np.abs(strain_limit[0] / strain[1]),
            "strain_g_xy": strain[2],
            "stress_g_x": stress[0],
            "stress_g_y": stress[1],
            "stress_g_xy": stress[2],
            "strain_l_x": strain_local[0],
            "strain_l_y": strain_local[1],
            "strain_l_xy": strain_local[2],
            "ratio_l_xy": np.abs(strain_limit[1] / strain_local[2]),
            "stress_l1_x": stress_local1[0],
            "stress_l1_y": stress_local1[1],
            "stress_l1_xy": stress_local1[2],
        }


@dataclass
class PlyPositioned:
    ply: Ply
    z_coord: Tuple[float, float]

    @property
    def modulus(self):
        return self.ply.modulus

    @property
    def material(self):
        return self.ply.material

    @property
    def orientation(self):
        return self.ply.orientation

    @property
    def Q_global(self):
        return self.ply.Q_global


class Laminate(Protocol):
    plies_unpositioned_: list[Ply]


@dataclass
class ABCLaminate(ABC):
    """ """

    # Old relic should remove as soon as there is something else working
    @property
    def units_table(self):
        return {
            "default": (
                (("kN/m", "kN", "kN m"), ("m/Kn", "1/kN", "1/(kN m)")),
                (1, 1, 1),
            ),
            "Imp_vector": (
                (("lb/inch", "lb", "lb inch"), ("inch/lb", "1/lb", "1/(lb inch)")),
                (5.7101471627692, 224.809, 8850.75),
            ),
        }

    @abstractproperty
    def plies(self) -> list[PlyPositioned]:
        """Must place plies in z correct position. Sandwich laminates plies list
        does not include core. It just affects ply z coordinates.
        """
        pass

    @property
    def stiff_matrix(self):
        def ABD_element(Q_array, z_array, power, i, j):
            return sum(
                [
                    Q[i][j] * (z[1] ** power - z[0] ** power) / power
                    for Q, z in zip(Q_array, z_array)
                ]
            )

        def single_matrix(Q_array, z_array, power):
            return np.array(
                [
                    [ABD_element(Q_array, z_array, power, i, j) for j in range(3)]
                    for i in range(3)
                ]
            )

        Q_array = [ply.Q_global for ply in self.plies]
        z_array = [ply.z_coord for ply in self.plies]
        return self.build_ABD(
            *[single_matrix(Q_array, z_array, power) for power in range(1, 4)]
        )

    @property
    def compl_matrix(self):
        return _matrix_inv(self.stiff_matrix)

    @property
    def thickness_eff(self):
        return np.sum([ply.material.thickness for ply in self.plies])

    @property
    def modulus(self):
        return np.array(
            [1 / (self.thickness_eff * self.compl_matrix[i][i]) for i in range(3)]
        )

    @property
    def modulus_x(self):
        return self.modulus[0]

    @property
    def modulus_xy(self):
        return self.modulus[2]

    @property
    def modulus_simp(self):
        return np.array(
            [
                np.sum([ply.modulus[i] * ply.material.thickness for ply in self.plies])
                / self.thickness_eff
                for i in range(3)
            ]
        )

    @property
    def f_area_weight(self):
        return np.sum([ply.material.f_area_density for ply in self.plies])

    @property
    def total_area_weight(self):
        return np.sum(
            [
                ply.material.f_area_density / ply.material.f_mass_cont
                for ply in self.plies
            ]
        )

    @property
    def bend_stiff(self):
        return np.array([self.stiff_matrix[3][3], self.stiff_matrix[4][4]])

    @property
    def bend_stiff_simp(self):
        return np.array(
            [
                np.sum(
                    [
                        ply.modulus[i]
                        * (
                            ply.material.thickness ** 3 / 12
                            + ply.material.thickness * np.average(ply.z_coord) ** 2
                        )
                        for ply in self.plies
                    ]
                )
                for i in range(2)
            ]
        )

    @property
    def neutral_axis(self):
        sum_Etzs = [0, 0]
        sum_Ets = [0, 0]
        for i in range(2):
            for ply in self.plies:
                Et = ply.modulus[i] * ply.material.thickness
                sum_Ets[i] += Et
                sum_Etzs[i] += Et * np.average(ply.z_coord)
        return np.array(
            [sum_Etz / sum_Et for sum_Etz, sum_Et in zip(sum_Etzs, sum_Ets)]
        )

    @property
    def neutral_axis2(self):
        sum_Etzs = [0, 0]
        sum_Ets = [0, 0]
        z0 = -self.thickness / 2
        for i in range(2):
            for ply in self.plies:
                Et = ply.modulus[i] * ply.material.thickness
                sum_Ets[i] += Et
                sum_Etzs[i] += Et * (np.average(ply.z_coord) - z0)
        return np.array(
            [sum_Etz / sum_Et for sum_Etz, sum_Et in zip(sum_Etzs, sum_Ets)]
        )

    @property
    def neutral_axis_dif(self):
        return np.array(
            [
                na - na2 + self.thickness / 2
                for na, na2 in zip(self.neutral_axis, self.neutral_axis2)
            ]
        )

    def strain_mid_plane(self, load):
        load = np.array(load)
        return self.compl_matrix @ load

    def strain_2D(self, strain_mid_plane, z):
        strain = strain_mid_plane
        return strain[:3] + z * strain[3:]

    def response_plies(self, load):
        responses = []
        for i, ply in enumerate(self.plies):
            z = ply.z_coord[np.argmax(np.max(np.abs(ply.z_coord)))]
            strain_mp = self.strain_mid_plane(load)
            strain = self.strain_2D(strain_mp, z)
            responses.append({"ply": str(i), **ply.response(strain)})
        return responses

    def _max_resp_plies(self, load):
        responses = self.response_plies(load)
        ply_max_x = np.argmin([ply["ratio_g_x"] for ply in responses])
        ply_max_shear = np.argmin([ply["ratio_l_xy"] for ply in responses])
        return {
            # 'CLT_max_uni_strain_ply': ply_max_x,
            "CLT_uni_ratio": responses[ply_max_x]["ratio_g_x"],
            # 'CLT_max_shear_strain_ply': ply_max_shear,
            "CLT_shear_ratio": responses[ply_max_shear]["ratio_l_xy"],
        }

    def _response_simplified(self, moment):
        z_edges = [self.plies[i].z_coord[i] - self.neutral_axis[0] for i in [0, -1]]
        strains = [moment * z / self.bend_stiff_simp[0] for z in z_edges]
        strain_limits = [self.plies[i].material.limit_strain[0] for i in [0, -1]]
        return {
            "simp_max_uni_ratio": np.min(
                [
                    np.abs(strain_limit / strain)
                    for strain, strain_limit in zip(strains, strain_limits)
                ]
            )
        }

    def response_resume(self, load, CLT=True, simp=True):
        resume = {}
        if CLT:
            resume.update(self._max_resp_plies(load))
        if simp:
            moment = load[3]
            resume.update(self._response_simplified(moment))
        return resume

    def extract_ABD(self, matrix):
        """Assumes a 6x6 ABD [[A, B][B, D]] sitffness or compliance matrix
        and returns the 3x3 A, B and D components
        """

        matrix = np.array(matrix)
        return matrix[:3, :3], matrix[:3, 3:], matrix[3:, 3:]

    def build_ABD(self, A_matrix, B_matrix, D_matrix):
        """Builds a 6x6 matrix [[A, B][B, D]]."""
        return np.array(
            np.vstack(
                [np.hstack([A_matrix, B_matrix]), np.hstack([B_matrix, D_matrix])]
            )
        )

    def convert_matrix(self, matrices, factors):
        return [matrix * factor for matrix, factor in zip(matrices, factors)]

    def print_out_matrix(self, units_system):
        m_types = ["stiff", "compl"]
        matrices = [
            self.extract_ABD(self.stiff_matrix),
            self.extract_ABD(self.compl_matrix),
        ]
        factors = [
            self.units_table[units_system][1],
            (1 / factor for factor in self.units_table[units_system][1]),
        ]
        matrices = [
            self.convert_matrix(matrix, factor)
            for matrix, factor in zip(matrices, factors)
        ]
        units = self.units_table[units_system][0]
        return {
            m_type: {
                "A": (matrix[0], unit[0]),
                "B": (matrix[1], unit[1]),
                "D": (matrix[2], unit[2]),
            }
            for m_type, matrix, unit in zip(m_types, matrices, units)
        }

    def print_out_matrices(self, *args):
        args = ("default", *args)
        return {arg: self.print_out_matrix(arg) for arg in args}


@dataclass
class PlyStack:
    plies: list[Ply]
    multiple: Optional[int] = field(
        metadata={DESERIALIZER_OPTIONS: MULTIPLE_OPTIONS}, default=None
    )
    symmetric: bool = field(
        metadata={DESERIALIZER_OPTIONS: SYMMETRIC_OPTIONS}, default=False
    )
    antisymmetric: bool = field(
        metadata={DESERIALIZER_OPTIONS: ANTI_SYMMETRIC_OPTIONS}, default=False
    )

    @property
    def print_stack_list(self):
        return [
            serialize_dataclass(ply, printing_format=True, include_names=True)
            for ply in self.plies
        ]

    @property
    def print_stack_options(self):
        return serialize_dataclass(
            self, printing_format=True, include_names=True, filter_fields=["plies"]
        )

    def __post_init__(self):
        if self.symmetric and self.antisymmetric:
            raise ValueError(
                "Ply stack can't be both symmetric and antisymmetric at the same time"
            )

    @property
    def stack(self):
        list_of_plies: list[Ply] = deepcopy(self.plies)
        if self.multiple:
            list_of_plies *= self.multiple
        if self.symmetric:
            for item in reversed(list_of_plies):
                list_of_plies.append(item)
        if self.antisymmetric:
            for item in reversed(list_of_plies):
                item.orientation *= -1
                list_of_plies.append(item)

        return list_of_plies


ply_stack_options = DeSerializerOptions(flatten=True)


@dataclass
class SingleSkinLaminate(ABCLaminate):

    name: str
    ply_stack: PlyStack = field(metadata={DESERIALIZER_OPTIONS: ply_stack_options})

    @property
    def thick_array(self) -> float:
        return np.array([ply.thickness for ply in self.ply_stack.stack])

    @property
    def thickness(self) -> float:
        return np.sum(self.thick_array)

    @property
    def z_mid(self) -> float:
        return self.thickness / 2

    @property
    def z_coords(self):
        z0 = np.cumsum(self.thick_array) - self.thick_array[0] - self.z_mid
        return np.array([[z_, z_ + z] for z_, z in zip(z0, self.thick_array)])

    @property
    def plies(self):
        return [
            PlyPositioned(ply, z_coord)
            for ply, z_coord in zip(self.ply_stack.stack, self.z_coords)
        ]


CORE_OPTIONS = DeSerializerOptions(
    flatten=True,
)


@dataclass
class SandwichLaminate(ABCLaminate):
    """Laminate sandwich multiply material."""

    name: str
    outter_laminate_ply_stack: PlyStack
    core: Core = field(metadata={DESERIALIZER_OPTIONS: CORE_OPTIONS})
    inner_laminate_ply_stack: PlyStack = None
    symmetric: bool = field(
        metadata={DESERIALIZER_OPTIONS: SYMMETRIC_OPTIONS}, default=False
    )
    antisymmetric: bool = field(
        metadata={DESERIALIZER_OPTIONS: ANTI_SYMMETRIC_OPTIONS}, default=False
    )

    def __post_init__(self):
        if self.symmetric and self.antisymmetric:
            raise ValueError(
                "Sandwich laminate can't be both symmetric and antisymmetric at the same time"
            )

        if not self.inner_laminate_ply_stack and not (
            self.symmetric or self.antisymmetric
        ):
            raise ValueError(
                "Must either provide inner_laminate_ply_list or let laminate be symmetric or antisymmetric."
            )

    @property
    def print_laminate_options(self):
        return serialize_dataclass(
            self,
            printing_format=True,
            include_names=True,
            filter_fields=[
                "name",
                "outter_laminate_ply_stack",
                "inner_laminate_ply_stack",
            ],
        )

    @property
    def exp(self):
        return 1 / 3

    @property
    def outter_laminate(self):
        return SingleSkinLaminate(
            ply_stack=self.outter_laminate_ply_stack, name="outter_skin"
        )

    @property
    def inner_laminate(self):
        inner_plies_stack = self.inner_laminate_ply_stack

        if self.symmetric:
            inner_plies_stack = PlyStack(
                plies=[
                    Ply(material=material, orientation=orientation)
                    for material, orientation in reversed(
                        self.outter_laminate_ply_stack.stack
                    )
                ]
            )

        if self.antisymmetric:
            inner_plies_stack = PlyStack(
                plies=[
                    Ply(material=material, orientation=-orientation)
                    for material, orientation in reversed(
                        self.outter_laminate_ply_stack.stack
                    )
                ]
            )

        return SingleSkinLaminate(ply_stack=inner_plies_stack, name="inner_skin")

    @property
    def plies(self):
        outter_plies = [
            PlyPositioned(
                ply,
                z_coord
                - self.core.core_thickness / 2
                - self.outter_laminate.thickness / 2,
            )
            for ply, z_coord in zip(
                self.inner_laminate_ply_stack.stack, self.outter_laminate.z_coords
            )
        ]
        inner_plies = [
            PlyPositioned(
                ply,
                z_coord
                + self.core.core_thickness / 2
                + self.inner_laminate.thickness / 2,
            )
            for ply, z_coord in zip(
                self.inner_laminate.ply_stack.stack, self.inner_laminate.z_coords
            )
        ]
        return outter_plies + inner_plies

    @property
    def thickness(self):
        return (
            self.inner_laminate.thickness
            + self.outter_laminate.thickness
            + self.core.core_thickness
        )
