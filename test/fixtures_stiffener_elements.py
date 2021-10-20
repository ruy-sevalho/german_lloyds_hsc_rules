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
        "element_type": "stiffener",
        "span": 1,
        "spacing_1": 0.4,
        "spacing_2": 0.4,
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
            bend_stiffness_NA=8.33124543714909,
            z_NA=0.0115411623450635,
            web_shear_stiffness=2707.26407307195,
            stiffness=23856.1306743935,
        ),
        pressures={"sea": 18.46875, "impact": 21.3672413793103},
    )


@pt.fixture
def stiffener_side_01_input():
    return {
        "name": "Side Stiffener 01",
        "x": 4,
        "z": 0.5,
        "element_type": "stiffener",
        "span": 1,
        "spacing_1": 0.4,
        "spacing_2": 0.4,
        "stiff_att_plate": 1,
        "stiff_att_angle": 20,
        "att_plate_1": "et_0900_20x",
        "att_plate_2": "et_0900_20x",
        "stiff_section": "lbar_01",
        "location": "side",
    }


@pt.fixture
def stiffener_side_01(et_0900_20x, lbar_01, vessel_ex1, stiffener_side_01_input):
    laminates = {et_0900_20x.name: et_0900_20x}
    stiff_sections = {lbar_01.name: lbar_01}
    return stiffener_element_constructor(
        vessel_ex1, laminates, stiff_sections, **stiffener_side_01_input
    )


@pt.fixture
def stiffener_side_01_exp():
    return ExpStiffenerElement(
        stiffener_section=ExpStiffenerSection(
            bend_stiffness_NA=7.98195791502877,
            z_NA=0.0112865125011699,
            web_shear_stiffness=2707.26407307195,
            stiffness=23856.1306743935,
        ),
        pressures={"sea": 10},
    )
