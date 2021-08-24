# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 10:37:57 2021

@author: ruy
"""

from collections import OrderedDict
import pytest as pt
import numpy as np
from gl_hsc_scantling.composites import (
    Lamina_parts_woven,
    Matrix,
    Fiber,
    Core,
    Core_mat,
    lamina_factory,
    Lamina,
    SingleSkinLaminate,
    SandwichLaminate,
    Ply,
)
from gl_hsc_scantling.vessel import Vessel
from gl_hsc_scantling.stiffeners import LBar, Stiffener
from .exp_output import ExpPly, ExpLaminate, ExpStiffSection

from .fixatures_vessel import *
from .fixatures_matrices import *
from .fixatures_fibers import *
from .fixatures_laminas import *
from .fixatures_cores import *
from .fixatures_laminates import *
from .fixatures_panels import *


@pt.fixture
def l_bar_input(et_0900_20x_45deg, et_0900_20x):
    return {
        "laminate_web": et_0900_20x_45deg,
        "dimension_web": 0.1,
        "laminate_flange": et_0900_20x,
        "dimension_flange": 0.02,
        "name": "l_bar",
    }


@pt.fixture
def l_bar(l_bar_input):
    return LBar(**l_bar_input)


@pt.fixture
def l_bar_exp():
    return ExpStiffSection("l_bar")
