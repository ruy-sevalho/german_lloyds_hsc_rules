"""
 # @ Author: Ruy Sevalho
 # @ Create Time: 2021-08-24 08:59:25
 # @ Description:
 """
import pytest as pt
from gl_hsc_scantling.vessel import Monohull, Catamaran
from .exp_output import ExpVessel, ExpCatamaran, ExpCatamaranGlobalLoads


@pt.fixture
def vessel_input_ex1():
    """Test vessel 01"""
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
        "lcg": 4,
        "deadrise_lcg": 12,
        "dist_hull_cl": 4.6,
    }


@pt.fixture
def vessel_ex1(vessel_input_ex1) -> Catamaran:
    return Catamaran(**vessel_input_ex1)


@pt.fixture
def vessel_ex1_expected():
    exp_vessel = ExpVessel(
        **{
            "vert_acg": 1,
            "max_wave_height": 1.424449396,
            "sig_wave_height": 0.407531163657313,
        }
    )
    exp_cat_loads = ExpCatamaranGlobalLoads(
        **{
            "transverse_bending_moment": 54.1512,
            "transverse_shear_force": 14.715,
            "transverse_torsional_moment": 73.575,
        }
    )

    return ExpCatamaran(general_param=exp_vessel, cat_loads=exp_cat_loads)
