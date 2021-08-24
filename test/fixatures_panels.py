"""
 # @ Author: Ruy Sevalho
 # @ Create Time: 2021-08-24 15:34:12
 # @ Description:
 """

import pytest as pt

from gl_hsc_scantling import Panel, StructuralElement, Bottom, Side, WetDeck, Vessel

from .fixatures_vessel import *
from .fixatures_laminates import *


@pt.fixture
def panel_bottom_01(et_0900_20x, vessel_ex1):
    panel = Panel(
        dim_x=1, dim_y=1, curvature_x=0.1, curvature_y=0.1, laminate=et_0900_20x
    )
    bottom = Bottom(deadrise=20)
    return StructuralElement(
        name="Bottom Panel 01",
        x=5,
        z=-0.3,
        vessel=vessel_ex1,
        model=panel,
        location=bottom,
    )
