# -*- coding: utf-8 -*-
"""
Created on Mon May 31 15:45:24 2021

@author: ruy
"""
import pytest as pt


def ply_check(ply, exp):
    assert ply.name == exp.name
    assert ply.thickness == pt.approx(exp.thickness)
    assert ply.modulus_x == pt.approx(exp.modulus_x)
    assert ply.modulus_y == pt.approx(exp.modulus_y)
    assert ply.modulus_xy == pt.approx(exp.modulus_xy)
    assert ply.poisson_xy == pt.approx(exp.poisson_xy)
    assert ply.poisson_yx == pt.approx(exp.poisson_yx, abs=1e-2)


def laminate_check(laminate, exp):
    assert laminate.thickness == pt.approx(exp.thickness, rel=1e-2)
    assert laminate.stiff_matrix.shape == exp.stiff_m.shape
    assert laminate.stiff_matrix == pt.approx(exp.stiff_m, rel=1e-5, abs=1e-9)


def test_E_glass_poly_70_304(E_glass_poly_70_304, E_glass_poly_70_304_expected):
    ply_check(E_glass_poly_70_304, E_glass_poly_70_304_expected)


def test_E_glass_poly_30_304(E_glass_poly_30_304, E_glass_poly_30_304_expected):
    ply_check(E_glass_poly_30_304, E_glass_poly_30_304_expected)


def test_et_0900_20x(et_0900_20x, et_0900_20x_exp):
    laminate_check(et_0900_20x, et_0900_20x_exp)


def test_et_0900_20x_45deg(et_0900_20x_45deg, et_0900_20x_45deg_exp):
    laminate_check(et_0900_20x_45deg, et_0900_20x_45deg_exp)


def test_sandwich_laminate(sandwich_laminate, sandwich_laminate_exp):
    laminate_check(sandwich_laminate, sandwich_laminate_exp)
