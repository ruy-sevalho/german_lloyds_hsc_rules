"""
 # @ Author: Ruy Sevalho
 # @ Create Time: 2021-08-24 10:00:10
 # @ Description:
 """

import pytest as pt
from gl_hsc_scantling.shortcut import Core, CoreMat


@pt.fixture
def H80_input():
    return {
        "core_type": "solid",
        "strength_shear": 950,
        "modulus_shear": 23000,
        "strength_tens": 2200,
        "modulus_tens": 85000,
        "strength_comp": 1150,
        "modulus_comp": 80000,
        "density": 80,
        "resin_absorption": 0.35,
        "name": "H80",
    }


@pt.fixture
def H80(H80_input):
    return CoreMat(**H80_input)


# @pt.fixture
# def H80_20mm_input(H80):
#     return {"core_material": H80, "thickness": 0.02, "name": "H80_20mm"}


# @pt.fixture
# def H80_20mm(H80_20mm_input):
#     return Core(**H80_20mm_input)
