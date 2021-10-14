import pytest as pt
from gl_hsc_scantling.shortcut import StructuralElement, Stiffener
from .exp_output import ExpStiffenerElement
from .test_stiffeners_sections import stiff_section_check


def stiffener_check(stiffener: StructuralElement, exp: ExpStiffenerElement):
    assert stiffener.pressures == pt.approx(exp.pressures)
    stiff_section_check(stiffener.model.stiff_section_att_plate, exp.stiffener_section)


def test_bottom_stiffener_01(stiffener_bottom_01, stiffener_bottom_01_exp):
    stiffener_check(stiffener_bottom_01, stiffener_bottom_01_exp)
