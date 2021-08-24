# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 12:28:58 2021

@author: ruy
"""
from collections import namedtuple
import numpy as np
from functools import cached_property, lru_cache
from typing import List
import abc

from .dc import dataclass
from .structural_model import StructuralModel, BoundaryCondition
from .vessel import Vessel
from .composites import SingleSkinLaminate, SandwichLaminate, ABCLaminate

# Point2D = namedtuple("Point2D", "y z")
Z_limits = namedtuple("Z_limits", "inf sup")


@dataclass
class Point2D:
    y: float
    z: float


def coord_transform(position: Point2D, angle: float) -> float:
    rad = np.radians(angle)
    sin = np.sin(rad)
    cos = np.cos(rad)
    z1 = sin * position.y
    z2 = cos * position.z
    return z1


# (abc.ABC)
@dataclass
class SectionElement(abc.ABC):
    """Defition of the necessary parameters that section elements of a stiffener
    must have.
    """

    @abc.abstractmethod
    def bend_stiff(self, angle=0):
        pass

    @abc.abstractproperty
    def shear_stiff(self):
        pass

    @abc.abstractmethod
    def z_limits(self, angle=0):
        pass

    @abc.abstractmethod
    def z_center(self, angle=0):
        pass


class HomogeneousSectionElement(SectionElement):
    @abc.abstractproperty
    def area(self):
        pass

    @abc.abstractmethod
    def inertia(self, angle=0):
        pass

    def bend_stiff(self, angle=0):
        return self.inertia(angle) * self.material.modulus_x

    @property
    def shear_stiff(self):
        return self.area * self.material.modulus_xy

    @property
    def stiff(self):
        return self.area * self.material.modulus_x


@dataclass
class RectSectionElement(HomogeneousSectionElement):
    material: ABCLaminate
    dimension: float

    @abc.abstractproperty
    def height():
        pass

    @abc.abstractproperty
    def width():
        pass

    def z_corners(self, angle=0):
        rad = np.radians(angle)
        sin = np.sin(rad)
        cos = np.cos(rad)
        z2 = sin * self.width
        z3 = cos * self.height
        z4 = z2 + z3
        return np.array([0, z2, z3, z4])

    def z_limits(self, angle=0):
        return Z_limits(np.min(self.z_corners(angle)), np.max(self.z_corners(angle)))

    def z_center(self, angle=0):
        return np.average(self.z_corners(angle))

    @property
    def area(self):
        return self.height * self.width

    def inertia(self, angle=0):
        rad = np.radians(angle)
        sin = np.sin(rad)
        cos = np.cos(rad)
        return (
            self.width
            * self.height
            * (self.height ** 2 * cos ** 2 + self.width ** 2 * sin ** 2)
        ) / 12


class SectionElmtRectVert(RectSectionElement):
    @property
    def height(self):
        return self.dimension

    @property
    def width(self):
        return self.material.thickness


class SectionElmtRectHoriz(RectSectionElement):
    @property
    def height(self):
        return self.material.thickness

    @property
    def width(self):
        return self.dimension


def section_elmt_factory(elmt_type):
    table = {
        "rect_vert": SectionElmtRectVert,
        "rect_horiz": SectionElmtRectHoriz,
    }
    return table[elmt_type]


@dataclass
class Elmt:
    """Section elemented positioned in a stiffener profile."""

    sect_elmt: SectionElement
    anchor_pt: Point2D = Point2D(0, 0)
    angle: float = 0
    web: bool = False


class StiffinerSection(SectionElement):
    """Stiffener profile section."""

    @property
    def web(self):
        return filter(lambda elmt: elmt.web, self.elmts)

    def z_limits(self, angle=0):
        # z_limits = [elmt.sect_elmt.z_limits(angle + elmt.angle) for elmt in self.elmts]
        return np.array(
            [
                np.min(
                    [
                        elmt.sect_elmt.z_limits(angle + elmt.angle)[0]
                        for elmt in self.elmts
                    ]
                ),
                np.max(
                    [
                        elmt.sect_elmt.z_limits(angle + elmt.angle)[1]
                        for elmt in self.elmts
                    ]
                ),
            ]
        )

    @property
    def stiff(self):
        return np.sum([elmt.sect_elmt.stiff for elmt in self.elmts])

    def z_elmt(self, elmt, angle=0):
        return elmt.sect_elmt.z_center(angle + elmt.angle) + coord_transform(
            elmt.anchor_pt, angle
        )

    def sum_stiffz(self, angle=0):
        return np.sum(
            [elmt.sect_elmt.stiff * self.z_elmt(elmt, angle) for elmt in self.elmts]
        )

    def z_center(self, angle=0):
        return self.sum_stiffz(angle) / self.stiff

    def bend_stiff_bottom(self, angle=0):
        return np.sum(
            [
                elmt.sect_elmt.bend_stiff(angle)
                + (elmt.sect_elmt.stiff * self.z_elmt(elmt, angle) ** 2)
                for elmt in self.elmts
            ]
        )

    def bend_stiff(self, angle=0):
        return self.bend_stiff_bottom(angle) - self.z_center(angle) ** 2 * self.stiff

    @property
    def shear_stiff(self):
        return np.sum([elmt.sect_elmt.shear_stiff for elmt in self.web])


@dataclass
class LBar(StiffinerSection):
    """L bar profile - composed of a web and a flange."""

    name: str
    laminate_web: ABCLaminate
    dimension_web: float
    laminate_flange: ABCLaminate
    dimension_flange: float

    @property
    def elmts(self):
        elmts = [
            Elmt(SectionElmtRectVert(self.laminate_web, self.dimension_web), web=True),
            Elmt(
                SectionElmtRectHoriz(self.laminate_flange, self.dimension_flange),
                anchor_pt=(0, self.dimension_web),
            ),
        ]
        return elmts

    @property
    def foot_width(self):
        return self.elmts[0].sect_elmt.width


def stiff_section_factory(sect_type, laminates, **definition):
    table = {"l bar": LBar}
    definition["laminate_web"] = laminates[definition["laminate_web"]]
    definition["laminate_flange"] = laminates[definition["laminate_flange"]]
    return table[sect_type](**definition)


@dataclass
class AttPlateSandwich(StiffinerSection):
    """Sandwich attached plate section."""

    dimension: float
    laminate: ABCLaminate

    @property
    def elmts(self):
        z_inner = self.laminate.thickness - self.laminate.skins[1].thickness
        anchors = [(0, 0), (0, z_inner)]
        return [
            Elmt(SectionElmtRectHoriz(skin, self.dimension), anchor_pt=anchor)
            for skin, anchor in zip(self.laminate.skins, anchors)
        ]


@dataclass
class AttPlateSS(StiffinerSection):
    """Single Skin attached plate section."""

    dimension: float
    laminate: ABCLaminate

    @property
    def elmts(self):
        return [Elmt(SectionElmtRectHoriz(self.laminate, self.dimension))]


@dataclass
class ComposedSection(StiffinerSection):
    """Stiff section composed of other stiff sections"""

    elmts: List[SectionElement]


def att_plate_section_factory(lam_type):
    table = {SingleSkinLaminate: AttPlateSS, SandwichLaminate: AttPlateSandwich}
    return table[lam_type]


@dataclass
class Stiffener(StructuralModel):
    """ """

    stiff_section: StiffinerSection
    span: float
    spacing_1: float
    spacing_2: float
    stiff_att_plate: int
    stiff_att_angle: float
    att_plate_1: ABCLaminate
    att_plate_2: ABCLaminate
    bound_cond: BoundaryCondition = BoundaryCondition.FIXED

    @property
    def spacings(self):
        return np.array([self.spacing_1, self.spacing_2])

    @property
    def spacing(self):
        return np.sum(self.spacings)

    @property
    def area(self):
        return self.span * self.spacing

    @property
    def att_plates_lam(self):
        return [self.att_plate_1, self.att_plate_2]

    @property
    def eff_widths(self):
        xp = list(range(10))
        fp = [0, 0.36, 0.64, 0.82, 0.91, 0.96, 0.98, 0.993, 0.998, 1]
        weffs = [
            np.interp(self.length_bet_mom / self.spacing, xp, fp) * spacing
            for spacing in self.spacings
        ]
        index = self.stiff_att_plate - 1
        weffs[index] = np.min(
            [self.spacings[index], weffs[index] + self.stiff_section.foot_width]
        )
        return weffs

    @property
    def length_bet_mom(self):
        table = {
            BoundaryCondition.FIXED: 0.4 * self.span,
            BoundaryCondition.SIMPLY_SUPPORTED: self.span,
        }
        return table[self.bound_cond]

    @property
    def stiff_section_att_plate(self):
        return ComposedSection(
            [
                Elmt(att_plate_section_factory(type(laminate))(laminate, dimension))
                for laminate, dimension in zip(self.att_plates_lam, self.eff_widths)
            ]
            + [
                Elmt(
                    self.stiff_section,
                    anchor_pt=(
                        0,
                        self.att_plates_lam[self.stiff_att_plate - 1].thickness,
                    ),
                    angle=self.stiff_att_angle,
                    web=True,
                )
            ]
        )
