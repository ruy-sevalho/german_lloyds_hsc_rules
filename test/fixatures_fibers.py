"""
 # @ Author: Ruy Sevalho
 # @ Create Time: 2021-08-24 09:14:42
 # @ Description:
 """
import pytest as pt
from gl_hsc_scantling.composites import (
    Fiber,
)


@pt.fixture
def eglass_gl_input():
    """Table C3.8.1 - generica material data"""
    return {
        "name": "e-glass",
        "density": 2540,
        "modulus_x": 73000000,
        "modulus_y": 73000000,
        "modulus_xy": 30000000,
        "poisson": 0.18,
    }


@pt.fixture
def eglass_gl(eglass_gl_input):
    return Fiber(**eglass_gl_input)


@pt.fixture
def sglass_gl_input():
    """Table C3.8.1 - generica material data"""
    return {
        "name": "s-glass",
        "density": 2490,
        "modulus_x": 86000000,
        "modulus_y": 86000000,
        "modulus_xy": 35000000,
        "poisson": 0.21,
    }


@pt.fixture
def sglass_gl(sglass_gl_input):
    return Fiber(**sglass_gl_input)
