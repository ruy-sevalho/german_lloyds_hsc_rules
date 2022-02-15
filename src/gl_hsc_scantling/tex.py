# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 12:53:01 2021

@author: ruy
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from itertools import chain
from math import ceil, floor
from typing import TYPE_CHECKING, Optional, Union

import quantities as pq
from dataclass_tools.tools import PrintWrapper, serialize_dataclass
import pylatex
from pylatex import (
    Document,
    MiniPage,
    NoEscape,
    Quantity,
    Section,
    Subsection,
    Subsubsection,
    Table,
    Tabular,
    Package,
    NewPage,
)
from pylatex.base_classes import Environment, CommandBase
from pylatex.labelref import Label
from pylatex.math import Math
from pylatex.utils import bold
from gl_hsc_scantling.elements import LOCATION_TYPES
from gl_hsc_scantling.locations_abc import Location
from gl_hsc_scantling.report_config import PrintOptions, ReportConfig

from gl_hsc_scantling.stiffeners import StiffenerSectionWithFoot

from .abrevitation_registry import abv_registry
from .composites import (
    LaminaMonolith,
    LaminaParts,
    Laminate,
    PlyStack,
    SandwichLaminate,
    SingleSkinLaminate,
)

if TYPE_CHECKING:
    from .session import Session


INPUT = "Input"
VESSEL_SECTION_TITLE = "Vessels"
VESSEL_INPUT_CAPTION = "Vessel parameters"
VESSEL_LOADS_CAPTION = "Vessel global loads"
MATERIALS_SECTION_TITLE = "Materials"
CONSTITUENT_MATERIASL_SECTION_TITLE = "Constituent materials"
LAMINAS_SECTION_TITLE = "Laminas"
LAMINATES_SECTION_TITLE = "Laminates"
FIBER_CAPTION = "Fibers"
MATRIX_CAPTION = "Matrices"
LAMINATE_COMPOSED_CAPTION = "Laminates - properties calculated from fiber and matix"
CAPTIONS_VESSEL = [VESSEL_INPUT_CAPTION, VESSEL_LOADS_CAPTION]
LAMINA_MONLITH_CAPTION = "Laminas"
LAMINA_PARTS_CAPTION = "Laminas - definied by fiber and matirx combination"
SINGLE_SKIN_DEFINITION_TABLE_CAPTION = "single skin laminate"
SANDWICH_LAMINATE_ARGUMENTS_TABLE_CAPTION = "core and symmetry otpions"
CORES_SUB_SECTION_TITLE = "Cores"
CORE_MATERIAL_TABLE_CAPTION = "Core materials"
OUTTER_SKIN_CATPION = "outter skin"
INNER_SKIN_CATPION = "inner skin"
STIFFENER_PROFILES_SECTION_TITLE = "Stiffener sections"
STIFFENER_SECTION_DEFINITION_CAPTION = "stiffener section"
PANELS_SECTION_TITLE = "Panels"
STIFFENERS_SECTION_TITLE = "Stiffeners"
INPUTS_TITLE = "Inputs"
PLY_STACK_LIST = "ply stack list"
PLY_STACK_OPTIONS = "ply stack options"
RULE_CHECK_RESULT_CAPTION = "Results"

pylatex.quantities.UNIT_NAME_TRANSLATIONS.update(
    {"nautical_miles_per_hour": "kt", "arcdegree": "degree", "p": "pascal"}
)

kN = pq.UnitQuantity("kiloNewton", pq.N * 1e3, symbol="kN")


class Center(Environment):
    pass


class Landscape(Environment):
    pass


class TableOfContents(CommandBase):
    pass


class ListOfTables(CommandBase):
    pass


def _print_quantity(
    quantity: pq.Quantity,
    disp_units=False,
    convert_units=None,
    round_precision=2,
):
    options = {"round-precision": round_precision}
    if convert_units is not None:
        quantity = quantity.rescale(convert_units)
    if not disp_units and not quantity.units == pq.percent:
        quantity = quantity.magnitude
    return Quantity(quantity, options=options)


def _print_type(
    value,
    disp_units=False,
    convert_units=None,
    round_precision=2,
):
    if isinstance(value, pq.Quantity):
        value = _print_quantity(
            value,
            disp_units=disp_units,
            convert_units=convert_units,
            round_precision=round_precision,
        )
    return value


def _get_unit(
    value: Union[str, pq.Quantity],
    convert_units: Optional[str] = None,
):
    if isinstance(value, str) or isinstance(value, bool):
        return ""
    if value.units == pq.dimensionless or value.units == pq.percent:
        return ""
    if convert_units is not None:
        value = value.rescale(convert_units)
    unit_string = Quantity(value.units).dumps()
    unit_string = unit_string[:4] + unit_string[7:]
    return NoEscape(" " + "(" + unit_string + ")")


