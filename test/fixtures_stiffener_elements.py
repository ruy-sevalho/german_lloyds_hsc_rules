import pytest as pt
from dataclass_tools.tools import deserialize_dataclass
from gl_hsc_scantling.elements import StructuralElement

from .exp_output import ExpStiffenerElement, ExpStiffenerSection
from .fixtures_laminates import *
from .fixtures_stiffener_sections import *
from .fixtures_vessel import *


@pt.fixture
def stiffener_bottom_01_input():
    return {
        "name": "Bottom Stiffener 01",
        "vessel": "catamaran",
        "x": 8,
        "z": -0.3,
        "element_type": "Stiffener",
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
    vessels = {vessel_ex1.name: vessel_ex1}
    collections = {
        "laminates": laminates,
        "stiffener_sections": stiff_sections,
        "vessels": vessels,
    }
    return deserialize_dataclass(
        dct=stiffener_bottom_01_input,
        dataclass=StructuralElement,
        build_instance=True,
        dict_of_collections=collections,
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
        "vessel": "catamaran",
        "x": 4,
        "z": 0.5,
        "element_type": "Stiffener",
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
    vessels = {vessel_ex1.name: vessel_ex1}
    collections = {
        "laminates": laminates,
        "stiffener_sections": stiff_sections,
        "vessels": vessels,
    }
    return deserialize_dataclass(
        dct=stiffener_side_01_input,
        dataclass=StructuralElement,
        build_instance=True,
        dict_of_collections=collections,
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
