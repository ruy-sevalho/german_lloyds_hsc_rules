# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 14:59:59 2021

@author: ruy
"""
from typing import Optional, List, Dict, Union
from dataclasses import dataclass, field, InitVar
from .vessel import Vessel

from .composites import (
    Fiber,
    Matrix,
    Lamina,
    Lamina_parts_woven,
    Lamina_parts_csm,
    Core_mat,
    Core,
    SingleSkinLaminate,
    SandwichLaminate,
)

from .panels import Panel
from .stiffeners import StiffinerSection, Stiffener


@dataclass
class Input:
    """Class for managing input data for a session"""

    name: str
    vessel: Optional[Vessel] = field(default=...)
    fibers: Dict[str, Fiber] = field(default_factory=dict)
    matrices: Dict[str, Matrix] = field(default_factory=dict)
    cores_mat: Dict[str, Core_mat] = field(default_factory=dict)
    cores: Dict[str, Core] = field(default_factory=dict)
    plies_composed: Dict[str, Union[Lamina_parts_csm, Lamina_parts_woven]] = field(
        default_factory=dict
    )
    plies_monolith: Dict[str, Lamina] = field(default_factory=dict)
    single_skin_laminates: Dict[str, SingleSkinLaminate] = field(default_factory=dict)
    sandwhich_laminates: Dict[str, SandwichLaminate] = field(default_factory=dict)
    panels: Dict[str, Panel] = field(default_factory=dict)
    stiff_sections: Dict[str, StiffinerSection] = field(default_factory=dict)
    stiff_elements: Dict[str, Stiffener] = field(default_factory=dict)


@dataclass
class Session:
    """Class for managing a project session complete analysis"""

    name: str = "Unamed Session"
    vessel: Optional[Vessel] = field(default=...)
    fibers: Dict[str, Fiber] = field(default_factory=dict)
    matrices: Dict[str, Matrix] = field(default_factory=dict)
    cores_mat: Dict[str, Core_mat] = field(default_factory=dict)
    cores: Dict[str, Core] = field(default_factory=dict)
    plies_composed: Dict[str, Union[Lamina_parts_csm, Lamina_parts_woven]] = field(
        default_factory=dict
    )
    plies_monolith: Dict[str, Lamina] = field(default_factory=dict)
    single_skin_laminates: Dict[str, SingleSkinLaminate] = field(default_factory=dict)
    sandwhich_laminates: Dict[str, SandwichLaminate] = field(default_factory=dict)
    panels: Dict[str, Panel] = field(default_factory=dict)
    stiff_sections: Dict[str, StiffinerSection] = field(default_factory=dict)
    stiff_elements: Dict[str, Stiffener] = field(default_factory=dict)
    load_input: InitVar[dict] = None

    @property
    def plies_mat(self):
        return {**self.plies_composed, **self.plies_monolith}

    @property
    def laminates(self):
        return {**self.single_skin_laminates, **self.sandwhich_laminates}

    def __post_init__(self, load_input):
        if load_input:
            print("loading")
    
    def _load_session(self, ):
        self.vessel = Vessel(**)
