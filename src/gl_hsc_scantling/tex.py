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
from pylatex import (
    Document,
    MiniPage,
    NoEscape,
    Quantity,
    Section,
    Subsection,
    Table,
    Tabular,
)
from pylatex.base_classes import Environment
from pylatex.labelref import Label
from pylatex.math import Math
from pylatex.utils import bold

from .abrevitation_registry import abv_registry
from .composites import LaminaMonolith, LaminaParts

if TYPE_CHECKING:
    from .session import Session

INPUT = "Input"
VESSEL_SECTION_TITLE = "Vessels"
VESSEL_INPUT_CAPTION = "Vessel parameters"
VESSEL_LOADS_CAPTION = "Vessel global loads"
MATERIALS_SECTION_TITLE = "Materials"
FIBER_CAPTION = "Fibers"
MATRIX_CAPTION = "Matrices"
LAMINATE_COMPOSED_CAPTION = "Laminates - properties calculated from fiber and matix"
CAPTIONS_VESSEL = [VESSEL_INPUT_CAPTION, VESSEL_LOADS_CAPTION]


class Center(Environment):
    pass


@dataclass
class PrintOptions:
    """[summary]"""

    convert_units: Optional[str] = None
    round_precision: int = 2


@dataclass
class ReportConfig:
    modulus_x: PrintOptions = PrintOptions(convert_units="GPa")
    modulus_y: PrintOptions = PrintOptions(convert_units="GPa")
    modulus_xy: PrintOptions = PrintOptions(convert_units="GPa")
    density: PrintOptions = PrintOptions(round_precision=0)
    max_strain_x: PrintOptions = PrintOptions()
    max_strain_xy: PrintOptions = PrintOptions()
    f_mass_cont: PrintOptions = PrintOptions()
    f_area_density: PrintOptions = PrintOptions()
    thickness: PrintOptions = PrintOptions()

    def to_dict(self):
        return {field_.name: getattr(self, field_.name) for field_ in fields(self)}


def _print_quantity(
    quantity: pq.Quantity,
    disp_units=False,
    convert_units=None,
    round_precision=2,
):
    options = {"round-precision": round_precision}
    if convert_units is not None:
        quantity = quantity.rescale(convert_units)
    if not disp_units:
        quantity = quantity.magnitude
    return Quantity(quantity, options=options)


def _print_type(
    value,
    disp_units=False,
    convert_units=None,
    round_precision=2,
):
    if isinstance(value, pq.Quantity):
        return _print_quantity(
            value,
            disp_units=disp_units,
            convert_units=convert_units,
            round_precision=round_precision,
        )
    return value


def _get_unit(value: Union[str, pq.Quantity], **kwargs):
    if isinstance(value, str):
        return ""
    if value.units == pq.dimensionless:
        return ""
    if kwargs.get("convert_units", None) is not None:
        value = value.rescale(kwargs["convert_units"])
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
                **asdict(options_dict.get(key, PrintOptions())),
            ),
        ]
        for key, printable in inp.items()
    ]