def _single_entity_dict_to_table_list(
    inp: dict[str, PrintWrapper],
    options_dict: dict[str, PrintOptions] = dict(),
):
    """Creates a table (list of lists) for display data of a single entity, with a name: value pair in each row."""
    return [
        [
            printable.names.abreviation,
            _print_type(
                printable.value,
                disp_units=True,
                # why I would ever do this to myself is beyond me, but hey here we are
                **dict(
                    filter(
                        lambda item: item[0] in ["convert_units", "round_precision"],
                        asdict(options_dict.get(key, PrintOptions())).items(),
                    )
                ),
            ),
        ]
        for key, printable in inp.items()
    ]


# Selection of attributes and properties to print are made by each object, which
# wraps the results as property that returns a dict
def _list_of_entities_dicts_to_table_list(
    entities: list[dict[str, PrintWrapper]],
    header: bool = False,
    split_units: bool = False,
    options_dict: dict[str, PrintOptions] = dict(),
):
    """Creates a table(lists of lists)"""
    table = [
        [
            _print_type(
                printable.value,
                # Turned out once wasn't enough
                **dict(
                    filter(
                        lambda item: item[0] in ["convert_units", "round_precision"],
                        asdict(options_dict.get(key, PrintOptions())).items(),
                    )
                ),
            )
            for key, printable in entity.items()
        ]
        for entity in entities
    ]
    if header:
        entity = entities[0]
        if split_units:
            header = [
                [
                    NoEscape(printable.names.abreviation)
                    for key, printable in entity.items()
                ],
                [
                    _get_unit(
                        printable.value,
                        convert_units=options_dict.get(
                            key, PrintOptions()
                        ).convert_units,
                    )
                    for key, printable in entity.items()
                ],
            ]
        else:
            header = [
                [
                    NoEscape(printable.names.abreviation)
                    + _get_unit(
                        printable.value,
                        convert_units=options_dict.get(
                            key, PrintOptions()
                        ).convert_units,
                    )
                    for key, printable in entity.items()
                ]
            ]
        table = header + table
    return table


def _cols_repeat(cols_step, n):
    cols_step = NoEscape(cols_step)
    cols = cols_step
    for _ in range(int(n - 1)):
        cols = NoEscape(cols + NoEscape(r" | ") + cols_step)
    return cols


def _build_cols(table_array):
    return "l" + " c" * (len(table_array[0]) - 1)


def _split_array(table_array, n):
    index = ceil(len(table_array) / n)
    if index * (n - 1) == len(table_array):
        n = n - 1
    split_arrays = [table_array[i * index : (i + 1) * index] for i in range(n)]
    new_array = [
        list(
            chain(
                *[
                    split_array[i]
                    if i < len(split_array)
                    else [""] * len(split_array[0])
                    for split_array in split_arrays
                ]
            )
        )
        for i in range(index)
    ]
    return new_array, n


def _add_tabular(table_array, cols=None, horizontal_lines=None, split=None):
    if cols is None:
        cols = _build_cols(table_array)
    if split:
        table_array, n = _split_array(table_array, split)
        cols = _cols_repeat(cols, n)
    if horizontal_lines is None:
        horizontal_lines = []
    tabular = Tabular(cols)
    for i, row in enumerate(table_array):
        tabular.add_row(row)
        if i in horizontal_lines:
            tabular.add_hline()
    return tabular


def _add_table(
    table_array,
    cols=None,
    header=None,
    caption=None,
    label=None,
    split=False,
    horizontal_lines=None,
):
    # if label is None:
    #     label = "".join(caption.split())

    data = _add_tabular(
        table_array, cols, horizontal_lines=horizontal_lines, split=split
    )

    center = Center(data=data)
    table = Table(position="H")
    if caption:
        table.add_caption(caption)
    table.append(center)
    if label:
        table.append(Label(label))
    return table


# Refactoring in process - eventually must drop either _add_table_ or _add_table for sanity's sake.
def _add_table_(
    data,
    caption=None,
    label=None,
):
    table = Table(position="H")
    if caption:
        table.add_caption(caption)
    if isinstance(data, list):
        for item in data:
            table.append(item)
    else:
        table.append(data)
    if label:
        table.append(Label(label))
    return table


