import pytest as pt
from dataclass_tools.tools import deserialize_dataclass
from gl_hsc_scantling.composites import Laminate
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


@pt.fixture
def ibar_01_input():
    return {
        "name": "ibar_01",
        "section_profile": "FlatBar",
        "laminate_web": "sandwich_laminate",
        "dimension_web": 0.05,
    }


@pt.fixture
def ibar_01(ibar_01_input, sandwich_laminate):
    collections = {"laminates": {lam.name: lam for lam in [sandwich_laminate]}}
    return deserialize_dataclass(
        dct=ibar_01_input,
        dataclass=StiffenerSectionWithFoot,
        dict_of_collections=collections,
        build_instance=True,
    )


@pt.fixture
def ibar_01_exp():
    return ExpStiffenerSection(
        bend_stiffness_NA=1.27041893193391,
        z_NA=0.025,
        web_shear_stiffness=1032.840114,
        stiffness=6098.01087328276,
    )


@pt.fixture
def top_hat_01_input():
    return {
        "name": "top_hat_01",
        "section_profile": "TopHat",
        "laminate_web": "et_0900_20x_45deg",
        "dimension_web": 0.05,
        "laminate_flange": "et_0900_20x",
        "dimension_flange": 0.02,
    }


@pt.fixture
def top_hat_01(top_hat_01_input, et_0900_20x: Laminate, et_0900_20x_45deg: Laminate):
    collections = {
        "laminates": {lam.name: lam for lam in [et_0900_20x, et_0900_20x_45deg]}
    }
    return deserialize_dataclass(
        dct=top_hat_01_input,
        dataclass=StiffenerSectionWithFoot,
        dict_of_collections=collections,
        build_instance=True,
    )


@pt.fixture
def top_hat_01_exp():
    return ExpStiffenerSection(
        bend_stiffness_NA=2.65457026598937,
        z_NA=0.0325617870280859,
        web_shear_stiffness=5414.5281461439,
        stiffness=8843.54658132216,
    )
