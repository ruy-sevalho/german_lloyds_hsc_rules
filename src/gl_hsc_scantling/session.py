from dataclasses import dataclass, field, fields
from typing import Union

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
from gl_hsc_scantling.elements import StructuralElement
from gl_hsc_scantling.panels import Panel
from gl_hsc_scantling.stiffeners import (
    Stiffener,
    StiffenerSection,
    StiffenerSectionWithFoot,
)
from gl_hsc_scantling.vessel import Vessel

TYPE_LABEL = "typ"

LAMINATE_OPTIONS = DeSerializerOptions(add_type=True)
STIFFENER_OPTIONS = DeSerializerOptions(add_type=True)


@dataclass
class Session:
    vessels: dict[str, Vessel] = field(default_factory=dict)
    fibers: dict[str, Fiber] = field(default_factory=dict)
    matrices: dict[str, Matrix] = field(default_factory=dict)
    laminas: dict[str, Lamina] = field(default_factory=dict)
    laminates: dict[str, Laminate] = field(
        default_factory=dict, metadata={DESERIALIZER_OPTIONS: LAMINATE_OPTIONS}
    )
    core_materials: dict[str, CoreMat] = field(default_factory=dict)
    cores: dict[str, Core] = field(default_factory=dict)
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
            Vessel,
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
            Vessel,
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
            Vessel: self.vessels,
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
                Vessel,
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

    def _load_dict(self, dict_of_values: dict, typ, dict_of_collections=None):
        return {
            name: deserialize_dataclass(
                dct=value,
                dataclass=typ,
                build_instance=True,
                dict_of_collections=dict_of_collections,
            )
            for name, value in dict_of_values.items()
        }

    def _load_dict_multiple_types(
        self,
        dict_of_values: dict,
        subtypes_table: dict,
        dict_of_collections: dict = None,
    ):
        dict_ = dict()
        for type_key, type_class in subtypes_table.items():
            dict_of_values_filetered = dict(
                filter(
                    lambda item: item[1][TYPE_LABEL] == type_key, dict_of_values.items()
                )
            )
            dict_.update(
                self._load_dict(
                    dict_of_values=dict_of_values_filetered,
                    typ=type_class,
                    dict_of_collections=dict_of_collections,
                )
            )
        return dict_

    def load_session(self, session: dict):
        self.vessels = self._load_dict(session["vessels"], Vessel)
        self.matrices = self._load_dict(session["matrices"], Matrix)
        self.fibers = self._load_dict(session["fibers"], Fiber)
        self.laminas = self._load_dict(
            session["laminas"],
            Lamina,
            dict_of_collections=self.session_dict,
        )
        self.core_materials = self._load_dict(session["core_materials"], CoreMat)
        self.cores = self._load_dict(
            session["cores"], Core, dict_of_collections=self.session_dict
        )
        self.laminates = self._load_dict_multiple_types(
            dict_of_values=session["laminates"],
            subtypes_table={
                typ.__name__: typ for typ in [SingleSkinLaminate, SandwichLaminate]
            },
            dict_of_collections=self.session_dict,
        )
        self.stiffener_sections = self._load_dict(
            dict_of_values=session["stiffener_sections"],
            typ=StiffenerSectionWithFoot,
            dict_of_collections=self.session_dict,
        )
        self.stiffener_elements = self._load_dict(
            dict_of_values=session["stiffener_elements"],
            typ=StructuralElement,
            dict_of_collections=self.session_dict,
        )
        self.panels = self._load_dict(
            dict_of_values=session["panels"],
            typ=StructuralElement,
            dict_of_collections=self.session_dict,
        )

    def panels_rule_check(self):
        df = pd.DataFrame()
        for panel in self.panels.values():
            df = pd.concat([df, panel.rule_check])
        return df
