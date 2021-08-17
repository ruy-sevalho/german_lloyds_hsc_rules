# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 16:53:39 2021

@author: ruy
"""

from enum import Enum

import numpy as np
from marshmallow_dataclass import dataclass

from .pressures import Bottom, Side, WetDeck, Deck
from .vessel import Vessel
from .structural_model import StructuralModel


def _distance(start, end):
    return end - start


@dataclass
class StructuralElement:
    """ """

    name: str
    x: float
    z: float
    vessel: Vessel
    model: StructuralModel
    location: "location"
