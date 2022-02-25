# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 10:13:09 2021

@author: ruy
"""
from dataclasses import asdict
import pytest as pt
from gl_hsc_scantling.shortcut import StiffenerSection
from .exp_output import ExpStiffenerSection


def _get_stiffener_stiff_dict(section: StiffenerSection):
    return {
        "bend_stiffness_NA": section.bend_stiff().y,
        "z_NA": section.center().z,
        "web_shear_stiffness": section.shear_stiff,
        "stiffness": section.stiff,
    }


def stiff_section_check(section: StiffenerSection, exp: ExpStiffenerSection):
    assert _get_stiffener_stiff_dict(section) == pt.approx(asdict(exp))


# Comment
def test_lbar_01(lbar_01, lbar_01_exp):
    stiff_section_check(lbar_01, lbar_01_exp)
