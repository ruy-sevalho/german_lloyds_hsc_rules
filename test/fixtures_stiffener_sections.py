import pytest as pt
from dataclass_tools.tools import deserialize_dataclass
from gl_hsc_scantling.stiffeners import StiffenerSectionWithFoot

from .exp_output import ExpStiffenerSection
from .fixtures_laminates import *


# Comment
@pt.fixture
def lbar_01_input():
    return {
        "name": "lbar_01",
        "section_profile": "LBar",
        "laminate_web": "et_0900_20x_45deg",
        "dimension_web": 0.05,
        "laminate_flange": "et_0900_20x",
        "dimension_flange": 0.02,
    }


@pt.fixture
def lbar_01(lbar_01_input, et_0900_20x, et_0900_20x_45deg):
    collections = {
        "laminates": {lam.name: lam for lam in [et_0900_20x, et_0900_20x_45deg]}
    }
    return deserialize_dataclass(
        dct=lbar_01_input,
        dataclass=StiffenerSectionWithFoot,
        dict_of_collections=collections,
        build_instance=True,
    )


@pt.fixture
def lbar_01_exp():
    return ExpStiffenerSection(
        bend_stiffness_NA=1.70253506207197,
        z_NA=0.0368412726626162,
        web_shear_stiffness=2707.26407307194,
        stiffness=5647.45173312655,
    )
