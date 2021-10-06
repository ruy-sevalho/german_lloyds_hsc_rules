from dataclasses import fields
from typing import Any
from .composites import ABCLaminate
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
from .stiffeners import (
    LBar,
    StiffinerSection,
    Stiffener,
)
from .elements import StructuralElement


def input_extractor(data_class, inputs: dict[str:Any]) -> dict[str:Any]:
    keys = [field.name for field in fields(data_class)]
    extracted_inputs = {key: inputs[key] for key in keys if key in inputs.keys()}
    return extracted_inputs


def value_substitution(
    inputs: dict[str:Any], name_dict_pairs: dict[str : dict[str:Any]]
):
    for key, dict_of_values in name_dict_pairs.items():
        inputs.update({key: dict_of_values[inputs[key]]})
    return inputs


def panel_constructor(laminates: dict[str:ABCLaminate], **kwargs) -> Panel:
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
    laminates: dict[str:ABCLaminate], **kwargs
) -> StiffinerSection:
    table = {
        "lbar": LBar,
    }
    stiffener_section = table[kwargs["location"].lower()]
    inputs = input_extractor(stiffener_section, kwargs)
    return stiffener_section(**inputs)


def stiffener_element_constructor(
    laminates: dict[str:ABCLaminate],
    stiffeners_sections: dict[str:StiffinerSection],
    **kwargs,
) -> Stiffener:
    inputs = input_extractor(Stiffener, kwargs)
    name_dict_pairs = {"laminate": laminates, "stiffener section": stiffeners_sections}
    inputs = value_substitution(inputs, name_dict_pairs)
    return Stiffener(**inputs)


def structural_element_constructor(
    vessel,
    laminates: dict[str:ABCLaminate],
    stiffeners_sections: dict[str:StiffinerSection],
    **kwargs,
) -> StructuralElement:
    table = {
        "panel": (panel_constructor, [laminates]),
        "stiffener": (stiffener_element_constructor, [laminates, stiffeners_sections]),
    }
    location = location_constructor(**kwargs)
    model_type = table[kwargs["element type"].lower()]
    model = model_type[0](*model_type[1], **kwargs)
    inputs = input_extractor(StructuralElement, kwargs)
    inputs.update({"vessel": vessel, "location": location, "model": model})
    return StructuralElement(**inputs)