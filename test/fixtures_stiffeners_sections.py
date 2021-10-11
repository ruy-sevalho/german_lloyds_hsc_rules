import pytest as pt
from gl_hsc_scantling.shortcut import stiffener_section_constructor, LBar


@pt.fixture
def lbar_01_input():
    return {
        "name": "lbar 01",
        "laminate_web": "et_0900_20x_45deg",
        "dimension_web": 0.05,
        "laminate_flange": "et_0900_20x",
    }
