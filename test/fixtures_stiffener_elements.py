import pytest as pt
from gl_hsc_scantling.shortcut import stiffener_element_constructor, Stiffener
from .fixtures_stiffener_sections import *
from .fixtures_laminates import *
from .fixtures_vessel import *
from .exp_output import ExpStiffenerElement, ExpStiffenerSection


@pt.fixture
def stiffener_bottom_01_input():
    return {
        "name": "Bottom Stiffener 01",
        "x": 8,
        "z": -0.3,
        "element type": "panel",
        "span": 1,
        "spacing_1": 1,
        "spacing_2": 1,
        "stiff_att_plate": 1,
        "att_plate_1": "et_0900_20x",
        "att_plate_2": "et_0900_20x",
        "stiff_section": "lbar_01",
        "location": "bottom",
        "deadrise": 16,
    }


@pt.fixture
def stiffener_bottom_01(et_0900_20x, lbar_01, vessel_ex1, stiffener_bottom_01_input):
    laminates = {et_0900_20x.name: et_0900_20x}
    stiff_sections = {lbar_01.name: lbar_01}
    return stiffener_element_constructor(
        vessel_ex1, laminates, stiff_sections, **stiffener_bottom_01_input
    )


@pt.fixture
def stiffener_bottom_01_exp():
    return ExpStiffenerElement(
        stiffener_section=ExpStiffenerSection(
            bend_stiffness_NA=0, z_NA=0, web_shear_stiffness=0, stiffness=0
        ),
        pressures={"sea": 18.46875, "impact": 21.3672413793103},
    )
