# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 10:21:16 2021

@author: ruy
"""
from collections import namedtuple
from .vessel import Vessel
from .stiffeners import Stiffener, stiff_section_factory
from .panels import Panel
from .composites import (
    Fiber,
    Matrix,
    Core_mat,
    Core,
    lamina_factory,
    LaminaMonolith,
    laminate_factory,
    LaminaPartsWoven,
    LaminaPartsCSM,
    SingleSkinLaminate,
    SandwichLaminate,
    Ply,
)
from .read_xls import read_xls
from .session import Session

# Session = namedtuple(
#     'Session',
#     ['vessel',
#      'fibers',
#      'matrices',
#      'cores_mat_data',
#      'plies_mat',
#      'laminates',
#      'stiff_sections',
#      'panels',
#      'stiff_elements',
#      ])


def evaluate(data, **kwargs):
    """Main routine"""

    vessel = Vessel(**data.vessel)
    fibers = {row["name"]: Fiber(**row) for row in data.fibers}
    matrices = {row["name"]: Matrix(**row) for row in data.matrices}
    cores_mat = {row["name"]: Core_mat(**row) for row in data.cores_mat}
    cores = {
        row["name"]: Core(core_material=cores_mat[row.pop("core_material")], **row)
        for row in data.cores
    }
    plies_mat = {
        row["name"]: lamina_factory(fibers, matrices, **row)
        for row in data.plies_composed
    }
    plies_mat.update(
        {row["name"]: LaminaMonolith(**row) for row in data.plies_monolith}
    )

    laminates = {
        row["name"]: SingleSkinLaminate(
            [
                Ply(
                    plies_mat[ply_input["material"]],
                    ply_input["orientation"],
                )
                for ply_input in row["plies_unpositioned"]
            ],
            name=row["name"],
        )
        for row in data.single_skin_laminates
    }
    laminates.update(
        {
            row["name"]: SandwichLaminate(
                laminates[row["outter_laminate"]],
                laminates[row["inner_laminate"]],
                cores[row["core"]],
            )
            for row in data.sandwhich_laminates
        }
    )
    panels = {
        row["name"]: Panel(
            vessel=vessel, laminate=laminates[row.pop("laminate")], **row
        )
        for row in data.panels
    }
    stiff_sections = {
        row["name"]: stiff_section_factory(row.pop("section_type"), laminates, **row)
        for row in data.stiff_sections
    }

    stiff_elements = {
        row["name"]: Stiffener(
            vessel=vessel,
            stiff_section=stiff_sections[row.pop("stiff_section_type")],
            laminates=laminates,
            **row
        )
        for row in data.stiff_elements
    }
    session = {
        "name": "session",
        "vessel": vessel,
        "fibers": fibers,
        "matrices": matrices,
        "cores_mat": cores_mat,
        "cores": cores,
        "plies_mat": plies_mat,
        "laminates": laminates,
        "panels": panels,
        "stiff_sections": stiff_sections,
        "stiff_elements": stiff_elements,
    }
    session = Session(**session)
    return session


def run_xls(input_file):
    data = read_xls(input_file)
    session = Session(name=input_file, data=data)
    return data, session
