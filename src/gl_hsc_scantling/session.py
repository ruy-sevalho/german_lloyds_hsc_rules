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
    LaminaMonolith,
    LaminaPartsWoven,
    LaminaPartsCSM,
    lamina_factory,
    Core_mat,
    Core,
    Ply,
    SingleSkinLaminate,
    SandwichLaminate,
)

from .panels import Panel
from .stiffeners import StiffinerSection, Stiffener, stiff_section_factory


@dataclass
class InputDict:
    """Class for managing input data for a session"""

    name: str
    vessel: Optional[Vessel] = field(default=...)
    fibers: Dict[str, Fiber] = field(default_factory=dict)
    matrices: Dict[str, Matrix] = field(default_factory=dict)
    cores_mat: Dict[str, Core_mat] = field(default_factory=dict)
    cores: Dict[str, Core] = field(default_factory=dict)
    plies_composed: Dict[str, Union[LaminaPartsCSM, LaminaPartsWoven]] = field(
        default_factory=dict
    )
    plies_monolith: Dict[str, LaminaMonolith] = field(default_factory=dict)
    single_skin_laminates: Dict[str, SingleSkinLaminate] = field(default_factory=dict)
    sandwhich_laminates: Dict[str, SandwichLaminate] = field(default_factory=dict)
    panels: Dict[str, Panel] = field(default_factory=dict)
    stiff_sections: Dict[str, StiffinerSection] = field(default_factory=dict)
    stiff_elements: Dict[str, Stiffener] = field(default_factory=dict)


@dataclass
class Session:
    """Class for managing a project session analysis"""

    name: str = "Unamed Session"
    vessel: Optional[Vessel] = field(default=...)
    fibers: Dict[str, Fiber] = field(default_factory=dict)
    matrices: Dict[str, Matrix] = field(default_factory=dict)
    cores_mat: Dict[str, Core_mat] = field(default_factory=dict)
    cores: Dict[str, Core] = field(default_factory=dict)
    plies_composed: Dict[str, Union[LaminaPartsCSM, LaminaPartsWoven]] = field(
        default_factory=dict
    )
    plies_monolith: Dict[str, LaminaMonolith] = field(default_factory=dict)
    single_skin_laminates: Dict[str, SingleSkinLaminate] = field(default_factory=dict)
    sandwhich_laminates: Dict[str, SandwichLaminate] = field(default_factory=dict)
    panels: Dict[str, Panel] = field(default_factory=dict)
    stiff_sections: Dict[str, StiffinerSection] = field(default_factory=dict)
    stiff_elements: Dict[str, Stiffener] = field(default_factory=dict)
    data: InitVar[dict] = None

    @property
    def plies_mat(self):
        return {**self.plies_composed, **self.plies_monolith}

    @property
    def laminates(self):
        return {**self.single_skin_laminates, **self.sandwhich_laminates}

    def __post_init__(self, data):
        if data:
            self._load_session(data)

    def _load_session(self, data):
        self.vessel = Vessel(**data.vessel)
        self.fibers = {row["name"]: Fiber(**row) for row in data.fibers}
        self.matrices = {row["name"]: Matrix(**row) for row in data.matrices}
        self.cores_mat = {row["name"]: Core_mat(**row) for row in data.cores_mat}
        self.cores = {
            row["name"]: Core(
                core_material=self.cores_mat[row.pop("core_material")], **row
            )
            for row in data.cores
        }
        self.plies_composed = {
            row["name"]: lamina_factory(self.fibers, self.matrices, **row)
            for row in data.plies_composed
        }
        self.plies_monolith = {
            row["name"]: LaminaMonolith(**row) for row in data.plies_monolith
        }
        self.single_skin_laminates = {
            row["name"]: SingleSkinLaminate(
                [
                    Ply(
                        self.plies_mat[ply_input["material"]],
                        ply_input["orientation"],
                    )
                    for ply_input in row["plies_unpositioned"]
                ],
                name=row["name"],
            )
            for row in data.single_skin_laminates
        }
        self.sandwhich_laminates = {
            row["name"]: SandwichLaminate(
                self.laminates[row["outter_laminate"]],
                self.laminates[row["inner_laminate"]],
                self.cores[row["core"]],
            )
            for row in data.sandwhich_laminates
        }
        self.panels = {
            row["name"]: Panel(
                vessel=self.vessel, laminate=self.laminates[row.pop("laminate")], **row
            )
            for row in data.panels
        }
        self.stiff_sections = {
            row["name"]: stiff_section_factory(
                row.pop("section_type"), self.laminates, **row
            )
            for row in data.stiff_sections
        }

        self.stiff_elements = {
            row["name"]: Stiffener(
                vessel=self.vessel,
                stiff_section=self.stiff_sections[row.pop("stiff_section_type")],
                laminates=self.laminates,
                **row
            )
            for row in data.stiff_elements
        }
