# -*- coding: utf-8 -*-
"""
Created on Wed May 26 18:16:39 2021

@author: ruy
"""
from dataclasses import asdict
import pytest as pt
from gl_hsc_scantling.vessel import Monohull, Catamaran

from .exp_output import ExpCatamaran, ExpVessel

def vessel_general_param(vessel: Monohull | Catamaran):
    vert_acg = vessel.vert_acg
    max_wave_height = vessel.max_wave_height
    sig_wave_height = vessel.sig_wave_height
    return {  
            "vert_acg": vert_acg,
            "max_wave_height": max_wave_height,
            "sig_wave_height": sig_wave_height,    
    }


def catamataran_results(catamaran: Catamaran):
    results = vessel_general_param(catamaran)
    transverse_bending_moment = catamaran.transverse_bending_moment
    transverse_shear_force = catamaran.transverse_shear_force
    transverse_torsional_moment = catamaran.transverse_torsional_moment
    cat_loads = {
            "transverse_bending_moment": transverse_bending_moment,
            "transverse_shear_force": transverse_shear_force,
            "transverse_torsional_moment": transverse_torsional_moment
    }
    results.update(cat_loads)
    return results
    
def test_vessel_ex1(vessel_ex1: Catamaran, vessel_ex1_expected: ExpCatamaran):
    """Global loads check."""    
    assert catamataran_results(vessel_ex1) == pt.approx(vessel_ex1_expected.to_dict())
   