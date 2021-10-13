import pytest as pt
from gl_hsc_scantling.shortcut import StructuralElement, Stiffener
from .exp_output import ExpStiffenerElement


def _stiffener_check(stiffener: StructuralElement, exp: ExpStiffenerElement):
    assert stiffener.pressures == pt.approx(exp.pressures)


def test_bottom_stiffener_01(stiffener_bottom_01, stiffener_bottom_01_exp):
    _stiffener_check(stiffener_bottom_01, stiffener_bottom_01_exp)