# Selection of attributes and properties to print are made by each object, which
# wraps the results as property that returns a dict
def _dict_of_entities_dicts_to_table_list(
    entities: dict[str, dict[str, PrintWrapper]],
    header: bool = False,
    options_dict: dict[str, PrintOptions] = dict(),
):
    """Creates a table(lists of lists)"""
    table = [
        [
            _print_type(
                printable.value, **asdict(options_dict.get(key, PrintOptions()))
            )
            for key, printable in entity.items()
        ]
        for entity in entities.values()
    ]
    if header:
        entity: dict[str, PrintWrapper] = list(entities.values())[0]
        table = [
            [
                NoEscape(
                    printable.names.abreviation
                    + _get_unit(
                        printable.value, **asdict(options_dict.get(key, PrintOptions()))
                    )
                )
                for key, printable in entity.items()
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


def _add_tabular(table_array, cols, horizontal_lines=None):
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
    doc = Document(**doc_kwargs)
    doc.preamble.append(NoEscape(r"\DeclareSIUnit\kt{kt}"))
    doc.preamble.append(NoEscape(r"\sisetup{round-mode=places}"))
    # doc.preamble.append(NoEscape(r"\sisetup{scientific-notation=true}"))

    # section_resume = Section("Resume", numbering=False)

    abr_table = [
        [item.metadata.names.long, item.metadata.names.abreviation]
        for item in abv_registry
    ]

    # section_resume.append(_add_table(abr_table))

    doc.append(_add_table(abr_table))

    # Section Vessel
    section_vessel = Section(VESSEL_SECTION_TITLE)

    # Vessel data
    vessels = session.vessels

    for vessel in vessels.values():
        options_dict = vessel.input_print_options()
        vessel_input = _single_entity_dict_to_table_list(
            serialize_dataclass(obj=vessel, printing_format=True, include_names=True),
            options_dict=vessel.input_print_options(),
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

    # modulus_options = PrintOptions(**{"round_precision": 2, "convert_units": "GPa"})

    # display_options = {
    #     "modulus_x": modulus_options,
    #     "modulus_y": modulus_options,
    #     "modulus_xy": modulus_options,
    #     "density": PrintOptions(**{"round_precision": 0}),
    # }
    display_options = config.to_dict()

    # Fibers data
    fibers_dict = {
        key: serialize_dataclass(value, printing_format=True, include_names=True)
        for key, value in session.fibers.items()
    }
    fibers_input = _dict_of_entities_dicts_to_table_list(
        fibers_dict, options_dict=display_options, header=True
    )
    fibers_table = _add_table(
        table_array=fibers_input,
        # cols="l c c c c c",
        caption=FIBER_CAPTION,
        label="".join(FIBER_CAPTION.split()),
        horizontal_lines=[0],
    )
    section_materials.append(fibers_table)

    # Matrix data
    matrices_dict = {
        key: serialize_dataclass(value, printing_format=True, include_names=True)
        for key, value in session.matrices.items()
    }
    matrices_input = _dict_of_entities_dicts_to_table_list(
        matrices_dict, options_dict=display_options, header=True
    )
    matrices_table = _add_table(
        table_array=matrices_input,
        # cols="l c c c c c",
        caption=MATRIX_CAPTION,
        label="".join(MATRIX_CAPTION.split()),
        horizontal_lines=[0],
    )
    section_materials.append(matrices_table)

    # Laminae data
    # Monolith lamin
    monolith_lamina_dict = {
        key: serialize_dataclass(value.data, printing_format=True, include_names=True)
        for key, value in session.laminas.items()
        if isinstance(value.data, LaminaMonolith)
    }
    monolith_lamina_input = _dict_of_entities_dicts_to_table_list(
        monolith_lamina_dict, options_dict=display_options, header=True
    )
    LAMINA_MONLITH_CAPTION = "Laminas"
    monolith_lamina_table = _add_table(
        table_array=monolith_lamina_input,
        # cols="l c c c c c",
        caption=LAMINA_MONLITH_CAPTION,
        label="".join(LAMINA_MONLITH_CAPTION.split()),
        horizontal_lines=[0],
    )
    section_materials.append(monolith_lamina_table)
    parts_lamina_dict = {
        key: serialize_dataclass(value.data, printing_format=True, include_names=True)
        for key, value in session.laminas.items()
        if isinstance(value.data, LaminaParts)
    }
    parts_lamina_input = _dict_of_entities_dicts_to_table_list(
        parts_lamina_dict, options_dict=display_options, header=True
    )
    LAMINA_PARTS_CAPTION = "Laminas - definied by fiber and matirx combination"
    parts_lamina_table = _add_table(
        table_array=parts_lamina_input,
        # cols="l c c c c c",
        caption=LAMINA_PARTS_CAPTION,
        label="LaminasParts",
        horizontal_lines=[0],
    )
    section_materials.append(parts_lamina_table)

    doc.append(section_materials)

    doc.generate_tex(file_name)
    return doc
