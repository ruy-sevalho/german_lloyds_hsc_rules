"""
 # @ Author: Ruy Sevalho
 # @ Create Time: 2021-08-24 09:11:42
 # @ Description:
 """
import pytest as pt
from gl_hsc_scantling.composites import (
    Matrix,
)


@pt.fixture
def polyester_gl_input():
    """Table C3.8.1 - generica material data"""
    return {
        "name": "polyester",
        "density": 1200,
        "modulus_x": 3000000,
        "modulus_xy": 1140000,
        "poisson": 0.316,
    }


@pt.fixture
def polyester_gl(polyester_gl_input):
    return Matrix(**polyester_gl_input)


@pt.fixture
def epoxy_gl_input():
    """Table C3.8.1 - generica material data"""
    return {
        "name": "epoxy",
        "density": 1200,
        "modulus_x": 3600000,
        "modulus_xy": 1330000,
        "poisson": 0.35,
    }


@pt.fixture
def epoxy_gl(epoxy_gl_input):
    return Matrix(**epoxy_gl_input)
