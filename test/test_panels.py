"""
 # @ Author: Ruy Sevalho
 # @ Create Time: 2021-08-24 15:31:46
 # @ Description:
 """

import pytest as pt

from gl_hsc_scantling import Panel, StructuralElement, Bottom, Side, WetDeck

from .exp_output import ExpPanel


def panel_pressure_check(panel: StructuralElement, exp: ExpPanel):
    for p_type, p_value in exp.pressures.items():
        assert panel.pressures[p_type] == pt.approx(p_value)


def test_panel_bottom_01(panel_bottom_01, panel_bottom_01_exp):
    panel_pressure_check(panel_bottom_01, panel_bottom_01_exp)


def test_panel_bottom_02(panel_bottom_02, panel_bottom_02_exp):
    panel_pressure_check(panel_bottom_02, panel_bottom_02_exp)


def test_panel_bottom_03(panel_bottom_03, panel_bottom_03_exp):
    panel_pressure_check(panel_bottom_03, panel_bottom_03_exp)


def test_panel_bottom_04(panel_bottom_04, panel_bottom_04_exp):
    panel_pressure_check(panel_bottom_04, panel_bottom_04_exp)


def test_panel_bottom_05(panel_bottom_05, panel_bottom_05_exp):
    panel_pressure_check(panel_bottom_05, panel_bottom_05_exp)


def test_panel_bottom_06(panel_bottom_06, panel_bottom_06_exp):
    panel_pressure_check(panel_bottom_06, panel_bottom_06_exp)


def test_panel_side_01(panel_side_01, panel_side_01_exp):
    panel_pressure_check(panel_side_01, panel_side_01_exp)
