"""
 # @ Author: Ruy Sevalho
 # @ Create Time: 2021-08-24 15:34:12
 # @ Description:
 """

import pytest as pt

from gl_hsc_scantling import Panel, StructuralElement, Bottom, Side, WetDeck, Vessel

from .fixatures_vessel import *
from .fixatures_laminates import *

from .exp_output import ExpPanel


@pt.fixture
def panel_bottom_01(et_0900_20x, vessel_ex1):
    panel = Panel(dim_x=1, dim_y=1, laminate=et_0900_20x)
    bottom = Bottom(deadrise=16)
    return StructuralElement(
        name="Bottom Panel 01",
        x=8,
        z=-0.3,
        vessel=vessel_ex1,
        model=panel,
        location=bottom,
    )


@pt.fixture
def panel_bottom_01_exp():
    return ExpPanel(
        name="Bottom Panel 01", pressures={"impact": 23.7413793103448, "sea": 18.46875}
    )


@pt.fixture
def panel_bottom_02(et_0900_20x, vessel_ex1):
    panel = Panel(dim_x=1, dim_y=1, laminate=et_0900_20x)
    bottom = Bottom(deadrise=5)
    return StructuralElement(
        name="Bottom Panel 02",
        x=8,
        z=-0.3,
        vessel=vessel_ex1,
        model=panel,
        location=bottom,
    )


@pt.fixture
def panel_bottom_02_exp():
    return ExpPanel(
        name="Bottom Panel 02", pressures={"impact": 26.3793103448276, "sea": 18.46875}
    )


@pt.fixture
def panel_bottom_03(et_0900_20x, vessel_ex1):
    panel = Panel(dim_x=1, dim_y=1, laminate=et_0900_20x)
    bottom = Bottom(deadrise=35)
    return StructuralElement(
        name="Bottom Panel 03",
        x=8,
        z=-0.3,
        vessel=vessel_ex1,
        model=panel,
        location=bottom,
    )


@pt.fixture
def panel_bottom_03_exp():
    return ExpPanel(
        name="Bottom Panel 03", pressures={"impact": 17.5862068965517, "sea": 18.46875}
    )


@pt.fixture
def panel_bottom_04(et_0900_20x, vessel_ex1):
    panel = Panel(dim_x=1, dim_y=1, laminate=et_0900_20x)
    bottom = Bottom(deadrise=35)
    return StructuralElement(
        name="Bottom Panel 04",
        x=3,
        z=-0.3,
        vessel=vessel_ex1,
        model=panel,
        location=bottom,
    )


@pt.fixture
def panel_bottom_04_exp():
    return ExpPanel(name="Bottom Panel 04", pressures={"impact": 0, "sea": 13.875})


@pt.fixture
def panel_bottom_05(et_0900_20x, vessel_ex1):
    panel = Panel(dim_x=1, dim_y=1, laminate=et_0900_20x)
    bottom = Bottom(deadrise=12)
    return StructuralElement(
        name="Bottom Panel 05",
        x=9.5,
        z=-0.3,
        vessel=vessel_ex1,
        model=panel,
        location=bottom,
    )


@pt.fixture
def panel_bottom_05_exp():
    return ExpPanel(name="Bottom Panel 05", pressures={"impact": 15.9375, "sea": 20})
