# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 10:37:57 2021

@author: ruy
"""

from collections import OrderedDict
import pytest as pt
import numpy as np
from gl_hsc_scantling.composites import (
    Lamina_parts_woven,
    Matrix,
    Fiber,
    Core,
    Core_mat,
    lamina_factory,
    Lamina,
    SingleSkinLaminate,
    SandwichLaminate,
    Ply,
)
from gl_hsc_scantling.vessel import Vessel
from gl_hsc_scantling.stiffeners import LBar, Stiffener
from .exp_output import ExpPly, ExpLaminate, ExpStiffSection

from .fixatures_vessel import *
from .fixatures_matrices import *
from .fixatures_fibers import *
from .fixatures_laminas import *
from .fixatures_cores import *

@pt.fixture
def et_0900_20x_input(et_0900):
    orientation = [0, 90]
    return [Ply(material=et_0900, orientation=ang) for ang in orientation] * 10


@pt.fixture
def et_0900_20x(et_0900_20x_input):
    return SingleSkinLaminate(plies_unpositioned=et_0900_20x_input, name="et_0900_20x")


def build_sub_matrix(M11, M12, M16, M22, M26, M66):
    return np.array([[M11, M12, M16], [M12, M22, M26], [M16, M26, M66]])


def build_ABD_matrix(A, B, D):
    return np.array(np.vstack([np.hstack([A, B]), np.hstack([B, D])]))


@pt.fixture
def et_0900_20x_exp():
    A11 = 124942.182621839
    A12 = 16472.6698461771
    A16 = 0
    A22 = 124942.182621839
    A26 = 0
    A66 = 20656.8
    A = build_sub_matrix(A11, A12, A16, A22, A26, A66)
    B11 = 6.62197298626791
    B12 = 0
    B16 = 0
    B22 = -6.62197298626791
    B26 = 0
    B66 = 0
    B = build_sub_matrix(B11, B12, B16, B22, B26, B66)
    D11 = 0.216499814047123
    D12 = 0.028543842309456
    D16 = 0
    D22 = 0.216499814047123
    D26 = 0
    D66 = 0.03579410304
    D = build_sub_matrix(D11, D12, D16, D22, D26, D66)
    stiff_m = build_ABD_matrix(A, B, D)
    return ExpLaminate(thickness=0.004566, stiff_m=stiff_m, name="et_0900_20x")


@pt.fixture
def et_0900_20x_45deg_input(et_0900):
    orientation = [45, -45]
    return [Ply(material=et_0900, orientation=ang) for ang in orientation] * 10


@pt.fixture
def et_0900_20x_input(et_0900):
    orientation = [0, 90]
    return [Ply(material=et_0900, orientation=ang) for ang in orientation] * 10


@pt.fixture
def et_0900_20x_45deg(et_0900_20x_45deg_input):
    return SingleSkinLaminate(
        name="et_0900_20x_45deg", plies_unpositioned=et_0900_20x_45deg_input
    )


@pt.fixture
def et_0900_20x_45deg_exp():
    A11 = 91364.16
    A12 = 50050.56
    A16 = 0
    A22 = 91364.16
    A26 = 0
    A66 = 54234.816
    A = build_sub_matrix(A11, A12, A16, A22, A26, A66)
    B11 = 0
    B12 = 0
    B16 = 3.3109857216
    B22 = 0
    B26 = 3.3109857216
    B66 = 0
    B = build_sub_matrix(B11, B12, B16, B22, B26, B66)
    D11 = 0.158315816448
    D12 = 0.086727610368
    D16 = 0
    D22 = 0.158315816448
    D26 = 0
    D66 = 0.0939780891648
    D = build_sub_matrix(D11, D12, D16, D22, D26, D66)
    stiff_m = build_ABD_matrix(A, B, D)
    return ExpLaminate(thickness=0.004566, stiff_m=stiff_m, name="et_0900_20x")


@pt.fixture
def sandwich_laminate_skin_input(et_0900):
    orientation = [0, 90]
    lam = [Ply(material=et_0900, orientation=ang) for ang in orientation] * 5

    return lam


@pt.fixture
def sandwich_laminate_skin(sandwich_laminate_skin_input):
    return SingleSkinLaminate(
        name="sandwich_laminate_skin", plies_unpositioned=sandwich_laminate_skin_input
    )


@pt.fixture
def sandwich_laminate(sandwich_laminate_skin, H80_20mm):
    return SandwichLaminate(
        name="sandwich_laminate",
        outter_laminate=sandwich_laminate_skin,
        inner_laminate=sandwich_laminate_skin,
        core=H80_20mm,
    )


@pt.fixture
def sandwich_laminate_exp():
    A11 = 124942.182621839
    A12 = 16472.6698461771
    A16 = 0
    A22 = 124942.182621839
    A26 = 0
    A66 = 20656.8
    A = build_sub_matrix(A11, A12, A16, A22, A26, A66)
    B11 = 6.62197298626943
    B12 = 0
    B16 = 0
    B22 = -6.62197298626791
    B26 = 0
    B66 = 0
    B = build_sub_matrix(B11, B12, B16, B22, B26, B66)
    D11 = 15.5593998400091
    D12 = 2.05138769942001
    D16 = 0
    D22 = 15.5593998400091
    D26 = 0
    D66 = 2.57244914304001
    D = build_sub_matrix(D11, D12, D16, D22, D26, D66)
    stiff_m = build_ABD_matrix(A, B, D)
    return ExpLaminate(thickness=0.02456, stiff_m=stiff_m, name="sandwich_laminate")


@pt.fixture
def laminates(et_0900_20x, et_0900_20x_45deg, sandwich_laminate):
    args = [et_0900_20x, et_0900_20x_45deg, sandwich_laminate]
    return {arg.name: arg for arg in args}


@pt.fixture
def l_bar_input(et_0900_20x_45deg, et_0900_20x):
    return {
        "laminate_web": et_0900_20x_45deg,
        "dimension_web": 0.1,
        "laminate_flange": et_0900_20x,
        "dimension_flange": 0.02,
        "name": "l_bar",
    }


@pt.fixture
def l_bar(l_bar_input):
    return LBar(**l_bar_input)


@pt.fixture
def l_bar_exp():
    return ExpStiffSection("l_bar")
