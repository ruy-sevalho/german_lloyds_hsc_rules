# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 11:49:36 2020

@author: ruy
"""
from abc import ABC, abstractmethod, abstractproperty
from copy import deepcopy
from dataclasses import asdict, dataclass, field, astuple
from enum import Enum
from functools import cache
from re import T
from typing import Any, Optional, Protocol, Tuple, TYPE_CHECKING
from urllib import response

import numpy as np
import pandas as pd
from quantities import Quantity

from dataclass_tools.tools import (
    DESERIALIZER_OPTIONS,
    DeSerializerOptions,
    PrintMetadata,
    serialize_dataclass,
)

from gl_hsc_scantling.safety_factors import CORE_SHEAR_SF

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
from .utils import Criteria, criteria

if TYPE_CHECKING:
    from gl_hsc_scantling.panels import Panel


DIRECTION_LABELS = ["x", "y", "xy"]
Z_LABEL = "z"
PLY_LABEL = "ply"
PLY_MATERIAL_OPTIONS = DeSerializerOptions(
    subs_by_attr="name",
    subs_collection_name="laminas",
    metadata=PrintMetadata(long_name="Material"),
)
ORIENTATION_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(long_name="Orientation", units="degree")
)
CLOTH_TYPE_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(long_name="Cloth type", abreviation="cloth")
)
PLY_STACK_OPTIONS = DeSerializerOptions(flatten=True)
CORE_OPTIONS = DeSerializerOptions(
    subs_by_attr="name",
    subs_collection_name="cores",
    metadata=PrintMetadata(long_name="Core", abreviation="core"),
)


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
        metadata={DESERIALIZER_OPTIONS: CLOTH_TYPE_OPTIONS}, default=ClothType.WOVEN
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
            / (1 - self.matrix.poisson**2)
            * (1 + 0.85 * self._f_vol_cont**2)
            / (
                (1 - self._f_vol_cont) ** 1.25
                + self._f_vol_cont
                * self.matrix.modulus_x
                / (self.fiber.modulus_y * (1 - self.matrix.poisson**2))
            )
        )

    @property
    def modulus_y_csm(self):
        return self.modulus_x

    @property
    def modulus_xy_(self):
        return (
            self.matrix.modulus_xy
            * (1 + 0.8 * self._f_vol_cont**0.8)
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


# Gotta be here because uses previous definitios
LAMINA_DATA_TYPES: list[LaminaData] = [LaminaMonolith, LaminaPartsCSM, LaminaParts]
LAMINA_TYPE_TABLE = {lamina.__name__: lamina for lamina in LAMINA_DATA_TYPES}
LAMININA_TYPE_OPTIONS = DeSerializerOptions(
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

    data: LaminaData = field(metadata={DESERIALIZER_OPTIONS: LAMININA_TYPE_OPTIONS})

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


class CoreType(str, Enum):
    SOLID = "SOLID"
    HONEYCOMB = "HONEYCOMB"


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
    core_type: CoreType = field(
        metadata={DESERIALIZER_OPTIONS: CORE_TYPE_OPTIONS}, default=CoreType.SOLID
    )


@dataclass
class Core:
    """Core definied by core material and thickness (m)"""

    name: str = field(metadata={DESERIALIZER_OPTIONS: NAME_OPTIONS})
    material: CoreMat = field(metadata={DESERIALIZER_OPTIONS: CORE_MATERIAL_OPTIONS})
    thickness: float = field(metadata={DESERIALIZER_OPTIONS: CORE_THICKNESS_OPTIONS})


@dataclass
class PlyState:
    stress_global: pd.DataFrame
    strain_local: pd.DataFrame
    strain_local_ratio: pd.DataFrame
    stress_local: pd.DataFrame


def _process_ply_state(
    stress_global: list,
    strain_local: list,
    strain_local_ratio: list,
    stress_local: list,
):
    states = [stress_global, strain_local, strain_local_ratio, stress_local]
    direction_labels = DIRECTION_LABELS
    state = PlyState(
        *(
            pd.DataFrame(
                {
                    direction: [value]
                    for direction, value in zip(direction_labels, state)
                }
            )
            for state in states
        )
    )
    return state


@dataclass
class LaminateState:
    load: list[float]
    strain: list[float]
    strain_global: pd.DataFrame = pd.DataFrame()
    stress_global: pd.DataFrame = pd.DataFrame()
    strain_local: pd.DataFrame = pd.DataFrame()
    strain_local_ratio: pd.DataFrame = pd.DataFrame()
    stress_local: pd.DataFrame = pd.DataFrame()


@dataclass
class Ply:
    """Single ply material elastic and physical properties.
    orientation - degrees.
    """

    material: Lamina = field(metadata={DESERIALIZER_OPTIONS: PLY_MATERIAL_OPTIONS})
    orientation: float = field(metadata={DESERIALIZER_OPTIONS: ORIENTATION_OPTIONS})

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
                [c**2, s**2, 2 * s * c],
                [s**2, c**2, -2 * s * c],
                [-s * c, s * c, (c**2 - s**2)],
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
        D = self.Q_global * self.material.thickness**3 / 12
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
        limit_values = [self.material.max_strain_x] * 2 + [self.material.max_strain_xy]
        safety_factor = 3
        strain_local_ratio = [
            Criteria(
                calculated_value=np.abs(strain_),
                theoretical_limit_value=limit,
                safety_factor=safety_factor,
            )  # .ratio
            for strain_, limit in zip(strain_local, limit_values)
        ]
        stress_local = self.material.Q_local @ strain_local
        return _process_ply_state(
            stress_global=stress,
            strain_local=strain_local,
            strain_local_ratio=strain_local_ratio,
            stress_local=stress_local,
        )


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


@dataclass
class Laminate(ABC):
    """General laminate behaviour, commom to both single skin and sandwich laminates."""

    name: str

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
    def thickness(self) -> float:
        """Overall laminate thickness. Includes core in sandwich laminates"""

    @abstractproperty
    def plies(self) -> list[PlyPositioned]:
        """Must place plies in z correct position. Sandwich laminates plies list
        does not include core. It just affects ply z coordinates.
        """

    @abstractmethod
    def panel_rule_check(self, panel, pressure: float) -> pd.DataFrame:
        """Returns a dictionary of rules checks against a given load,
        where the value given is the ratio between the allowed value
        and calculated value.
        """

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
                            ply.material.thickness**3 / 12
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

    def _add_strain_response_to_df(self, z: float, strain_mp: list[float]):
        strain_vector = self.strain_2D(strain_mp, z)
        df = pd.DataFrame(
            {
                **{
                    strain_label: [strain_component]
                    for strain_label, strain_component in zip(
                        DIRECTION_LABELS, strain_vector
                    )
                },
                Z_LABEL: [z],
            }
        )
        return df

    def response_plies(self, load) -> LaminateState:
        strain_mp = self.strain_mid_plane(load)

        # Initializing the strain df, since it has one more row than
        # the lenght of the following for loop that populates the
        # rest of the results
        z = self.plies[0].z_coord[0]
        strain_df = pd.DataFrame(
            self._add_strain_response_to_df(z=z, strain_mp=strain_mp)
        )
        state = LaminateState(load=load, strain=strain_mp, strain_global=strain_df)
        for i, ply in enumerate(self.plies):
            z = ply.z_coord[1]
            state.strain_global = pd.concat(
                [
                    state.strain_global,
                    self._add_strain_response_to_df(z=z, strain_mp=strain_mp),
                ]
            )
            for z in ply.z_coord:
                strain = self.strain_2D(strain_mid_plane=strain_mp, z=z)
                response = ply.ply.response(strain)
                d: dict[str, pd.DataFrame] = asdict(response)
                for key, value in d.items():
                    laminate_state_df: pd.DataFrame = getattr(state, key)
                    value[Z_LABEL] = z
                    value[PLY_LABEL] = i
                    laminate_state_df = pd.concat([laminate_state_df, value])
                    state.__setattr__(key, laminate_state_df)
        return state

    def max_strain_ratio(self, response: LaminateState) -> pd.DataFrame:
        linear_directions = ["x", "y"]
        linear_strain = np.min(
            [
                np.min(response.strain_local_ratio[direction])
                for direction in linear_directions
            ]
        )
        shear_strain = np.min(response.strain_local_ratio["xy"])
        return pd.DataFrame(
            {
                "linear_strain_ratio": [linear_strain],
                "shear_strain_ratio": [shear_strain],
            }
        )

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

    @property
    def seydel_factor(self):
        D12 = self.stiff_matrix[3, 4]
        D11 = self.stiff_matrix[3, 3]
        D22 = self.stiff_matrix[4, 4]
        D33 = self.stiff_matrix[5, 5]
        return (D12 + 2 * D33) / (D11 * D22) ** (1 / 2)

    def buckling_shear_strain(self, width: float, length: float) -> float:
        """C3.8.6.3 Buckling of orthotropic plates under
        in-plane shear loads.
        1 Critical buckling strain
        """
        D11 = self.stiff_matrix[3, 3]
        D22 = self.stiff_matrix[4, 4]
        mod_asp_r = width / length * (D11 / D22) ** (1 / 4)
        if mod_asp_r <= 1:
            s = width
            Da = D11
            Db = D22
        else:
            mod_asp_r = 1 / mod_asp_r
            s = length
            Da = D22
            Db = D11
        coef_ks = self.calc_coef_ks(mod_asp_r)
        return (coef_ks * (np.pi / s) ** 2 * (Da * Db**3) ** (0.25)) / (
            self.modulus_xy * self.thickness_eff
        )

    def calc_coef_ks(self, asp_ratio):
        """C3.8.6.3 Buckling of orthotropic plates under
        in-plane shear loads.
        kS = buckling coefficient, as per Fig. C3.8.12
        """
        xp = np.array(range(11)) / 10
        fp = {
            0.0: [
                3.34528,
                3.37329,
                3.42097,
                3.48325,
                3.55803,
                3.66243,
                3.81342,
                4.00646,
                4.23399,
                4.49888,
                4.80574,
            ],
            0.4: [
                4.23778,
                4.24273,
                4.30864,
                4.42958,
                4.59181,
                4.79673,
                5.06405,
                5.41067,
                5.83258,
                6.30655,
                6.81896,
            ],
            0.8: [
                4.97935,
                5.0401,
                5.15263,
                5.319,
                5.55205,
                5.86016,
                6.24856,
                6.70883,
                7.22622,
                7.78833,
                8.404,
            ],
            1.0: [
                5.28092,
                5.36478,
                5.50693,
                5.70784,
                5.95351,
                6.26361,
                6.6815,
                7.19426,
                7.79788,
                8.51283,
                9.33426,
            ],
            1.2: [
                5.6772,
                5.80211,
                5.95189,
                6.14655,
                6.43489,
                6.82919,
                7.32083,
                7.90675,
                8.58399,
                9.34883,
                10.20889,
            ],
            1.6: [
                6.35288,
                6.46749,
                6.63198,
                6.85659,
                7.19295,
                7.66999,
                8.27659,
                9.0039,
                9.85082,
                10.80789,
                11.86192,
            ],
            2.0: [
                6.95278,
                7.09907,
                7.32589,
                7.64945,
                8.09345,
                8.66811,
                9.37673,
                10.20068,
                11.14849,
                12.24589,
                13.53398,
            ],
            2.4: [
                7.57073,
                7.80339,
                8.06953,
                8.41767,
                8.91613,
                9.58415,
                10.43038,
                11.4412,
                12.56962,
                13.84555,
                15.32557,
            ],
            2.8: [
                8.1678,
                8.30154,
                8.56435,
                8.98312,
                9.57548,
                10.36163,
                11.34033,
                12.4871,
                13.80315,
                15.28743,
                16.92195,
            ],
        }
        beta_values = list(fp.keys())
        index = np.searchsorted(beta_values, self.seydel_factor)
        betas = [beta_values[index - 1], beta_values[index]]
        return sum([np.interp(asp_ratio, xp, fp[beta]) for beta in betas]) / 2


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


@dataclass
class SingleSkinLaminate(Laminate):

    name: str
    ply_stack: PlyStack = field(metadata={DESERIALIZER_OPTIONS: PLY_STACK_OPTIONS})

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

    def panel_rule_check(self, panel: "Panel", pressure: float) -> pd.DataFrame:
        load = panel.load_array(pressure=pressure)
        response = self.response_plies(load)
        return self.max_strain_ratio(response)


@dataclass
class SandwichLaminate(Laminate):
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
                z_coord - self.core.thickness / 2 - self.outter_laminate.thickness / 2,
            )
            for ply, z_coord in zip(
                self.inner_laminate_ply_stack.stack, self.outter_laminate.z_coords
            )
        ]
        inner_plies = [
            PlyPositioned(
                ply,
                z_coord + self.core.thickness / 2 + self.inner_laminate.thickness / 2,
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
            + self.core.thickness
        )

    def core_shear_stress(self, shear_force: float):
        """C3.8.3.4 Determination of laminate strains and stresses
        .2 Determination of core shear stresses in sandwich laminates.
        """
        return shear_force / (
            self.core.thickness
            + self.outter_laminate.thickness / 2
            + self.inner_laminate.thickness / 2
        )

    def core_shear_stress_ratio(self, shear_force: float):
        ratio = Criteria(
            calculated_value=self.core_shear_stress(shear_force=shear_force),
            theoretical_limit_value=self.core.material.strength_shear,
            safety_factor=CORE_SHEAR_SF,
        )
        return pd.DataFrame({"core_shear_stress_ratio": [ratio]})

    def _critical_skin_wrinkling_solid_core(self, panel):
        """C3.8.6.1 Skin wrinkling of sandwich skins"""
        K1 = 0.5
        index = panel.direction_table[panel.span_direction]
        flexural_modulus = self.outter_laminate.bend_stiff[index] / (
            self.outter_laminate.thickness**3 / 12
        )
        return (
            K1
            * (
                flexural_modulus
                * self.core.material.modulus_comp
                * self.core.material.modulus_shear
            )
            ** 0.5
            / self.outter_laminate.modulus[index]
        )

    def _critical_skin_wrinkling(self, panel: "Panel"):
        table = {CoreType.SOLID: self._critical_skin_wrinkling_solid_core}
        return table[self.core.material.core_type](panel=panel)

    def skin_wrinkling_check(self, panel: "Panel", response: LaminateState):
        critical_strain = self._critical_skin_wrinkling(panel)
        outer_skin_ply_index = len(self.outter_laminate_ply_stack.plies)
        direction = panel.span_direction
        max_compression_strain = np.min(response.strain_global[direction])
        ratio = Criteria(
            calculated_value=np.abs(max_compression_strain),
            theoretical_limit_value=critical_strain,
            safety_factor=1,
        )
        return pd.DataFrame({"skin_wrinkling_ratio": [ratio]})

    def panel_rule_check(self, panel: "Panel", pressure: float) -> pd.DataFrame:
        load = panel.load_array(pressure=pressure)
        response = self.response_plies(load)
        strain_check = self.max_strain_ratio(response)
        core_shear_check = self.core_shear_stress_ratio(
            shear_force=panel.max_shear_force(pressure=pressure)
        )
        wrinkling_check = self.skin_wrinkling_check(panel=panel, response=response)
        return pd.concat([strain_check, core_shear_check, wrinkling_check], axis=1)
