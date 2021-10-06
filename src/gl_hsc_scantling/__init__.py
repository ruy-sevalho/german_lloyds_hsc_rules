# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 10:26:35 2020

@author: ruy

Automation of German Lloyd 2012 High Speed Craft strucutural rules calculation
"""

from .vessel import Vessel

from .composites import (
    Fiber,
    Matrix,
    Core_mat,
    Core,
    lamina_factory,
    Lamina,
    laminate_factory,
    Lamina_parts_woven,
    Lamina_parts_csm,
    ABCLaminate,
    SingleSkinLaminate,
    SandwichLaminate,
    Ply,
)
from .elements import StructuralElement
from .panels import Panel
from .locations import (
    Bottom,
    Side,
    Deck,
    WetDeck,
    DeckHouse,
    DeckHouseMainFront,
    DeckHouseMainSide,
    DeckHouseOther,
)
from .stiffeners import Stiffener, LBar
from .constructors import (
    panel_constructor,
    location_constructor,
    stiffener_element_constructor,
    stiffener_section_constructor,
    structural_element_constructor,
)

# from .read_xls import read_xls
# from .to_tex import to_tex
# from .tex import generate_report
# from .session_manager import evaluate, run_xls
