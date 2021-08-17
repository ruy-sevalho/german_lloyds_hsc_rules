# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 10:29:20 2021

@author: ruy
"""

from abc import ABC
from enum import Enum


class BoundaryCondition(str, Enum):
    FIXED = "FIXED"
    SIMPLY_SUPPORTED = "SIMPLY_SUPPORTED"


class StructuralModel(ABC):
    span: float
    spacing: float
