from dataclasses import fields
from typing import Any
from .vessel import Vessel
from .composites import (
    ABCLaminate,
    Lamina,
    Fiber,
    LaminaMonolith,
    Matrix,
    LaminaPartsCSM,
    LaminaPartsWoven,
)
from .panels import Panel
from .locations import (
    Location,
    Bottom,
    Side,
    Deck,
    WetDeck,
    DeckHouse,
    DeckHouseMainFront,
    DeckHouseMainSide,
    DeckHouseOther,
)
from .stiffeners import LBar, StiffenerSection, Stiffener, AttStiffenerSection, LBar20
from .elements import StructuralElement

# Classes to extract input must be dataclasses, with relevant input as fields.
# Other else it is assumed that the class needs no initialization paramenters
def input_extractor(data_class, inputs: dict[str, Any]) -> dict[str, Any]:
    try:
        keys = [field.name for field in fields(data_class)]
        extracted_inputs = {key: inputs[key] for key in keys if key in inputs.keys()}
        return extracted_inputs
    except TypeError:
        return dict()


def value_substitution(
    inputs: dict[str, Any], name_dict_pairs: dict[str, dict[str, Any]]
):
    for key, dict_of_values in name_dict_pairs.items():
        inputs.update({key: dict_of_values[inputs[key]]})
    return inputs


def lamina_constructor(
    fibers: dict[str, Fiber], matrices: dict[str, Matrix], **kwargs
) -> Lamina:
    def parts_lamina_constructor(
        fibers: dict[str, Fiber], matrices: dict[str, Matrix], **kwargs
    ) -> Lamina:
        table = {"woven": LaminaPartsWoven, "csm": LaminaPartsCSM}
        lamina = table[kwargs["cloth"]]
        name_dict_pairs = {"fiber": fibers, "matrix": matrices}
        inputs = input_extractor(lamina, kwargs)
        inputs = value_substitution(inputs, name_dict_pairs)
        return lamina(**inputs)

    def monolith_lamina_constructor(**kwargs) -> Lamina:
        inputs = input_extractor(LaminaMonolith, kwargs)
        return LaminaMonolith(**inputs)

    table = {"parts": parts_lamina_constructor, "monoltih": monolith_lamina_constructor}
    constructor = table[kwargs["properties from"]]
    return constructor(fibers=fibers, matrices=matrices, **kwargs)


def panel_constructor(laminates: dict[str, ABCLaminate], **kwargs) -> Panel:
    inputs = input_extractor(Panel, kwargs)
    name_dict_pairs = {"laminate": laminates}
    inputs = value_substitution(inputs, name_dict_pairs)
    return Panel(**inputs)


def location_constructor(**kwargs) -> Location:
    table = {
        "bottom": Bottom,
        "side": Side,
        "wet deck": WetDeck,
        "deck": Deck,
        "deck house": DeckHouse,
        "deck house main front": DeckHouseMainFront,
        "deck house main side": DeckHouseMainSide,
        "deck house other": DeckHouseOther,
    }
    location = table[kwargs["location"].lower()]
    inputs = input_extractor(location, kwargs)
    return location(**inputs)


def stiffener_section_constructor(
    laminates: dict[str, ABCLaminate], **kwargs
) -> AttStiffenerSection:
    name_dict_pairs_ = {"laminate_web": laminates, "laminate_flange": laminates}
    table = {
        "lbar": (LBar, name_dict_pairs_),
        "lbar20": (LBar20, name_dict_pairs_),
    }
    stiffener_section, name_dict_pairs = table[kwargs["section_profile"].lower()]
    inputs = input_extractor(stiffener_section, kwargs)
    inputs = value_substitution(inputs, name_dict_pairs)
    return AttStiffenerSection(elmt_container=stiffener_section(**inputs))


def stiffener_att_plate_section_constructor(
    laminates: dict[str, ABCLaminate],
    stiffeners_sections: dict[str:StiffenerSection],
    **kwargs,
) -> Stiffener:
    inputs = input_extractor(Stiffener, kwargs)
    name_dict_pairs = {
        "att_plate_1": laminates,
        "att_plate_2": laminates,
        "stiff_section": stiffeners_sections,
    }
    inputs = value_substitution(inputs, name_dict_pairs)
    return Stiffener(**inputs)


def panel_element_constructor(
    vessel: Vessel,
    laminates: dict[str, ABCLaminate],
    **kwargs,
) -> StructuralElement:
    location = location_constructor(**kwargs)
    model = panel_constructor(laminates, **kwargs)
    inputs = input_extractor(StructuralElement, kwargs)
    inputs.update({"vessel": vessel, "location": location, "model": model})
    return StructuralElement(**inputs)


def stiffener_element_constructor(
    vessel,
    laminates: dict[str, ABCLaminate],
    stiffeners_sections: dict[str, StiffenerSection],
    **kwargs,
) -> StructuralElement:
    location = location_constructor(**kwargs)
    model = stiffener_att_plate_section_constructor(
        laminates, stiffeners_sections, **kwargs
    )
    inputs = input_extractor(StructuralElement, kwargs)
    inputs.update({"vessel": vessel, "location": location, "model": model})
    return StructuralElement(**inputs)


def structural_element_constructor(
    vessel: Vessel,
    laminates: dict[str, ABCLaminate],
    stiffeners_sections: dict[str, StiffenerSection],
    **kwargs,
) -> StructuralElement:
    table = {
        "panel": (panel_element_constructor, [laminates]),
        "stiffener": (stiffener_element_constructor, [laminates, stiffeners_sections]),
    }
    element_type, element_references = table[kwargs["element type"].lower()]
    return element_type(*element_references, **kwargs)
