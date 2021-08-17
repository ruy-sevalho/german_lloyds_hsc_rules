# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 08:30:37 2021

@author: ruy
"""
# from collections import namedtuple
# from dataclasses import dataclass
from typing import Any, List

import numpy as np
import pylatex
from pylatex import NoEscape, Quantity
import quantities as pq
from marshmallow_dataclass import dataclass
from marshmallow import fields, Schema

from .metadata import METADATA, PrintWrapper, NamePrint


pylatex.quantities.UNIT_NAME_TRANSLATIONS.update(
    {"nautical_miles_per_hour": "kt", "arcdegree": "degree", "p": "pascal"}
)

kN = pq.UnitQuantity("kiloNewton", pq.N * 1e3, symbol="kN")


def _print_wrapper_builder(value, **metadata):
    if isinstance(value, Data):
        return PrintWrapper(value.name, metadata["names"])
    if isinstance(value, (int, float)):
        if metadata["units"] == "percent":
            value *= 100
        return PrintWrapper(pq.Quantity(value, metadata["units"]), metadata["names"])
    else:
        return PrintWrapper(value, metadata["names"])


def _data_to_dict(obj, names: List[str], metadata: dict = METADATA):
    # metadata.update({"name": {"names": NamePrint("Name", "Name")}})
    return {
        name: _print_wrapper_builder(getattr(obj, name), **metadata[name])
        for name in names
    }


def _input_data_dict(obj):
    return _data_to_dict(obj, obj.__dataclass_fields__.keys())


@dataclass
class Criteria:
    value: float
    allowed: float

    @property
    def ratio(self):
        return self.allowed / self.value


@dataclass
class Data:
    @property
    def inputs_asdict(self):
        return _input_data_dict(self)

    @property
    def _plucked_attr(self):
        return [
            attr
            for attr in self.__dataclass_fields__.keys()
            if isinstance(getattr(self, attr), Data)
        ]

    @property
    def _plucked_asdict(self):
        schema = self.Schema()
        f = schema.fields
        for attr in self._plucked_attr:
            f.update({attr: fields.Pluck("self", "name")})
        updated_schema = Schema.from_dict(f)()
        return updated_schema.dump(self)


# @dataclass
# class QuantityPrintWrapper:
#     """Print meta data for attr."""

#     _value: float
#     name: NamePrint
#     unit: str = None
#     round_precision: int = 2

#     @property
#     def value(self):

# def print_quantity(self, value, unit=None):
#     quantity = pq.Quantity(value, self.unit)
#     if unit is not None:
#         quantity = quantity.rescale(pq.Quantity(unit))
#     return quantity

# @dataclass
# class PrintWrapper:
#     """Printer wrapper for attr."""

#     value: float
#     meta_data: PrintMetaData

#     def __getattr__(self, name):
#         try:
#             return getattr(self.meta_data, name)
#         except AttributeError:
#             return self.__getattribute__(name)
#             # raise AttributeError(
#             #     f"'{type(self).__name__}' object has no attribute '{name}'")

#     # def __post_init__(self):
#     #     self.__dict__.update({key: self.md.__dict__[key])

# # PrintMetaData = namedtuple('PrintMetaData', 'long abbr unit', defaults=[None])
# fwd_perp = PrintMetaData(
#     "Foward perpendicular",
#     NoEscape(r"F\textsubscript{P}"),
#     " m"
# )
# aft_perp = PrintMetaData(
#     "Aft perpendicular",
#     NoEscape(r"A\textsubscript{P}"),
#     " m"
# )
# z_baseline = PrintMetaData(
#     "z coordinate of baseline", NoEscape(r"z\textsubscript{BL}"), " m"
# )
# dist_hull_cl = PrintMetaData(
#     "Distance between hulls centerline",
#     NoEscape(r"B\textsubscript{CL}"),
#     " m"
# )
# lcg = PrintMetaData(
#     "Longitudinal center of gravity", NoEscape(r"L\textsubscript{CG}"), " m"
# )
# service_range = PrintMetaData("Service range", "SR", None)
# type_of_service = PrintMetaData("Type of service", "ToS", None)
# block_coef = PrintMetaData(
#     "Block coefficient", NoEscape(r"C\textsubscript{B}"), None)
# water_plane_area = PrintMetaData(
#     "Water plane area", NoEscape(r"WP\textsubscript{A}"), " m*m"
# )
# deadrise_lcg = PrintMetaData(
#     NoEscape(r"Deadrise at " + lcg.abbr),
#     NoEscape(r"$\alpha$\textsubscript{d}"),
#     'degree'
#     # NoEscape(r"$^{\circ}$"),
# )
# shear_force = PrintMetaData(
#     "Shear force", NoEscape(r"T\textsubscript{bt}"), "kN")
# transverse_bending_moment = PrintMetaData(
#     "Transverse bending moment", NoEscape(r"M\textsubscript{bt}"), " kN"
# )
# transverse_torsional_moment = PrintMetaData(
#     "Transverse torsional moment", NoEscape(r"M\textsubscript{tt}"), " kN"
# )
# speed = PrintMetaData("Speed", "S", " kt")
# length = PrintMetaData("Length", "L", " m")
# displacement = PrintMetaData("Displacement", NoEscape(r"$\Delta$"), " t")
# beam = PrintMetaData("Beam", "B", " m")
# draft = PrintMetaData("Draft", "H", " m")
# vert_acg = PrintMetaData(
#     "Vertical acceleration",
#     NoEscape(r"a\textsubscript{CG}"),
#     " g"
# )


# class Report:
#     _attr_print_wrappers = {
#         "fwd_perp": fwd_perp,
#         "aft_perp": aft_perp,
#         "z_baseline": z_baseline,
#         "dist_hull_cl": dist_hull_cl,
#         "lcg": lcg,
#         "service_range": service_range,
#         "type_of_service": type_of_service,
#         "block_coef": block_coef,
#         "water_plane_area": water_plane_area,
#         "deadrise_lcg": deadrise_lcg,
#         "shear_force": shear_force,
#         "transverse_bending_moment": transverse_bending_moment,
#         "transverse_torsional_moment": transverse_torsional_moment,
#         "speed": speed,
#         "length": length,
#         "beam": beam,
#         "displacement": displacement,
#         "draft": draft,
#         "vert_acg": vert_acg,
#     }
#     _named_types = [
#         "Fiber",
#         "Matrix",
#         "Laminate",
#         "SandwichLaminate",
#     ]
#     _filtered_out = [
#         "plies_materials",
#     ]

#     def _print_wrapper(self, key):
#         return self._attr_print_wrappers.get(key, PrintMetaData(key, key))

#     def _convert_dict2(self, d):
#         return [
#             [
#                 self._print_wrapper(key).abbr,
#                 _print_sort(
#                     value,
#                     self._print_wrapper(key).unit,
#                     self._print_wrapper(key).round_precision),
#             ]
#             for key, value in d.items()
#         ]

#     @property
#     def _named_keys(self):
#         return list(
#             filter(
#                 lambda key: type(
#                     self.__dict__[key]).__name__ in self._named_types,
#                 self.__dict__.keys(),
#             )
#         )

#     def _filtered(self, d):
#         return dict(
#             filter(lambda item: item[0] not in self._filtered_out, d.items())
#         )

#     def _named(self, d):
#         def value(key):
#             if key in self._named_keys:
#                 return d[key].__name__
#             else:
#                 return d[key]

#         if not self._named_keys:
#             return d
#         d_copy = {key: value(key) for key in d}
#         return d_copy

#     def _named_and_filterd(self, d):
#         return self._named(self._filtered(d))

#     def _input(self):
#         return self._named_and_filterd(self.__dict__)

#     def _input_print(self):
#         return self._convert_dict2(self._input())
#         # return self._convert_dict(
#         #     self._input(),
#         #     self._attr_print,
#         #     self._units_table,
#         # )

#     def _output_print(self):
#         return self._convert_dict2(self._output())
#         # return self._convert_dict(
#         #     self._output(),
#         #     self._attr_print,
#         #     self._units_table,
#         # )

#     @property
#     def input_print_dict(self):
#         return {key: PrintWrapper(value, self._print_wrapper(key))
#                 for key, value in self._input().items()}

#     def input_print(self):
#         return self._input_print()

#     def output_print(self):
#         return self._output_print()
