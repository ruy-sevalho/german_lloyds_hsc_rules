# -*- coding: utf-8 -*-
"""
Created on Wed May 26 18:16:39 2021

@author: ruy
"""
import pytest

def test_vessel_ex1_vert_acg(vessel_ex1):
    assert vessel_ex1.vert_acg == pytest.approx(1.)
    # assert vessel_ex1.trans_bend_moment == pytest.approx(1.)
