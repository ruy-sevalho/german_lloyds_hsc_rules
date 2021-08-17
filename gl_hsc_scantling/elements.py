# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 15:36:31 2020

@author: ruy

CODE FOR USING German Lloyd 2012 High Speed Craft strucutural rules
# """
from enum import Enum

import numpy as np
from marshmallow_dataclass import dataclass

from .pressures import Bottom, Side, WetDeck, Deck
from .vessel import Vessel
from .structural_model import StructuralModel
from .location import Location


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
    location: Location

    @property
    def z_baseline(self):
        return _distance(self.vessel.z_baseline, self.z)

    @property
    def z_waterline(self):
        return self.z - self.vessel.z_waterline

    @property
    def x_pos(self):
        return (self.x - self.vessel.aft_perp) / (
            self.vessel.fwd_perp - self.vessel.aft_perp
        )

    @property
    def pressures(self):
        return self.location.calc_pressures(self)

    @property
    def design_pressure_type(self):
        return max(self.pressures, key=lambda k: self.pressures[k])

    @property
    def design_pressure(self):
        return self.pressures[self.design_pressure_type]
