# -*- coding: utf-8 -*-
"""
Created on Wed May 26 18:16:39 2021

@author: ruy
"""
import pytest as pt
from gl_hsc_scantling.vessel import Vessel

from .exp_output import ExpVessel


def test_vessel_ex1(vessel_ex1: Vessel, vessel_ex1_expected: ExpVessel):
    """Global loads check."""
    assert vessel_ex1.vert_acg == pt.approx(vessel_ex1_expected.vert_acg)
    assert vessel_ex1.max_wave_height == pt.approx(vessel_ex1_expected.max_wave_height)
    assert vessel_ex1.sig_wave_height == pt.approx(vessel_ex1_expected.sig_wave_height)
    assert vessel_ex1.transverse_bending_moment == pt.approx(
        vessel_ex1_expected.transverse_bending_moment
    )
    assert vessel_ex1.transverse_shear_force == pt.approx(
        vessel_ex1_expected.transverse_shear_force
    )
    assert vessel_ex1.transverse_torsional_moment == pt.approx(
        vessel_ex1_expected.transverse_torsional_moment
    )
