# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 10:13:09 2021

@author: ruy
"""
import pytest as pt


def stiff_section_check(section, exp):
    assert section.name == exp.name

def test_l_bar(l_bar, l_bar_exp):
    stiff_section_check(l_bar, l_bar_exp)