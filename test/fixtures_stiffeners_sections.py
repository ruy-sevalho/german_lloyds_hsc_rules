import pytest as pt
from gl_hsc_scantling.shortcut import stiffener_section_constructor, LBar
from .fixtures_laminates import *
from .exp_output import ExpStiffenerSection


@pt.fixture
def lbar_01_input():
    return {
        "name": "lbar 01",
        "section_profile": "lbar",
        "laminate_web": "et_0900_20x_45deg",
        "dimension_web": 0.05,
        "laminate_flange": "et_0900_20x",
        "dimension_flange": 0.02,
    }


@pt.fixture
def lbar_01(lbar_01_input, et_0900_20x, et_0900_20x_45deg):
    laminates = {lam.name: lam for lam in [et_0900_20x, et_0900_20x_45deg]}
    return stiffener_section_constructor(laminates=laminates, **lbar_01_input)


@pt.fixture
def lbar_01_exp():
    return ExpStiffenerSection(
        bend_stiffness_NA=1.70253506207197,
        z_NA=0.0368412726626162,
        web_shear_stiffness=2707.26407307194,
    )