def _add_ply_stack_tables(
    ply_stack: PlyStack,
    options_dict: dict[str, PrintOptions] = dict(),
    center: bool = True,
    lam_name: str = "",
):
    tabulars = Center() if center else list()
    tabulars.append(
        _add_table(
            _list_of_entities_dicts_to_table_list(
                ply_stack.print_stack_list, header=True, options_dict=options_dict
            ),
            caption=f"{lam_name} {PLY_STACK_LIST}",
            horizontal_lines=[0],
        )
    )
    tabulars.append(
        _add_table(
            _list_of_entities_dicts_to_table_list(
                [ply_stack.print_stack_options], header=True, options_dict=options_dict
            ),
            caption=f"{lam_name} {PLY_STACK_OPTIONS}",
            horizontal_lines=[0],
        )
    )
    return tabulars


def _single_skin_laminate_tables(
    lam: SingleSkinLaminate,
    label=None,
    options_dict: dict[str, PrintOptions] = dict(),
    center: bool = True,
):
    return _add_ply_stack_tables(
        lam.ply_stack, options_dict=options_dict, center=center, lam_name=lam.name
    )


def _sandwich_laminate_tables(
    lam: SandwichLaminate,
    label=None,
    options_dict: dict[str, PrintOptions] = dict(),
    center: bool = True,
):
    tables = []
    sandwich_laminate_options_data = _list_of_entities_dicts_to_table_list(
        [lam.print_laminate_options], header=True, options_dict=options_dict
    )
    sandwich_laminate_options_table = _add_table(
        sandwich_laminate_options_data,
        caption=f"{lam.name} {SANDWICH_LAMINATE_ARGUMENTS_TABLE_CAPTION}",
        horizontal_lines=[0],
    )
    if center:
        center_ = Center()
        center_.append(sandwich_laminate_options_table)
        tables.append(center_)
    else:
        tables.append(sandwich_laminate_options_table)
    tables.append(
        _add_ply_stack_tables(
            lam.outter_laminate_ply_stack,
            options_dict=options_dict,
            center=center,
            lam_name=f"{lam.name} outter skin",
        )
    )
    if not (lam.antisymmetric or lam.symmetric):
        tables.append(
            _add_ply_stack_tables(
                lam.inner_laminate_ply_stack,
                options_dict=options_dict,
                center=center,
                lam_name=f"{lam.name} inner skin",
            )
        )
    return tables


def _stiffener_tables(
    stiffener: StiffenerSectionWithFoot,
    options_dict: dict[str, PrintOptions] = dict(),
    center: bool = True,
):
    data = _list_of_entities_dicts_to_table_list(
        [serialize_dataclass(stiffener, printing_format=True, include_names=True)],
        header=True,
        options_dict=options_dict,
    )
    # Swap performed between name and type of stiffener properties, to leave name first
    for row in data:
        row[0], row[1] = row[1], row[0]
    container = Center() if center else list()
    container.append(
        _add_tabular(
            data,
            horizontal_lines=[0],
        )
    )
    return _add_table_(
        container,
        caption=f"{STIFFENER_SECTION_DEFINITION_CAPTION.capitalize()} {stiffener.name}",
    )


