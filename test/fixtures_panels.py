"""
 # @ Author: Ruy Sevalho
 # @ Create Time: 2021-08-24 15:34:12
 # @ Description:
 """

import pytest as pt
from gl_hsc_scantling.constructors import panel_element_constructor

from gl_hsc_scantling.shortcut import (
    Panel,
    StructuralElement,
    Bottom,
    Side,
)

from .fixtures_vessel import *
from .fixtures_laminates import *

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


@pt.fixture
def panel_bottom_06(et_0900_20x, vessel_ex1):
    panel = Panel(dim_x=0.1, dim_y=0.1, laminate=et_0900_20x)
    bottom = Bottom(deadrise=5)
    return StructuralElement(
        name="Bottom Panel 06",
        x=6.5,
        z=-0.3,
        vessel=vessel_ex1,
        model=panel,
        location=bottom,
    )


@pt.fixture
def panel_bottom_06_exp():
    return ExpPanel(
        name="Bottom Panel 06", pressures={"impact": 36.2260174353845, "sea": 16.171875}
    )


@pt.fixture
def panel_side_01(et_0900_20x, vessel_ex1):
    panel = Panel(dim_x=1, dim_y=1, laminate=et_0900_20x)
    return StructuralElement(
        name="Side Panel 01",
        x=8,
        z=0.2,
        vessel=vessel_ex1,
        model=panel,
        location=Side(),
    )


@pt.fixture
def panel_side_01_exp():
    return ExpPanel(name="Side Panel 01", pressures={"sea": 17.6875})


@pt.fixture
def panel_wet_deck_01_input():
    return {
        "name": "Wet Deck Panel 02",
        "x": 6.5,
        "z": 0.2,
        "element type": "panel",
        "dim_x": 1,
        "dim_y": 1,
        "laminate": "et_0900_20x",
        "location": "wet deck",
        "deadrise": 16,
        "air_gap": 0.2,
    }


@pt.fixture
def panel_wet_deck_01(vessel_ex1, et_0900_20x, panel_wet_deck_01_input):
    laminates = {et_0900_20x.name: et_0900_20x}
    return panel_element_constructor(vessel_ex1, laminates, **panel_wet_deck_01_input)


@pt.fixture
def panel_wet_deck_01_exp():
    return ExpPanel(
        name="Wet Deck Panel 01",
        pressures={"sea": 14.21875, "impact": 10.2320134062126},
    )


@pt.fixture
def panel_wet_deck_02_input():
    return {
        "name": "Wet Deck Panel 02",
        "x": 7.5,
        "z": 0.2,
        "element type": "panel",
        "dim_x": 1,
        "dim_y": 1,
        "laminate": "et_0900_20x",
        "location": "wet deck",
        "deadrise": 16,
        "air_gap": 0.2,
    }


@pt.fixture
def panel_wet_deck_02(vessel_ex1, et_0900_20x, panel_wet_deck_02_input):
    laminates = {et_0900_20x.name: et_0900_20x}
    return panel_element_constructor(vessel_ex1, laminates, **panel_wet_deck_02_input)


@pt.fixture
def panel_wet_deck_02_exp():
    return ExpPanel(
        name="Wet Deck Panel 02", pressures={"sea": 16.53125, "impact": 12.952671921744}
    )


@pt.fixture
def panel_deck_01_input():
    return {
        "name": "Deck Panel 01",
        "x": 8,
        "z": 0.5,
        "element type": "panel",
        "dim_x": 1,
        "dim_y": 1,
        "laminate": "et_0900_20x",
        "location": "deck",
    }


@pt.fixture
def panel_deck_01(vessel_ex1, et_0900_20x, panel_deck_01_input):
    laminates = {et_0900_20x.name: et_0900_20x}
    return panel_element_constructor(vessel_ex1, laminates, **panel_deck_01_input)


@pt.fixture
def panel_deck_01_exp():
    return ExpPanel(name="Deck Panel 01", pressures={"deck": 6})


@pt.fixture
def panel_deck_02_input():
    return {
        "name": "Deck Panel 02",
        "x": 8,
        "z": 2.5,
        "element type": "panel",
        "dim_x": 1,
        "dim_y": 1,
        "laminate": "et_0900_20x",
        "location": "deck",
    }


@pt.fixture
def panel_deck_02(vessel_ex1, et_0900_20x, panel_deck_02_input):
    laminates = {et_0900_20x.name: et_0900_20x}
    return panel_element_constructor(vessel_ex1, laminates, **panel_deck_02_input)


@pt.fixture
def panel_deck_02_exp():
    return ExpPanel(name="Deck Panel 02", pressures={"deck": 4.5})


@pt.fixture
def panel_deck_03_input():
    return {
        "name": "Deck Panel 03",
        "x": 8,
        "z": 4,
        "element type": "panel",
        "dim_x": 1,
        "dim_y": 1,
        "laminate": "et_0900_20x",
        "location": "deck",
    }


@pt.fixture
def panel_deck_03(vessel_ex1, et_0900_20x, panel_deck_03_input):
    laminates = {et_0900_20x.name: et_0900_20x}
    return panel_element_constructor(vessel_ex1, laminates, **panel_deck_03_input)


@pt.fixture
def panel_deck_03_exp():
    return ExpPanel(name="Deck Panel 03", pressures={"deck": 3})
