# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 11:49:36 2020

@author: ruy
"""

from functools import cache
from abc import ABC, abstractproperty
from enum import Enum, auto
from typing import Tuple

import numpy as np
from .dc import dataclass

from .report import (
    NamePrint,
    _print_wrapper_builder,
    _data_to_dict,
    _input_data_dict,
    Data,
    Criteria,
)


def _matrix_inv(matrix):
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
class Matrix(Data):
    """Generic matrix - resins -  material"""

    name: str
    density: float
    modulus_x: float
    modulus_xy: float
    poisson: float


@dataclass
class Fiber(Data):
    """Generic fiber material"""

    name: str
    density: float
    modulus_x: float
    modulus_y: float
    modulus_xy: float
    poisson: float


class Lamina(ABC):
    thickness: float
    modulus_x: float
    modulus_y: float
    modulus_xy: float

    @property
    def limit_strain(self):
        return np.array([self.max_strain_x, self.max_strain_xy])

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
class LaminaMonolith(Lamina, Data):
    """Single lamina externally defiened properties"""

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
class LaminaPartsWoven(Lamina):
    """Single lamina made of woven cloth - prop caculated from fiber and
    matrix, in accordance to C3.8.2 Elasto-mechanical properties
    of laminated structures.
    """

    name: str
    fiber: Fiber
    matrix: Matrix
    f_mass_cont: float
    f_area_density: float
    max_strain_x: float
    max_strain_xy: float

    @property
    def f_vol_cont(self):
        return self.f_mass_cont / (
            self.f_mass_cont
            + (1 - self.f_mass_cont) * self.fiber.density / self.matrix.density
        )

    @property
    def modulus_x(self):
        return (
            self.f_vol_cont * self.fiber.modulus_x
            + (1 - self.f_vol_cont) * self.matrix.modulus_x
        )

    @property
    def modulus_y(self):
        return (
            self.matrix.modulus_x
            / (1 - self.matrix.poisson ** 2)
            * (1 + 0.85 * self.f_vol_cont ** 2)
            / (
                (1 - self.f_vol_cont) ** 1.25
                + self.f_vol_cont
                * self.matrix.modulus_x
                / (self.fiber.modulus_y * (1 - self.matrix.poisson ** 2))
            )
        )

    @property
    def modulus_xy(self):
        return (
            self.matrix.modulus_xy
            * (1 + 0.8 * self.f_vol_cont ** 0.8)
            / (
                (1 - self.f_vol_cont) ** 1.25
                + self.matrix.modulus_xy * self.f_vol_cont / self.fiber.modulus_xy
            )
        )

    @property
    def poisson_xy(self):
        return (
            self.f_vol_cont * self.fiber.poisson
            + (1 - self.f_vol_cont) * self.matrix.poisson
        )

    @property
    def thickness(self):
        return self.f_area_density * (
            1 / self.fiber.density
            + (1 - self.f_mass_cont) / (self.f_mass_cont * self.matrix.density)
        )


@dataclass
class LaminaPartsCSM(LaminaPartsWoven):
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


@dataclass
class Core_mat(Data):
    """Core material, with strength and modulus inputs in kPa.
    Density value should be in kg/m3 and resin absorption in kg/m2"""

    name: str
    strength_shear: float
    modulus_shear: float
    strength_tens: float
    modulus_tens: float
    strength_comp: float
    modulus_comp: float
    density: float
    resin_absorption: float = 0
    core_type: str = "solid"


@dataclass
class Core(Data):
    """Core definied by core material and thickness (m)"""

    name: str
    core_material: Core_mat
    thickness: float


@dataclass
class Ply:
    """Single ply material elastic and physical properties.
    orientation - degrees.
    """

    material: Lamina
    orientation: float

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


@dataclass
class ABCLaminate(Data, ABC):
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

    @property
    def thick_array(self) -> float:
        return np.array([ply.thickness for ply in self.plies_unpositioned])

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

    @abstractproperty
    def plies() -> list[PlyPositioned]:
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
class SingleSkinLaminate(ABCLaminate):

    name: str
    plies_unpositioned: list[Ply]

    @property
    def plies(self):
        return [
            PlyPositioned(ply, z_coord)
            for ply, z_coord in zip(self.plies_unpositioned, self.z_coords)
        ]


@dataclass
class SandwichLaminate(ABCLaminate):
    """Laminate sandwich multiply material. plies_materials should be dict
    with plies used in laminate. plies_list should be list of dicts, in the
    form {'material': string of material name, 'orientation': angle(deg).
    corresponding to the definition of each ply. Only one ply should be of the
    Core type.
    """

    name: str
    outter_laminate: SingleSkinLaminate
    inner_laminate: SingleSkinLaminate
    core: Core

    @property
    def plies_unpositioned(self):
        return [self.outter_laminate, self.core, self.inner_laminate]

    @property
    def plies(self):
        outter_plies = [
            PlyPositioned(
                ply,
                z_coord - self.core.thickness / 2 - self.outter_laminate.thickness / 2,
            )
            for ply, z_coord in zip(
                self.inner_laminate.plies_unpositioned, self.outter_laminate.z_coords
            )
        ]
        inner_plies = [
            PlyPositioned(
                ply,
                z_coord + self.core.thickness / 2 + self.inner_laminate.thickness / 2,
            )
            for ply, z_coord in zip(
                self.inner_laminate.plies_unpositioned, self.inner_laminate.z_coords
            )
        ]
        return outter_plies + inner_plies

    @property
    def exp(self):
        return 1 / 3

    @property
    def skins(self):
        return [self.outter_laminate, self.inner_laminate]
