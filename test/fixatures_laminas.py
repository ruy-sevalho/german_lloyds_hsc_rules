"""
 # @ Author: Ruy Sevalho
 # @ Create Time: 2021-08-24 09:35:50
 # @ Description:
 """

import pytest as pt

from gl_hsc_scantling import Lamina_parts_woven, Lamina_parts_csm, Lamina
from .exp_output import ExpPly
from .fixatures_fibers import *
from .fixatures_matrices import *


@pt.fixture
def E_glass_poly_70_304(eglass_gl, polyester_gl):
    return Lamina_parts_woven(
        name="E_glass_poly_70_304",
        fiber=eglass_gl,
        matrix=polyester_gl,
        f_mass_cont=0.7,
        f_area_density=0.304,
        max_strain_x=0.0035,
        max_strain_xy=0.007,
    )


@pt.fixture
def E_glass_poly_70_304_expected():
    return ExpPly(
        0.000228256467942,
        39704119.8501873,
        9814079.99527406,
        4058669.26991943,
        0.244689138576779,
        0.059409655355304,
        "E_glass_poly_70_304",
    )


@pt.fixture
def E_glass_poly_30_304(eglass_gl, polyester_gl):
    return Lamina_parts_woven(
        name="E_glass_poly_30_304",
        fiber=eglass_gl,
        matrix=polyester_gl,
        f_mass_cont=0.3,
        f_area_density=0.304,
        max_strain_x=0.0035,
        max_strain_xy=0.007,
    )


@pt.fixture
def E_glass_poly_30_304_expected():
    return ExpPly(
        thickness=0.000710796150481,
        modulus_x=14786716.5575304,
        modulus_y=4256597.62674039,
        modulus_xy=1697946.00161313,
        poisson_xy=0.293100093545369,
        poisson_yx=0.084118801363399,
        name="E_glass_poly_30_304",
    )


@pt.fixture
def et_0900_input():
    return {
        "modulus_x": 14336000,
        "modulus_y": 39248000,
        "modulus_xy": 4530000,
        "poisson_xy": 0.09,
        "thickness": 0.000228,
        "f_mass_cont": 0.7,
        "f_area_density": 0.304,
        "max_strain_x": 0.035,
        "max_strain_xy": 0.07,
        "name": "et_0900",
    }


@pt.fixture
def et_0900(et_0900_input):
    return Lamina(**et_0900_input)