def generate_report(
    session: Session, file_name="report", config: ReportConfig = ReportConfig()
):
    # Document preamble
    geometry_options = NoEscape(r"text={7in,10in}, a4paper, centering")
    document_options = ["11pt", "a4paper"]
    doc_kwargs = {
        "document_options": document_options,
        "geometry_options": geometry_options,
    }
    display_options = config.to_dict()
    doc = Document(**doc_kwargs)
    doc.preamble.append(Package("float"))
    doc.preamble.append(Package("pdflscape"))
    doc.preamble.append(Package("hyperref"))
    doc.preamble.append(Package("bookmark"))
    doc.preamble.append(NoEscape(r"\DeclareSIUnit\kt{kt}"))
    doc.preamble.append(NoEscape(r"\sisetup{round-mode=places}"))
    # doc.preamble.append(NoEscape(r"\sisetup{scientific-notation=true}"))
    doc.append(TableOfContents())
    doc.append(ListOfTables())

    ABR_CAPTION = "Abreviations"
    abr_section = Section(ABR_CAPTION, numbering=False)
    abr_table = [
        [item.metadata.names.long, item.metadata.names.abreviation]
        for item in abv_registry
    ]

    abr_section.append(_add_table(abr_table))
    doc.append(abr_section)
    doc.append(NewPage())

    # Section Vessel
    section_vessel = Section(VESSEL_SECTION_TITLE)

    # Vessel data
    vessels = session.vessels
    for vessel in vessels.values():
        options_dict = display_options
        vessel_input = _single_entity_dict_to_table_list(
            serialize_dataclass(obj=vessel, printing_format=True, include_names=True),
            options_dict=options_dict,
        )
        vessel_loads = vessel.loads_asdict
        vessel_loads = _single_entity_dict_to_table_list(vessel_loads)
        vessel_tables = [vessel_input, vessel_loads]
        captions = [f"{vessel.name} parameters", f"{vessel.name} global loads"]
        for array, caption, split in zip(vessel_tables, captions, [4, 2]):
            table = _add_table(
                table_array=array,
                cols="l r",
                caption=caption,
                split=split,
                label="".join(caption.split()),
            )
            section_vessel.append(table)
    doc.append(section_vessel)

    # Section Materials
    section_materials = Section(MATERIALS_SECTION_TITLE)
    section_constituent_materials = Subsection(CONSTITUENT_MATERIASL_SECTION_TITLE)

    # Fibers data

    fibers_dict = {
        key: serialize_dataclass(value, printing_format=True, include_names=True)
        for key, value in session.fibers.items()
    }
    fibers_input = _list_of_entities_dicts_to_table_list(
        list(fibers_dict.values()),
        options_dict=display_options,
        header=True,
        split_units=True,
    )
    fibers_table = _add_table(
        table_array=fibers_input,
        # cols="l c c c c c",
        caption=FIBER_CAPTION,
        label="".join(FIBER_CAPTION.split()),
        horizontal_lines=[1],
    )
    sub_section_fibers = Subsection(FIBER_CAPTION)
    section_constituent_materials.append(fibers_table)
    # section_materials.append(sub_section_fibers)

    # Matrix data
    matrices_dict = {
        key: serialize_dataclass(value, printing_format=True, include_names=True)
        for key, value in session.matrices.items()
    }
    matrices_input = _list_of_entities_dicts_to_table_list(
        list(matrices_dict.values()),
        options_dict=display_options,
        header=True,
        split_units=True,
    )
    matrices_table = _add_table(
        table_array=matrices_input,
        # cols="l c c c c c",
        caption=MATRIX_CAPTION,
        label="".join(MATRIX_CAPTION.split()),
        horizontal_lines=[1],
    )
    sub_section_matrices = Subsection(MATRIX_CAPTION)
    section_constituent_materials.append(matrices_table)
    # section_materials.append(sub_section_matrices)

    # Core Data
    sub_section_cores = Subsection(CORES_SUB_SECTION_TITLE)
    data = [
        serialize_dataclass(item, printing_format=True, include_names=True)
        for item in session.core_materials.values()
    ]
    core_materials_input = _list_of_entities_dicts_to_table_list(
        entities=data, options_dict=display_options, header=True, split_units=True
    )
    core_materials_table = _add_table(
        table_array=core_materials_input,
        # cols="l c c c c c",
        caption=CORE_MATERIAL_TABLE_CAPTION,
        horizontal_lines=[1],
    )
    section_constituent_materials.append(core_materials_table)
    data = [
        serialize_dataclass(item, printing_format=True, include_names=True)
        for item in session.cores.values()
    ]
    cores_input = _list_of_entities_dicts_to_table_list(
        entities=data, options_dict=display_options, header=True, split_units=True
    )
    cores_table = _add_table(
        table_array=cores_input,
        # cols="l c c c c c",
        caption=CORES_SUB_SECTION_TITLE,
        horizontal_lines=[1],
    )
    section_constituent_materials.append(cores_table)
    # section_materials.append(sub_section_cores)

    # Laminae data
    # Monolith lamina
    monolith_lamina_dict = {
        key: serialize_dataclass(value.data, printing_format=True, include_names=True)
        for key, value in session.laminas.items()
        if isinstance(value.data, LaminaMonolith)
    }
    monolith_lamina_input = _list_of_entities_dicts_to_table_list(
        list(monolith_lamina_dict.values()),
        options_dict=display_options,
        header=True,
        split_units=True,
    )
    monolith_lamina_table = _add_table(
        table_array=monolith_lamina_input,
        # cols="l c c c c c",
        caption=LAMINA_MONLITH_CAPTION,
        label="".join(LAMINA_MONLITH_CAPTION.split()),
        horizontal_lines=[1],
    )
    sub_section_laminas = Subsection(LAMINAS_SECTION_TITLE)
    section_constituent_materials.append(monolith_lamina_table)

    # Lamina definied by parts
    parts_lamina_dict = {
        key: serialize_dataclass(value.data, printing_format=True, include_names=True)
        for key, value in session.laminas.items()
        if isinstance(value.data, LaminaParts)
    }
    parts_lamina_input = _list_of_entities_dicts_to_table_list(
        list(parts_lamina_dict.values()),
        options_dict=display_options,
        header=True,
        split_units=True,
    )
    parts_lamina_table = _add_table(
        table_array=parts_lamina_input,
        # cols="l c c c c c",
        caption=LAMINA_PARTS_CAPTION,
        label="LaminasParts",
        horizontal_lines=[1],
    )
    section_constituent_materials.append(parts_lamina_table)
    section_materials.append(section_constituent_materials)

    # Laminate Data

    # Single skin laminates
    sub_section_laminates = Subsection(LAMINATES_SECTION_TITLE)
    for lam in filter(
        lambda lam: isinstance(lam, SingleSkinLaminate), session.laminates.values()
    ):
        _single_skin_laminate_tables(lam, options_dict=display_options)
        sub_sub_section = Subsubsection(lam.name)
        for data in _single_skin_laminate_tables(lam, options_dict=display_options):
            sub_sub_section.append(data)
        sub_section_laminates.append(sub_sub_section)

    # Sandwich laminates
    for lam in filter(
        lambda lam: isinstance(lam, SandwichLaminate), session.laminates.values()
    ):
        data = _sandwich_laminate_tables(lam, options_dict=display_options)
        sub_sub_section = Subsubsection(lam.name)
        for item in data:
            sub_sub_section.append(item)
        sub_section_laminates.append(sub_sub_section)
    section_materials.append(sub_section_laminates)
    doc.append(section_materials)

    # Stiffener Sections
    section_stiffener_profiles = Section(STIFFENER_PROFILES_SECTION_TITLE)
    for stiffener in session.stiffener_sections.values():
        sub_section = Subsection(stiffener.name)
        sub_section.append(_stiffener_tables(stiffener, options_dict=display_options))
        section_stiffener_profiles.append(sub_section)
    doc.append(section_stiffener_profiles)

    # Panels
    locations: list[Location] = LOCATION_TYPES
    landscape = Landscape()
    section_panels = Section(PANELS_SECTION_TITLE)
    sub_section_panels_inputs = Subsection(
        f"{PANELS_SECTION_TITLE} {INPUTS_TITLE.lower()}"
    )
    for location in locations:
        panels = [
            dict(
                filter(
                    lambda item: item[0] not in ["element_type", "location"],
                    serialize_dataclass(
                        panel,
                        printing_format=True,
                        include_names=True,
                        filter_fields=["vessel"],
                    ).items(),
                )
            )
            for panel in session.panels.values()
            if isinstance(panel.location, location)
        ]
        if panels:
            panels_input = _list_of_entities_dicts_to_table_list(
                panels, header=True, split_units=True, options_dict=options_dict
            )
            panels_tabular = Center()
            panels_tabular.append(_add_tabular(panels_input, horizontal_lines=[1]))
            sub_section_panels_inputs.append(
                _add_table_(
                    panels_tabular, caption=f"{location.name.capitalize()} panels"
                )
            )

    section_panels.append(sub_section_panels_inputs)
    landscape.append(section_panels)
    sub_section = Subsection(RULE_CHECK_RESULT_CAPTION)

    doc.append(landscape)

    # Stiffeners
    landscape = Landscape()
    section_stiffeners_elements = Section(STIFFENERS_SECTION_TITLE)
    sub_section_stiffeners_inputs = Subsection(
        f"{STIFFENERS_SECTION_TITLE} {INPUTS_TITLE.lower()}"
    )
    for location in locations:
        stiffeners = [
            dict(
                filter(
                    lambda item: item[0] not in ["element_type", "location"],
                    serialize_dataclass(
                        stiffener,
                        printing_format=True,
                        include_names=True,
                        filter_fields=["vessel"],
                    ).items(),
                )
            )
            for stiffener in session.stiffener_elements.values()
            if isinstance(stiffener.location, location)
        ]
        if stiffeners:
            stiffeners_input = _list_of_entities_dicts_to_table_list(
                stiffeners, header=True, split_units=True, options_dict=options_dict
            )
            stiffeners_tabular = Center()
            stiffeners_tabular.append(
                _add_tabular(stiffeners_input, horizontal_lines=[1])
            )
            sub_section_stiffeners_inputs.append(
                _add_table_(
                    stiffeners_tabular,
                    caption=f"{location.name.capitalize()} stiffeners",
                )
            )

    section_stiffeners_elements.append(sub_section_stiffeners_inputs)
    landscape.append(section_stiffeners_elements)
    doc.append(landscape)

    doc.generate_tex(file_name)
    # doc.generate_pdf(file_name, clean_tex=False)
    return doc
