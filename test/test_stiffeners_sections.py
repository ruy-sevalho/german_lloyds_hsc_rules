# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 10:13:09 2021

@author: ruy
"""
import pytest as pt
from gl_hsc_scantling.shortcut import StiffenerSection
from .exp_output import ExpStiffenerSection


def stiff_section_check(section: StiffenerSection, exp: ExpStiffenerSection):
    assert section.bend_stiff().y == pt.approx(exp.bend_stiffness_NA)
    assert section.center().z == pt.approx(exp.z_NA)
    assert section.shear_stiff == pt.approx(exp.web_shear_stiffness)
    assert section.stiff == pt.approx(exp.stiffness)


# Comment
def test_lbar_01(lbar_01, lbar_01_exp):
    stiff_section_check(lbar_01, lbar_01_exp)
