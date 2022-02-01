# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 10:46:30 2021

@author: ruy
"""
from dataclasses import dataclass
from typing import Any, Optional

from pylatex import NoEscape


@dataclass
class NamePrint:
    """Strings for printing value name."""

    long: str
    abbr: str


@dataclass
class PrintWrapper:
    """Print wrapper for string or quantity values."""

    value: Any
    names: NamePrint

@dataclass
class PrintMetadata:
    names: NamePrint
    units: Optional[str] = None
    

METADATA = {
    # Name
    "name": {"names": NamePrint("Name", "Name")},
    # Vessel
    "speed": {"names": NamePrint("Speed", "S"), "units": "kt"},
    "vert_acg": {
        "names": NamePrint("Vertical acceleration", NoEscape(r"a\textsubscript{CG}")),
        "units": "g",
    },
    "transverse_bending_moment": {
        "names": NamePrint(
            "Transverse bending moment", NoEscape(r"M\textsubscript{bt}")
        ),
        "units": "kN",
    },
    "transverse_torsional_moment": {
        "names": NamePrint(
            "Transverse torsional moment", NoEscape(r"M\textsubscript{tt}")
        ),
        "units": "kN",
    },
    "shear_force": {
        "names": NamePrint("Shear force", NoEscape(r"T\textsubscript{bt}")),
        "units": "kN",
    },
    "length": {"names": NamePrint("Length", "L"), "units": "m"},
    "displacement": {
        "names": NamePrint("Displacement", NoEscape(r"$\Delta$")),
        "units": "t",
    },
    "beam": {"names": NamePrint("Beam", "B"), "units": "m"},
    "draft": {"names": NamePrint("Draft", "H"), "units": "m"},
    "fwd_perp": {
        "names": NamePrint("Foward perpendicular", NoEscape(r"F\textsubscript{P}")),
        "units": "m",
    },
    "aft_perp": {
        "names": NamePrint("Aft perpendicular", NoEscape(r"A\textsubscript{P}")),
        "units": "m",
    },
    "z_baseline": {
        "names": NamePrint(
            "z coordinate of baseline",
            NoEscape(r"z\textsubscript{BL}"),
        ),
        "units": "m",
    },
    "dist_hull_cl": {
        "names": NamePrint(
            "Distance between hulls centerline", NoEscape(r"B\textsubscript{CL}")
        ),
        "units": "m",
    },
    "lcg": {
        "names": NamePrint(
            "Longitudinal center of gravity", NoEscape(r"L\textsubscript{CG}")
        ),
        "units": "m",
    },
    "service_range": {"names": NamePrint("Service range", "SR")},
    "type_of_service": {"names": NamePrint("Type of service", "ToS")},
    "block_coef": {
        "names": NamePrint("Block coefficient", NoEscape(r"C\textsubscript{B}")),
        "units": "",
    },
    "water_plane_area": {
        "names": NamePrint("Water plane area", NoEscape(r"WP\textsubscript{A}")),
        "units": "m**2",
    },
    "deadrise_lcg": {
        "names": NamePrint(
            NoEscape(r"Deadrise at longitudinal center of gravity"),
            NoEscape(r"$\alpha$\textsubscript{d}"),
        ),
        "units": "degree",
    },
    # Material properties
    "density": {"names": NamePrint("density", NoEscape(r"$\rho$")), "units": "kg/m**3"},
    "modulus_x": {
        "names": NamePrint("Modulus - x direction", NoEscape(r"E\textsubscript{x}")),
        "units": "kPa",
    },
    "modulus_y": {
        "names": NamePrint("Modulus - y direction", NoEscape(r"E\textsubscript{y}")),
        "units": "kPa",
    },
    "modulus_xy": {
        "names": NamePrint(
            "Modulus - shear in xy plane", NoEscape(r"G\textsubscript{xy}")
        ),
        "units": "kPa",
    },
    "poisson": {
        "names": NamePrint("Poisson", NoEscape(r"$\nu$")),
        "units": "",
    },
    "poisson_xy": {
        "names": NamePrint("Poisson xy", NoEscape(r"$\nu$\textsubscript{xy}")),
        "units": "",
    },
    "poisson_yx": {
        "names": NamePrint("Poisson yx", NoEscape(r"$\nu$\textsubscript{yx}")),
        "units": "",
    },
    "thickness": {
        "names": NamePrint("thickness", "t"),
        "units": "m",
    },
    "f_mass_cont": {
        "names": NamePrint("Fiber mass content", NoEscape(r"$\psi$")),
        "units": "percent",
    },
    "f_area_density": {
        "names": NamePrint("Fiber area density", NoEscape(r"f\textsubscript{d}")),
        "units": "percent",
    },
    "max_strain_x": {
        "names": NamePrint(
            "Limit linear strain",
            NoEscape(r"max $\epsilon\textsubscript{x}"),
        ),
        "units": "",
    },
    "max_strain_xy": {
        "names": NamePrint(
            "Limit shear strain",
            NoEscape(r"max $\epsilon\textsubscript{xy}"),
        ),
        "units": "",
    },
    "fiber": {
        "names": NamePrint(
            "Fiber",
            "Fiber",
        ),
    },
    "matrix": {
        "names": NamePrint(
            "Matrix",
            "Matrix",
        ),
    },
    "laminate": {
        "names": NamePrint(
            "Laminate",
            "Laminate",
        ),
    },
    "material": {
        "names": NamePrint(
            "Material",
            "Material",
        ),
    },
    "orientation": {
        "names": NamePrint(
            "Orientation",
            NoEscape(r"$\theta"),
        ),
        "units": "degree",
    },
}


# def _metadata(names, metadata=METADATA):
#     return dict(filter(lambda item: item[0] in names, metadata.items()))
