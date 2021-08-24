# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 12:53:01 2021

@author: ruy
"""
from math import ceil, floor
from itertools import chain
from dataclasses import field

import quantities as pq
from pylatex import (
    NoEscape,
    Table,
    Tabular,
    Document,
    Section,
    Subsection,
    MiniPage,
    Quantity,
)
from pylatex.base_classes import Environment
from pylatex.labelref import Label
from pylatex.utils import (
    bold,
)
from pylatex.math import Math


INPUT = "Input"
VESSEL_SECTION_TITLE = "Vessel"
VESSEL_INPUT_CAPTION = "Vessel parameters"
VESSEL_LOADS_CAPTION = "Vessel global loads"
MATERIALS_SECTION_TITLE = "Materials"
FIBER_CAPTION = "Fibers"
MATRIX_CAPTION = "Matrices"
LAMINATE_COMPOSED_CAPTION = "Laminates - properties calculated from fiber and matix"
CAPTIONS_VESSEL = [VESSEL_INPUT_CAPTION, VESSEL_LOADS_CAPTION]


class Center(Environment):
    pass


def _print_quantity(quantity, convert_units=None, round_precision=2, disp_units=False):
    options = {"round-precision": round_precision}
    if convert_units is not None:
        quantity = quantity.rescale(convert_units)
    if not disp_units:
        quantity = quantity.magnitude
    return Quantity(quantity, options=options)


def _print_type(value, **kwargs):
    if isinstance(value, pq.Quantity):
        return _print_quantity(value, **kwargs)
    return value


def _get_unit(value, **kwargs):
    if isinstance(value, str):
        return ""
    if value.units == pq.dimensionless:
        return ""
    if kwargs.get("convert_units", None) is not None:
        value = value.rescale(kwargs["convert_units"])
    unit_string = Quantity(value.units).dumps()
    unit_string = unit_string[:4] + unit_string[7:]

    return NoEscape(" " + "(" + unit_string + ")")


def _single_entity_dict_to_table_list(inp, header=None, options_dict={}):
    return [
        [
            printable.names.abbr,
            _print_type(
                printable.value, **{"disp_units": True, **options_dict.get(key, {})}
            ),
        ]
        for key, printable in inp.items()
    ]


# Selection of attributes and properties to print are made by each object, which
# wraps the results as property that returns a dict
def _dict_of_entities_dicts_to_table_list(
    entities, attr_name="inputs_asdict", header=None, options_dict={}
):
    table = [
        [
            _print_type(printable.value, **options_dict.get(key, {}))
            for key, printable in getattr(entity, attr_name).items()
        ]
        for entity in entities.values()
    ]
    if header:
        table = [
            [
                NoEscape(
                    printable.names.abbr
                    + _get_unit(printable.value, **options_dict.get(key, {}))
                )
                for key, printable in getattr(
                    list(entities.values())[0], attr_name
                ).items()
            ]
        ] + table
    return table


def _cols_repeat(cols_step, n):
    cols_step = NoEscape(cols_step)
    cols = cols_step
    for _ in range(int(n - 1)):
        cols = NoEscape(cols + NoEscape(r" | ") + cols_step)
    return cols


def _build_cols(table_array):
    return "l" + " c" * (len(table_array[0]) - 1)


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
    if cols is None:
        cols = _build_cols(table_array)
    table = Table(position="h!")
    if caption:
        table.add_caption(caption)
    if split:
        table_array, n = _split_array(table_array, split)
        cols = _cols_repeat(cols, n)
    # table.append(NoEscape(r"\centering"))
    center = Center(
        data=_add_tabular(table_array, cols, horizontal_lines=horizontal_lines)
    )
    table.append(center)
    if label:
        table.append(Label(label))
    return table


def _add_tabular(table_array, cols, horizontal_lines=None):
    if horizontal_lines is None:
        horizontal_lines = []
    tabular = Tabular(cols)
    for i, row in enumerate(table_array):
        tabular.add_row(row)
        if i in horizontal_lines:
            tabular.add_hline()
    return tabular


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


def _extract_attr_from_entities(entities, attr_name="input_asdict"):
    return [getattr(entity, attr_name) for entity in entities.values()]


def generate_report(session, file_name="report"):
    # Vessel data
    vessel = session.vessel
    vessel_input = _single_entity_dict_to_table_list(vessel.inputs_asdict)
    vessel_loads = _single_entity_dict_to_table_list(vessel.loads_asdict)
    vessel_tables = [vessel_input, vessel_loads]

    modulus_options = {"round_precision": 2, "convert_units": "GPa"}

    display_options = {
        "modulus_x": modulus_options,
        "modulus_y": modulus_options,
        "modulus_xy": modulus_options,
        "density": {"round_precision": 0},
    }

    # Fibers data
    fibers_input = _dict_of_entities_dicts_to_table_list(
        session.fibers, options_dict=display_options, header=True
    )
    # Matrix data
    matrices_input = _dict_of_entities_dicts_to_table_list(
        session.matrices, options_dict=display_options, header=True
    )

    # Plies data
    plies = _dict_of_entities_dicts_to_table_list(
        session.plies_mat, options_dict=display_options, header=True
    )

    # Lamina/Ply data

    geometry_options = NoEscape(r"text={7in,10in}, a4paper, centering")
    document_options = ["11pt", "a4paper"]
    doc_kwargs = {
        "document_options": document_options,
        "geometry_options": geometry_options,
    }

    # Document preamble
    doc = Document(**doc_kwargs)
    doc.preamble.append(NoEscape(r"\DeclareSIUnit\kt{kt}"))
    doc.preamble.append(NoEscape(r"\sisetup{round-mode=places}"))
    # doc.preamble.append(NoEscape(r"\sisetup{scientific-notation=true}"))

    # Section Vessel
    section_vessel = Section(VESSEL_SECTION_TITLE)
    for array, caption, split in zip(vessel_tables, CAPTIONS_VESSEL, [4, 2]):
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
    matrices_table = _add_table(
        table_array=matrices_input,
        # cols="l c c c c c",
        caption=MATRIX_CAPTION,
        label="".join(MATRIX_CAPTION.split()),
        horizontal_lines=[0],
    )
    section_materials.append(matrices_table)
    fibers_table = _add_table(
        table_array=fibers_input,
        # cols="l c c c c c",
        caption=FIBER_CAPTION,
        label="".join(FIBER_CAPTION.split()),
        horizontal_lines=[0],
    )
    section_materials.append(fibers_table)

    doc.append(section_materials)

    doc.generate_tex(file_name)
    return doc
