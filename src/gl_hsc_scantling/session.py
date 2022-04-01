from dataclasses import dataclass, field, fields
from typing import Union
from json import dump, dumps, load, loads

import pandas as pd

from dataclass_tools.tools import (
    DESERIALIZER_OPTIONS,
    DeSerializerOptions,
    deserialize_dataclass,
    serialize_dataclass,
)

from gl_hsc_scantling.composites import (
    Core,
    CoreMat,
    Fiber,
    Lamina,
    Laminate,
    Matrix,
    SandwichLaminate,
    SingleSkinLaminate,
)
from gl_hsc_scantling.elements import VESSEL_OPTIONS, StructuralElement
from gl_hsc_scantling.panels import Panel
from gl_hsc_scantling.stiffeners import (
    Stiffener,
    StiffenerSection,
    StiffenerSectionWithFoot,
)
from gl_hsc_scantling.vessel import Catamaran, Monohull

TYPE_LABEL = "typ"

LAMINATE_OPTIONS = DeSerializerOptions(add_type=True)
STIFFENER_OPTIONS = DeSerializerOptions(add_type=True)
VESSEL_OPTIONS = DeSerializerOptions(add_type=True)


@dataclass
class Session:
    vessels: dict[str, Monohull | Catamaran] = field(
        default_factory=dict, metadata={DESERIALIZER_OPTIONS: VESSEL_OPTIONS}
    )
    fibers: dict[str, Fiber] = field(default_factory=dict)
    matrices: dict[str, Matrix] = field(default_factory=dict)
    laminas: dict[str, Lamina] = field(default_factory=dict)
    core_materials: dict[str, CoreMat] = field(default_factory=dict)
    cores: dict[str, Core] = field(default_factory=dict)
    laminates: dict[str, Laminate] = field(
        default_factory=dict, metadata={DESERIALIZER_OPTIONS: LAMINATE_OPTIONS}
    )
    stiffener_sections: dict[str, StiffenerSectionWithFoot] = field(
        default_factory=dict
    )
    panels: dict[str, StructuralElement] = field(default_factory=dict)
    stiffener_elements: dict[str, StructuralElement] = field(default_factory=dict)

    @property
    def session_dict(self):
        return {field_.name: getattr(self, field_.name) for field_ in fields(self)}

    def sort_strucutural_element(self, element: StructuralElement):
        if not isinstance(element, StructuralElement):
            return None
        table = {Panel: self.panels, Stiffener: self.stiffener_elements}
        return table[type(element.model)]

    def _sort_item(
        self,
        item: Union[
            Monohull,
            Fiber,
            Matrix,
            CoreMat,
            Core,
            Lamina,
            Laminate,
            StiffenerSection,
            StructuralElement,
        ],
    ) -> dict[
        str,
        Union[
            Monohull,
            Fiber,
            Matrix,
            CoreMat,
            Core,
            Lamina,
            Laminate,
            StiffenerSection,
            StructuralElement,
        ],
    ]:
        table = {
            Monohull: self.vessels,
            Catamaran: self.vessels,
            Fiber: self.fibers,
            Matrix: self.matrices,
            CoreMat: self.core_materials,
            Core: self.cores,
            Lamina: self.laminas,
            Laminate: self.laminates,
            SingleSkinLaminate: self.laminates,
            SandwichLaminate: self.laminates,
            StiffenerSection: self.stiffener_sections,
            StiffenerSectionWithFoot: self.stiffener_sections,
            StructuralElement: self.sort_strucutural_element(item),
        }
        return table[type(item)]

    def add_stuff(
        self,
        stuff=list[
            Union[
                Monohull,
                Catamaran,
                Fiber,
                Matrix,
                CoreMat,
                Core,
                Lamina,
                Laminate,
                StiffenerSection,
                StructuralElement,
            ]
        ],
    ):
        if not isinstance(stuff, list):
            stuff = [stuff]
        for item in stuff:
            dictionary_of_item_type = self._sort_item(item)
            dictionary_of_item_type.update({item.name: item})

    # TODO Finish function
    def load_single_entry(self, key, value):
        """Loads a single object from serialized dict, passed as the value argument.
        The key argument is a stirng that maps to the session colections. Valid keys are:
        laminate
        panel
        stiffener_element
        stifferner_section


        """
        table = {
            "laminate": {
                "SingleSkinLaminate": SingleSkinLaminate,
                "SandwichLaminate": SandwichLaminate,
            },
            "panel": StructuralElement,
        }

        typ = table[key]
        if isinstance(typ, dict):
            typ = typ[value[TYPE_LABEL]]
        return deserialize_dataclass(
            dct=value,
            typ=typ,
            build_instance=True,
            dict_of_collections={},
        )

    def _load_list(self, list_of_values: list[dict], typ, dict_of_collections=None):
        return {
            value["name"]: deserialize_dataclass(
                dct=value,
                dataclass=typ,
                build_instance=True,
                dict_of_collections=dict_of_collections,
            )
            for value in list_of_values
        }

    def _load_list_multiple_types(
        self,
        list_of_values: list[dict],
        subtypes_table: dict,
        dict_of_collections: dict = None,
    ):
        dict_ = dict()
        for type_key, type_class in subtypes_table.items():
            list_of_values_filetered = list(
                filter(lambda item: item[TYPE_LABEL] == type_key, list_of_values)
            )
            dict_.update(
                self._load_list(
                    list_of_values=list_of_values_filetered,
                    typ=type_class,
                    dict_of_collections=dict_of_collections,
                )
            )
        return dict_

    def load_session(self, session: dict):
        if session.get("vessels"):
            self.vessels.update(
                self._load_list_multiple_types(
                    session["vessels"],
                    subtypes_table={typ.__name__: typ for typ in [Monohull, Catamaran]},
                )
            )
        if session.get("matrices"):
            self.matrices.update(self._load_list(session["matrices"], Matrix))
        if session.get("fibers"):
            self.fibers.update(self._load_list(session["fibers"], Fiber))
        if session.get("laminas"):
            self.laminas.update(
                self._load_list(
                    session["laminas"],
                    Lamina,
                    dict_of_collections=self.session_dict,
                )
            )
        if session.get("core_materials"):
            self.core_materials.update(
                self._load_list(session["core_materials"], CoreMat)
            )
        if session.get("cores"):
            self.cores.update(
                self._load_list(
                    session["cores"], Core, dict_of_collections=self.session_dict
                )
            )
        if session.get("laminates"):
            self.laminates.update(
                self._load_list_multiple_types(
                    list_of_values=session["laminates"],
                    subtypes_table={
                        typ.__name__: typ
                        for typ in [SingleSkinLaminate, SandwichLaminate]
                    },
                    dict_of_collections=self.session_dict,
                )
            )
        if session.get("stiffener_sections"):
            self.stiffener_sections.update(
                self._load_list(
                    list_of_values=session["stiffener_sections"],
                    typ=StiffenerSectionWithFoot,
                    dict_of_collections=self.session_dict,
                )
            )
        if session.get("stiffener_elements"):
            self.stiffener_elements.update(
                self._load_list(
                    list_of_values=session["stiffener_elements"],
                    typ=StructuralElement,
                    dict_of_collections=self.session_dict,
                )
            )
        if session.get("panels"):
            self.panels.update(
                self._load_list(
                    list_of_values=session["panels"],
                    typ=StructuralElement,
                    dict_of_collections=self.session_dict,
                )
            )

    def load_json(self, f):
        """Loads a json file from a IO stream"""
        d = load(f)
        self.load_session(d)

    def loads_json(self, string):
        """Loads a json string"""
        d = loads(string)
        self.load_session(d)

    def laminates_resume(self):
        """Resume of laminates properties."""
        df = pd.DataFrame()
        for laminate in self.laminates.values():
            df = pd.concat([df, laminate.resume], ignore_index=True)
        return df

    def stiffeners_resume(self):
        """Resume of laminates properties."""
        df = pd.DataFrame()
        for stiff in self.stiffener_sections.values():
            df = pd.concat([df, stiff.resume], ignore_index=True)
        return df

    def panels_rule_check(self):
        df = pd.DataFrame()
        for panel in self.panels.values():
            df = pd.concat([df, panel.rule_check], ignore_index=True)
        return df

    def stiffeners_rule_check(self):
        df = pd.DataFrame()
        for stifferner in self.stiffener_elements.values():
            df = pd.concat([df, stifferner.rule_check], ignore_index=True)
        return df

    @property
    def _pre_process_json(self):

        return {
            key: [value for value in values.values()]
            for key, values in serialize_dataclass(self).items()
        }

    def dump_json(self, file_name: str = "session.json"):
        """Dumps session to a json file.
        file_name = file path/name to write to.
        """

        with open(file_name, "w") as f:
            dump(self._pre_process_json, f)

    def dumps_json(self):
        """Dumps session to a json str."""

        return dumps(self._pre_process_json)
