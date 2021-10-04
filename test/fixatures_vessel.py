"""
 # @ Author: Ruy Sevalho
 # @ Create Time: 2021-08-24 08:59:25
 # @ Description:
 """
import pytest as pt
from gl_hsc_scantling.vessel import Vessel


@pt.fixture
def vessel_input_ex1():
    return {
        "name": "catamaran",
        "service_range": "USR",
        "type_of_service": "PASSENGER",
        "speed": 15,
        "displacement": 6,
        "length": 10,
        "beam": 6.5,
        "fwd_perp": 10,
        "aft_perp": 0,
        "draft": 0.51,
        "z_baseline": -0.51,
        "block_coef": 0.4,
        "water_plane_area": 10,
        "lcg": 6,
        "deadrise_lcg": 12,
        "dist_hull_cl": 4.6,
    }


@pt.fixture
def vessel_ex1(vessel_input_ex1):
    return Vessel(**vessel_input_ex1)
