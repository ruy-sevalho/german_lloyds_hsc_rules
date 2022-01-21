# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 15:36:31 2020

@author: ruy

CODE FOR USING German Lloyd 2012 High Speed Craft strucutural rules
# """
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
from dataclass_tools.tools import DESERIALIZER_OPTIONS, DeSerializerOptions

from .common_field_options import NAMED_FIELD_OPTIONS
from .locations import (
    Bottom,
    Deck,
    DeckHouseMainFrontPressure,
    DeckHouseMainSidePressure,
    DeckHouseOtherPressure,
    DeckHousePressure,
    Side,
    WetDeck,
)
from .locations_abc import Location
from .panels import Panel
from .stiffeners import Stiffener
from .structural_model import StructuralModel
from .vessel import Vessel


def _distance(start, end):
    return end - start


MODEL_TYPE_TABLE = {
    Panel.__name__: Panel,
    Stiffener.__name__: Stiffener,
}
MODEL_OPTIONS = DeSerializerOptions(
    add_type=True,
    type_label="element type",
    subtype_table=MODEL_TYPE_TABLE,
    flatten=True,
)

LOCATION_TYPES = [
    Bottom,
    Side,
    WetDeck,
    Deck,
    DeckHousePressure,
    DeckHouseMainFrontPressure,
    DeckHouseMainSidePressure,
    DeckHouseOtherPressure,
]
LOCATION_TYPE_TABLE = {location.name: location for location in LOCATION_TYPES}
LOCATION_OPTIONS = DeSerializerOptions(
    add_type=True,
    type_name=lambda x: x.name,
    subtype_table=LOCATION_TYPE_TABLE,
    flatten=True,
)


VESSEL_OPTIONS = DeSerializerOptions(
    subs_by_attr="name", subs_collection_name="vessels"
)


@dataclass
class StructuralElement:
    """ """

    name: str
    x: float
    z: float
    vessel: Vessel = field(metadata={DESERIALIZER_OPTIONS: VESSEL_OPTIONS})
    model: StructuralModel = field(metadata={DESERIALIZER_OPTIONS: MODEL_OPTIONS})
    location: Location = field(metadata={DESERIALIZER_OPTIONS: LOCATION_OPTIONS})

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
    def pressures(self) -> dict[str, float]:
        return self.location.calc_pressures(self)

    @property
    def design_pressure_type(self):
        return max(self.pressures, key=lambda k: self.pressures[k])

    @property
    def design_pressure(self):
        return self.pressures[self.design_pressure_type]
