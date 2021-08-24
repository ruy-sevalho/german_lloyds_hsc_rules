"""
 # @ Author: Ruy Sevalho
 # @ Create Time: 2021-08-24 15:31:46
 # @ Description:
 """

import pytest as pt

from gl_hsc_scantling import Panel, StructuralElement, Bottom, Side, WetDeck


def test_panel_bottom_01(panel_bottom_01):
    assert panel_bottom_01.name == "Bottom Panel 01"
