# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 12:28:58 2021

@author: ruy
"""
import abc
from dataclasses import astuple, dataclass, field, fields
from itertools import chain
from functools import cached_property as property

import numpy as np
import pandas as pd
from dataclass_tools.tools import (
    DESERIALIZER_OPTIONS,
    DeSerializerOptions,
    PrintMetadata,
)
from quantities import Quantity

from gl_hsc_scantling.utils import Criteria

from .common_field_options import (
    ATT_PLATE_1_OPTIONS,
    ATT_PLATE_2_OPTIONS,
    BOUND_COND_OPTIONS,
    CURVATURE_OPTIONS,
    DIMENSION_FLANGE_OPTIONS,
    DIMENSION_WEB_OPTIONS,
    LAMINATE_FLANGE_OPTIONS,
    LAMINATE_OPTIONS,
    LAMINATE_WEB_OPTIONS,
    NAME_OPTIONS,
    SPACING_1_OPTIONS,
    SPACING_2_OPTIONS,
    SPAN_OPTIONS,
    STIFF_ATT_ANGLE_OPTIONS,
    STIFF_ATT_PLATE_OPTIONS,
)
from .composites import Laminate, SandwichLaminate, SingleSkinLaminate
from .structural_model import BoundaryCondition, StructuralModel


class DimensionalData:
    def __add__(self, other):
        return self.__class__(
            *(
                getattr(self, dim.name) + getattr(other, dim.name)
                for dim in fields(self)
            )
        )

    def __sub__(self, other):
        return self.__class__(
            *(
                getattr(self, dim.name) - getattr(other, dim.name)
                for dim in fields(self)
            )
        )

    def __mul__(self, other):
        # waiting for numpy to be avaliable for python 3.10 to use pattern matching
        if isinstance(other, self.__class__):
            return self.__class__(
                *(
                    getattr(self, dim.name) * getattr(other, dim.name)
                    for dim in fields(self)
                )
            )
        else:
            try:
                other = float(other)
            except ValueError:
                raise TypeError(
                    f"unsupported operand type(s) for *: '{type(self).__name__}' and '{type(other).__name__}'"
                )
            return self.__class__(
                *(getattr(self, dim.name) * other for dim in fields(self))
            )

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        # waiting for numpy to be avaliable for python 3.10 to use pattern matching
        if isinstance(other, self.__class__):
            return self.__class__(
                *(
                    getattr(self, dim.name) / getattr(other, dim.name)
                    for dim in fields(self)
                )
            )
        else:
            try:
                other = float(other)
            except ValueError:
                raise TypeError(
                    f"unsupported operand type(s) for *: '{type(self).__name__}' and '{type(other).__name__}'"
                )
            return self.__class__(
                *(getattr(self, dim.name) / other for dim in fields(self))
            )

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __iter__(self):
        return iter(astuple(self))


@dataclass
class Point2D(DimensionalData):
    y: float
    z: float


@dataclass
class Inertia(DimensionalData):
    """Container class for 2D section's moments of inertia (m4)."""

    y: float
    z: float


@dataclass
class BendStiff(DimensionalData):
    """Container class for 2D section's bending stiffness (kN m2)."""

    y: float
    z: float


def _coord_transform(position: Point2D, angle: float) -> Point2D:
    rad = np.radians(angle)
    sin = np.sin(rad)
    cos = np.cos(rad)
    z = cos * position.z + sin * position.y
    y = -sin * position.z + cos * position.y
    return Point2D(y, z)


class SectionElement(abc.ABC):
    @abc.abstractmethod
    def bend_stiff(self, angle=0) -> BendStiff:
        """Bending stiffness with respect to y (main)
        and z (secondary) directions - E*I (kPa*m4).
        Section rotaded given angle.
        """

    @property
    def bend_stiff_0(self) -> BendStiff:
        """Bending stiffness with respect to y (main)
        and z (secondary) directions - E*I (kPa*m4).
        Rotation angle = 0.
        """
        return self.bend_stiff()

    @abc.abstractproperty
    def stiff(self) -> float:
        """Extensional stiffness E*A (kPa*m??)."""

    @abc.abstractproperty
    def shear_stiff(self) -> float:
        """Shear stiffness G*A (kPa*m??)"""

    @abc.abstractmethod
    def center(self, angle=0) -> Point2D:
        """P(y,z) - element's centroid (m)
        in which the local coordinate system
        is rotaded. Rotation angle in degrees.
        """

    @property
    def center_0(self) -> Point2D:
        return self.center()

    @abc.abstractmethod
    def limit_z_points(self, angle=0) -> list[Point2D]:
        """Resturns the 2D points whit the lowes and highest z coordinates."""

    @property
    def limit_z_points_0(self):
        return self.limit_z_points()

    def limit_z_anchor_pt(self, angle: float = 0) -> list[float]:
        return [pt.z for pt in self.limit_z_points(angle=angle)]

    def limit_z_center(self, angle: float = 0) -> list[float]:
        return self.limit_z_anchor_pt(angle) - self.center(angle).z

    def linear_strain(self, bend_moment: float, angle: float = 0):
        bend_stiff = self.bend_stiff(angle=angle).y
        return np.array(
            [bend_moment * z / bend_stiff for z in self.limit_z_anchor_pt(angle=angle)]
        )

    def shear_strain_web(self, shear_force: float) -> float:
        return shear_force / (self.shear_stiff)


class HomogeneousSectionElement(SectionElement):
    """Defition of the necessary parameters that section elements of a stiffener
    must have.
    """

    @abc.abstractproperty
    def area(self) -> float:
        """Area (m??)."""

    @abc.abstractmethod
    def inertia(self, angle=0) -> Inertia:
        """Area moment of inertia container with respect y (main)
        and z (secondary) directions - I (m4).
        Local coordinate system rotaded. Rotation angle in degrees.
        """

    @abc.abstractproperty
    def density(self) -> float:
        """Density of section element kg/m3."""

    @property
    def linear_density(self) -> float:
        """Area density of section element kg/m2."""
        return self.area * self.density


@dataclass
class RectSectionElement(HomogeneousSectionElement):
    """Rectangular element, with local centroid at the mid witdth at height 0."""

    laminate: Laminate
    dimension: float

    @property
    def density(self) -> float:
        return self.laminate.area_density / self.laminate.thickness

    def bend_stiff(self, angle=0) -> BendStiff:
        return BendStiff(*self.inertia(angle) * self.laminate.modulus_x)

    @property
    def stiff(self) -> float:
        return self.area * self.laminate.modulus_x

    @property
    def shear_stiff(self) -> float:
        return self.area * self.laminate.modulus_xy

    @abc.abstractproperty
    def height() -> float:
        pass

    @abc.abstractproperty
    def width() -> float:
        pass

    def _corners(self, angle=0) -> list[Point2D]:
        """Returns a np.array with z coordinates of corner with respect to rotated
        coordinete system. Angle in degress.
        """
        y = self.width / 2
        z = self.height
        corners = [Point2D(y, 0), Point2D(y, z), Point2D(-y, z), Point2D(-y, 0)]
        return [_coord_transform(corner, angle) for corner in corners]

    def limit_z_points(self, angle=0) -> list[Point2D]:
        z = np.array([pt.z for pt in self._corners(angle=angle)])
        indexes = [np.argmin(z), np.argmax(z)]
        return [self._corners(angle)[i] for i in indexes]

    def center(self, angle=0) -> Point2D:
        return _coord_transform(Point2D(0, self.height / 2), angle)

    @property
    def area(self) -> float:
        return self.height * self.width

    def _inertia(self, width, height, angle=0) -> float:
        rad = np.radians(angle)
        sin = np.sin(rad)
        cos = np.cos(rad)
        return (width * height * (height**2 * cos**2 + width**2 * sin**2)) / 12

    def inertia(self, angle=0) -> Inertia:
        return Inertia(
            self._inertia(width=self.width, height=self.height, angle=angle),
            self._inertia(width=self.height, height=self.width, angle=angle),
        )


class SectionElmtRectVert(RectSectionElement):
    @property
    def height(self) -> float:
        return self.dimension

    @property
    def width(self) -> float:
        return self.laminate.thickness


class SectionElmtRectHoriz(RectSectionElement):
    @property
    def height(self):
        return self.laminate.thickness

    @property
    def width(self):
        return self.dimension


@dataclass
class Elmt(SectionElement):
    """Section elemented positioned in a stiffener profile."""

    sect_elmt: HomogeneousSectionElement
    anchor_pt: Point2D = Point2D(y=0, z=0)
    angle: float = 0
    web: bool = False

    def center(self, angle=0) -> Point2D:
        """Centroid of element"""
        return self.sect_elmt.center(angle + self.angle) + self.rotaded_anchor_pt(angle)

    def rotaded_anchor_pt(self, angle: float = 0):
        return _coord_transform(self.anchor_pt, angle)

    def limit_z_points(self, angle=0) -> list[Point2D]:
        a = self.rotaded_anchor_pt(self.angle + angle)
        l = [limit_pt for limit_pt in self.sect_elmt.limit_z_points(angle)]
        return [
            limit_pt + self.rotaded_anchor_pt(self.angle + angle)
            for limit_pt in self.sect_elmt.limit_z_points(angle)
        ]

    # Output is not really a 2d point, but it works
    def stiff_weighted_center(self, angle=0) -> Point2D:
        return self.center(angle) * self.sect_elmt.stiff

    @property
    def stiff_weighted_center_0(self):
        return self.stiff_weighted_center()

    def stiff_double_weighted_center(self, angle=0) -> Point2D:
        return self.stiff_weighted_center(angle) * self.center(angle)

    @property
    def stiff_double_weighted_center_0(self):
        return self.stiff_double_weighted_center()

    def bend_stiff(self, angle=0) -> BendStiff:
        return self.sect_elmt.bend_stiff(angle + self.angle)

    @property
    def bend_stiff_0(self) -> BendStiff:
        return self.bend_stiff()

    def bend_stiff_base(self, angle=0) -> BendStiff:
        bend_transf = self.stiff_double_weighted_center(angle)
        # y and z switched due to moment of inertia defintion
        bend_transf = BendStiff(bend_transf.z, bend_transf.y)
        return self.bend_stiff(angle) + bend_transf

    @property
    def bend_stiff_base_0(self):
        return self.bend_stiff_base()

    @property
    def shear_stiff(self) -> float:
        return self.sect_elmt.shear_stiff

    @property
    def stiff(self) -> float:
        return self.sect_elmt.stiff

    @property
    def linear_density(self) -> float:
        return self.sect_elmt.linear_density


class SectionElementList(abc.ABC):
    @abc.abstractproperty
    def elmts(self) -> list[Elmt]:
        """List of placed section elements, defining a section."""


@dataclass
class SectionElementListChain(SectionElementList):
    elmt_lists: list[SectionElementList]

    @property
    def elmts(self) -> list[Elmt]:
        return list(chain(*[elmt.elmts for elmt in self.elmt_lists]))


@dataclass
class SectionElementListWithFoot(SectionElementList):
    name: str

    @abc.abstractproperty
    def foot_width(self):
        """Width of stiffener base - counts for attached plate
        effective width.
        """

    @abc.abstractmethod
    def shear_buckling_strain(self, length: float) -> float:
        """C3.8.6.3 Buckling of orthotropic plates under
        in-plane shear loads.
        """


@dataclass
class StiffenerSection(SectionElement):
    """Stiffener section composed of stiffeners sections elements."""

    elmt_container: SectionElementList

    @property
    def elmts(self):
        return self.elmt_container.elmts

    @property
    def web(self) -> list[Elmt]:
        return filter(lambda elmt: elmt.web, self.elmts)

    @property
    def stiff(self):
        return np.sum([elmt.sect_elmt.stiff for elmt in self.elmts])

    def limit_z_points(self, angle=0) -> list[Point2D]:
        z__limts = np.array([elmt.limit_z_anchor_pt(angle) for elmt in self.elmts])
        z__limts = z__limts.reshape(2, len(z__limts))
        z_limit_points = [elmt.limit_z_points(angle) for elmt in self.elmts]
        idx = [np.argmin(z__limts[0]), np.argmax(z__limts[1])]
        return [z_limit_points[i][j] for j, i in enumerate(idx)]

    def center(self, angle=0) -> Point2D:
        return (
            np.sum([elmt.center(angle) * elmt.sect_elmt.stiff for elmt in self.elmts])
            / self.stiff
        )

    def bend_stiff_base(self, angle=0) -> BendStiff:
        return BendStiff(*np.sum([elmt.bend_stiff_base(angle) for elmt in self.elmts]))

    def bend_stiff(self, angle=0) -> BendStiff:
        bend_stiff_base = self.bend_stiff_base(angle)
        center = self.center(angle)
        bend_stiff_y = bend_stiff_base.y - self.stiff * center.z**2
        bend_stiff_z = bend_stiff_base.z - self.stiff * center.y**2
        return BendStiff(bend_stiff_y, bend_stiff_z)

    @property
    def shear_stiff(self):
        return np.sum([elmt.sect_elmt.shear_stiff for elmt in self.web])

    @property
    def linear_density(self) -> float:
        return sum([elmt.linear_density for elmt in self.elmts])

    @property
    def resume(self):
        return pd.DataFrame(
            {
                "name": [self.name],
                "linear_density": [Quantity(self.linear_density, "kg/m")],
                "bend_stiff": [Quantity(self.bend_stiff_0.y, "kN*m**2")],
                "shear_stiff": [Quantity(self.shear_stiff, "kN")],
            }
        )


@dataclass
class LBar(SectionElementListWithFoot):
    """L bar profile - composed of a web and a flange. Dimensions in m."""

    laminate_web: Laminate = field(
        metadata={DESERIALIZER_OPTIONS: LAMINATE_WEB_OPTIONS}
    )
    dimension_web: float = field(metadata={DESERIALIZER_OPTIONS: DIMENSION_WEB_OPTIONS})
    laminate_flange: Laminate = field(
        metadata={DESERIALIZER_OPTIONS: LAMINATE_FLANGE_OPTIONS}
    )
    dimension_flange: float = field(
        metadata={DESERIALIZER_OPTIONS: DIMENSION_FLANGE_OPTIONS}
    )
    name: str = field(metadata={DESERIALIZER_OPTIONS: NAME_OPTIONS})

    @property
    def elmts(self) -> list[Elmt]:
        if isinstance(self.laminate_web, SingleSkinLaminate):
            web_elements = [
                Elmt(
                    SectionElmtRectVert(self.laminate_web, self.dimension_web), web=True
                )
            ]
        elif isinstance(self.laminate_web, SandwichLaminate):
            web_elements = [
                Elmt(
                    SectionElmtRectVert(
                        self.laminate_web.outter_laminate, self.dimension_web
                    ),
                    web=True,
                    anchor_pt=Point2D(
                        -(
                            self.laminate_web.core.thickness
                            + self.laminate_web.outter_laminate.thickness
                        )
                        / 2,
                        0,
                    ),
                ),
                Elmt(
                    SectionElmtRectVert(
                        self.laminate_web.inner_laminate, self.dimension_web
                    ),
                    web=True,
                    anchor_pt=Point2D(
                        (
                            self.laminate_web.core.thickness
                            + self.laminate_web.outter_laminate.thickness
                        )
                        / 2,
                        0,
                    ),
                ),
            ]

        return web_elements + [
            Elmt(
                SectionElmtRectHoriz(self.laminate_flange, self.dimension_flange),
                anchor_pt=Point2D(
                    (self.dimension_flange - self.laminate_web.thickness) / 2,
                    self.dimension_web,
                ),
            ),
        ]

    @property
    def foot_width(self) -> float:
        return self.laminate_web.thickness

    def shear_buckling_strain(self, length: float) -> float:
        return self.laminate_web.buckling_shear_strain(self.dimension_web, length)


@dataclass
class TopHat(SectionElementListWithFoot):
    """L bar profile - composed of a web and a flange. Dimensions in m."""

    laminate_web: SingleSkinLaminate = field(
        metadata={DESERIALIZER_OPTIONS: LAMINATE_WEB_OPTIONS}
    )
    dimension_web: float = field(metadata={DESERIALIZER_OPTIONS: DIMENSION_WEB_OPTIONS})
    laminate_flange: SingleSkinLaminate = field(
        metadata={DESERIALIZER_OPTIONS: LAMINATE_FLANGE_OPTIONS}
    )
    dimension_flange: float = field(
        metadata={DESERIALIZER_OPTIONS: DIMENSION_FLANGE_OPTIONS}
    )
    name: str = field(metadata={DESERIALIZER_OPTIONS: NAME_OPTIONS})

    @property
    def elmts(self) -> list[Elmt]:
        web_elements = [
            Elmt(
                SectionElmtRectVert(self.laminate_web, self.dimension_web),
                web=True,
                anchor_pt=Point2D(-self.dimension_flange / 2, 0),
            ),
            Elmt(
                SectionElmtRectVert(self.laminate_web, self.dimension_web),
                web=True,
                anchor_pt=Point2D(self.dimension_flange / 2, 0),
            ),
        ]
        return web_elements + [
            Elmt(
                SectionElmtRectHoriz(self.laminate_flange, self.dimension_flange),
                anchor_pt=Point2D(
                    0,
                    self.dimension_web,
                ),
            ),
        ]

    @property
    def foot_width(self) -> float:
        return self.dimension_flange

    def shear_buckling_strain(self, length: float) -> float:
        return self.laminate_web.buckling_shear_strain(self.dimension_web, length)


@dataclass
class FlatBar(SectionElementListWithFoot):
    """I bar profile - composed of a web only. Dimensions in m."""

    laminate_web: Laminate = field(
        metadata={DESERIALIZER_OPTIONS: LAMINATE_WEB_OPTIONS}
    )
    dimension_web: float = field(metadata={DESERIALIZER_OPTIONS: DIMENSION_WEB_OPTIONS})

    name: str = field(metadata={DESERIALIZER_OPTIONS: NAME_OPTIONS})

    @property
    def elmts(self) -> list[Elmt]:
        if isinstance(self.laminate_web, SingleSkinLaminate):
            web_elements = [
                Elmt(
                    SectionElmtRectVert(self.laminate_web, self.dimension_web), web=True
                )
            ]
        elif isinstance(self.laminate_web, SandwichLaminate):
            web_elements = [
                Elmt(
                    SectionElmtRectVert(
                        self.laminate_web.outter_laminate, self.dimension_web
                    ),
                    web=True,
                    anchor_pt=Point2D(
                        -(
                            self.laminate_web.core.thickness
                            + self.laminate_web.outter_laminate.thickness
                        )
                        / 2,
                        0,
                    ),
                ),
                Elmt(
                    SectionElmtRectVert(
                        self.laminate_web.inner_laminate, self.dimension_web
                    ),
                    web=True,
                    anchor_pt=Point2D(
                        (
                            self.laminate_web.core.thickness
                            + self.laminate_web.outter_laminate.thickness
                        )
                        / 2,
                        0,
                    ),
                ),
            ]

        return web_elements

    @property
    def foot_width(self) -> float:
        return self.laminate_web.thickness

    def shear_buckling_strain(self, length: float) -> float:
        return self.laminate_web.buckling_shear_strain(self.dimension_web, length)


@dataclass
class OpenU(SectionElementListWithFoot):
    """L bar profile - composed of a web and a flange. Dimensions in m."""

    laminate_web: Laminate = field(
        metadata={DESERIALIZER_OPTIONS: LAMINATE_WEB_OPTIONS}
    )
    dimension_web: float = field(metadata={DESERIALIZER_OPTIONS: DIMENSION_WEB_OPTIONS})
    laminate_flange: Laminate = field(
        metadata={DESERIALIZER_OPTIONS: LAMINATE_FLANGE_OPTIONS}
    )
    dimension_flange: float = field(
        metadata={DESERIALIZER_OPTIONS: DIMENSION_FLANGE_OPTIONS}
    )
    name: str = field(metadata={DESERIALIZER_OPTIONS: NAME_OPTIONS})

    @property
    def elmts(self) -> list[Elmt]:
        if isinstance(self.laminate_web, SingleSkinLaminate):
            web_elements = [
                Elmt(
                    SectionElmtRectVert(self.laminate_web, self.dimension_web),
                    web=True,
                    anchor_pt=Point2D(-self.dimension_flange / 2, 0),
                ),
                Elmt(
                    SectionElmtRectVert(self.laminate_web, self.dimension_web),
                    web=True,
                    anchor_pt=Point2D(self.dimension_flange / 2, 0),
                ),
            ]
        elif isinstance(self.laminate_web, SandwichLaminate):
            y_inner = (
                self.dimension_flange / 2
                - self.laminate_web.thickness_eff / 2
                - self.laminate_web.core.thickness
            )
            web_elements = [
                Elmt(
                    SectionElmtRectVert(
                        self.laminate_web.outter_laminate, self.dimension_web
                    ),
                    web=True,
                    anchor_pt=Point2D(-self.dimension_flange / 2, 0),
                ),
                Elmt(
                    SectionElmtRectVert(
                        self.laminate_web.inner_laminate, self.dimension_web
                    ),
                    web=True,
                    anchor_pt=Point2D(
                        -y_inner,
                        0,
                    ),
                ),
                Elmt(
                    SectionElmtRectVert(
                        self.laminate_web.inner_laminate, self.dimension_web
                    ),
                    web=True,
                    anchor_pt=Point2D(y_inner, 0),
                ),
                Elmt(
                    SectionElmtRectVert(
                        self.laminate_web.outter_laminate, self.dimension_web
                    ),
                    web=True,
                    anchor_pt=Point2D(self.dimension_flange / 2, 0),
                ),
            ]
        if isinstance(self.laminate_flange, SingleSkinLaminate):
            flange_elements = [
                Elmt(
                    SectionElmtRectHoriz(
                        laminate=self.laminate_flange, dimension=self.dimension_flange
                    ),
                    anchor_pt=Point2D(0, self.dimension_web),
                )
            ]
        elif isinstance(self.laminate_flange, SandwichLaminate):
            flange_elements = [
                Elmt(
                    SectionElmtRectHoriz(
                        laminate=self.laminate_flange.inner_laminate,
                        dimension=self.dimension_flange,
                    ),
                    anchor_pt=Point2D(0, self.dimension_web),
                ),
                Elmt(
                    SectionElmtRectHoriz(
                        laminate=self.laminate_flange.outter_laminate,
                        dimension=self.dimension_flange,
                    ),
                    anchor_pt=Point2D(
                        0,
                        self.dimension_web
                        + self.laminate_flange.outter_laminate.thickness
                        + self.laminate_flange.core.thickness,
                    ),
                ),
            ]
        return web_elements + flange_elements

    @property
    def foot_width(self) -> float:
        return self.dimension_flange

    def shear_buckling_strain(self, length: float) -> float:
        return self.laminate_web.buckling_shear_strain(self.dimension_web, length)


@dataclass
class ClosedU(SectionElementListWithFoot):
    """L bar profile - composed of a web and a flange. Dimensions in m."""

    laminate_web: Laminate = field(
        metadata={DESERIALIZER_OPTIONS: LAMINATE_WEB_OPTIONS}
    )
    dimension_web: float = field(metadata={DESERIALIZER_OPTIONS: DIMENSION_WEB_OPTIONS})
    laminate_flange: Laminate = field(
        metadata={DESERIALIZER_OPTIONS: LAMINATE_FLANGE_OPTIONS}
    )
    dimension_flange: float = field(
        metadata={DESERIALIZER_OPTIONS: DIMENSION_FLANGE_OPTIONS}
    )
    laminate_flange_lower: SingleSkinLaminate = field(
        metadata={DESERIALIZER_OPTIONS: LAMINATE_FLANGE_OPTIONS}
    )
    name: str = field(metadata={DESERIALIZER_OPTIONS: NAME_OPTIONS})

    @property
    def elmts(self) -> list[Elmt]:
        if isinstance(self.laminate_web, SingleSkinLaminate):
            web_elements = [
                Elmt(
                    SectionElmtRectVert(self.laminate_web, self.dimension_web),
                    web=True,
                    anchor_pt=Point2D(-self.dimension_flange / 2, 0),
                ),
                Elmt(
                    SectionElmtRectVert(self.laminate_web, self.dimension_web),
                    web=True,
                    anchor_pt=Point2D(self.dimension_flange / 2, 0),
                ),
            ]
        elif isinstance(self.laminate_web, SandwichLaminate):
            y_inner = (
                self.dimension_flange / 2
                - self.laminate_web.thickness_eff / 2
                - self.laminate_web.core.thickness
            )
            web_elements = [
                Elmt(
                    SectionElmtRectVert(
                        self.laminate_web.outter_laminate, self.dimension_web
                    ),
                    web=True,
                    anchor_pt=Point2D(-self.dimension_flange / 2, 0),
                ),
                Elmt(
                    SectionElmtRectVert(
                        self.laminate_web.inner_laminate, self.dimension_web
                    ),
                    web=True,
                    anchor_pt=Point2D(
                        -y_inner,
                        0,
                    ),
                ),
                Elmt(
                    SectionElmtRectVert(
                        self.laminate_web.inner_laminate, self.dimension_web
                    ),
                    web=True,
                    anchor_pt=Point2D(y_inner, 0),
                ),
                Elmt(
                    SectionElmtRectVert(
                        self.laminate_web.outter_laminate, self.dimension_web
                    ),
                    web=True,
                    anchor_pt=Point2D(self.dimension_flange / 2, 0),
                ),
            ]
        if isinstance(self.laminate_flange, SingleSkinLaminate):
            flange_elements = [
                Elmt(
                    SectionElmtRectHoriz(
                        laminate=self.laminate_flange, dimension=self.dimension_flange
                    ),
                    anchor_pt=Point2D(0, self.dimension_web),
                )
            ]
        elif isinstance(self.laminate_flange, SandwichLaminate):
            flange_elements = [
                Elmt(
                    SectionElmtRectHoriz(
                        laminate=self.laminate_flange.inner_laminate,
                        dimension=self.dimension_flange,
                    ),
                    anchor_pt=Point2D(0, self.dimension_web),
                ),
                Elmt(
                    SectionElmtRectHoriz(
                        laminate=self.laminate_flange.outter_laminate,
                        dimension=self.dimension_flange,
                    ),
                    anchor_pt=Point2D(
                        0,
                        self.dimension_web
                        + self.laminate_flange.outter_laminate.thickness
                        + self.laminate_flange.core.thickness,
                    ),
                ),
            ]
        flange_elements = flange_elements + [
            Elmt(
                sect_elmt=SectionElmtRectHoriz(
                    laminate=self.laminate_flange_lower,
                    dimension=2 * self.laminate_web.thickness,
                ),
                anchor_pt=Point2D(0, 0),
            )
        ]
        return web_elements + flange_elements

    @property
    def foot_width(self) -> float:
        return self.dimension_flange

    def shear_buckling_strain(self, length: float) -> float:
        return self.laminate_web.buckling_shear_strain(self.dimension_web, length)


@dataclass
class Box(SectionElementListWithFoot):
    """L bar profile - composed of a web and a flange. Dimensions in m."""

    laminate_web: Laminate = field(
        metadata={DESERIALIZER_OPTIONS: LAMINATE_WEB_OPTIONS}
    )
    dimension_web: float = field(metadata={DESERIALIZER_OPTIONS: DIMENSION_WEB_OPTIONS})
    laminate_flange: Laminate = field(
        metadata={DESERIALIZER_OPTIONS: LAMINATE_FLANGE_OPTIONS}
    )
    dimension_flange: float = field(
        metadata={DESERIALIZER_OPTIONS: DIMENSION_FLANGE_OPTIONS}
    )
    name: str = field(metadata={DESERIALIZER_OPTIONS: NAME_OPTIONS})

    @property
    def elmts(self) -> list[Elmt]:
        dimension = self.dimension_web - self.laminate_flange.thickness * 2
        if isinstance(self.laminate_web, SingleSkinLaminate):
            web_elements = [
                Elmt(
                    SectionElmtRectVert(self.laminate_web, dimension),
                    web=True,
                    anchor_pt=Point2D(
                        -self.dimension_flange / 2, self.laminate_flange.thickness
                    ),
                ),
                Elmt(
                    SectionElmtRectVert(self.laminate_web, dimension),
                    web=True,
                    anchor_pt=Point2D(
                        self.dimension_flange / 2 - self.thickness,
                        self.laminate_flange.thickness,
                    ),
                ),
            ]
        elif isinstance(self.laminate_web, SandwichLaminate):
            y_inner = (
                self.dimension_flange / 2
                - self.laminate_web.thickness_eff / 2
                - self.laminate_web.core.thickness
            )

            web_elements = [
                Elmt(
                    SectionElmtRectVert(self.laminate_web.outter_laminate, dimension),
                    web=True,
                    anchor_pt=Point2D(
                        -self.dimension_flange / 2, self.laminate_flange.thickness
                    ),
                ),
                Elmt(
                    SectionElmtRectVert(self.laminate_web.inner_laminate, dimension),
                    web=True,
                    anchor_pt=Point2D(
                        -y_inner,
                        self.laminate_flange.thickness,
                    ),
                ),
                Elmt(
                    SectionElmtRectVert(
                        self.laminate_web.inner_laminate, self.dimension_web
                    ),
                    web=True,
                    anchor_pt=Point2D(y_inner, self.laminate_flange.thickness),
                ),
                Elmt(
                    SectionElmtRectVert(
                        self.laminate_web.outter_laminate, self.dimension_web
                    ),
                    web=True,
                    anchor_pt=Point2D(
                        self.dimension_flange / 2, self.laminate_flange.thickness
                    ),
                ),
            ]
        if isinstance(self.laminate_flange, SingleSkinLaminate):
            flange_elements = [
                Elmt(
                    SectionElmtRectHoriz(
                        laminate=self.laminate_flange, dimension=self.dimension_flange
                    ),
                    anchor_pt=Point2D(0, 0),
                ),
                Elmt(
                    SectionElmtRectHoriz(
                        laminate=self.laminate_flange, dimension=self.dimension_flange
                    ),
                    anchor_pt=Point2D(
                        0, self.dimension_web - self.laminate_flange.thickness
                    ),
                ),
            ]
        elif isinstance(self.laminate_flange, SandwichLaminate):
            flange_elements = [
                Elmt(
                    SectionElmtRectHoriz(
                        laminate=self.laminate_flange.outter_laminate,
                        dimension=self.dimension_flange,
                    ),
                    anchor_pt=Point2D(0, 0),
                ),
                Elmt(
                    SectionElmtRectHoriz(
                        laminate=self.laminate_flange.inner_laminate,
                        dimension=self.dimension_flange,
                    ),
                    anchor_pt=Point2D(
                        0,
                        +self.laminate_flange.outter_laminate.thickness
                        + self.laminate_flange.core.thickness,
                    ),
                ),
                Elmt(
                    SectionElmtRectHoriz(
                        laminate=self.laminate_flange.inner_laminate,
                        dimension=self.dimension_flange,
                    ),
                    anchor_pt=Point2D(
                        0, self.dimension_web - self.laminate_flange.thickness
                    ),
                ),
                Elmt(
                    SectionElmtRectHoriz(
                        laminate=self.laminate_flange.outter_laminate,
                        dimension=self.dimension_flange,
                    ),
                    anchor_pt=Point2D(
                        0,
                        self.dimension_web
                        - self.laminate_flange.outter_laminate.thickness,
                    ),
                ),
            ]
        return web_elements + flange_elements

    @property
    def foot_width(self) -> float:
        return self.dimension_flange

    def shear_buckling_strain(self, length: float) -> float:
        return self.laminate_web.buckling_shear_strain(self.dimension_web, length)


ELMT_CONTAINER_SUBTYPES = [LBar, FlatBar, TopHat, OpenU, ClosedU, Box]
ELMT_CONTAINER_SUBTYPE_TABLE = {typ.__name__: typ for typ in ELMT_CONTAINER_SUBTYPES}
ELMT_CONTAINER_OPTIONS = DeSerializerOptions(
    add_type=True,
    type_label="section_profile",
    flatten=True,
    subtype_table=ELMT_CONTAINER_SUBTYPE_TABLE,
    metadata=PrintMetadata(long_name="Section type"),
)


@dataclass
class StiffenerSectionWithFoot(StiffenerSection):

    elmt_container: SectionElementListWithFoot = field(
        metadata={DESERIALIZER_OPTIONS: ELMT_CONTAINER_OPTIONS}
    )

    @property
    def foot_width(self):
        return self.elmt_container.foot_width

    @property
    def name(self):
        return self.elmt_container.name

    def shear_buckling_strain(self, length: float) -> float:
        return self.elmt_container.shear_buckling_strain(length)


@dataclass
class AttPlateSandwich(SectionElementList):
    """Sandwich attached plate section."""

    laminate: SandwichLaminate
    dimension: float

    @property
    def elmts(self):
        z_inner = self.laminate.thickness - self.laminate.skins[1].thickness
        anchors = [Point2D(0, 0), Point2D(0, z_inner)]
        return [
            Elmt(SectionElmtRectHoriz(skin, self.dimension), anchor_pt=anchor)
            for skin, anchor in zip(self.laminate.skins, anchors)
        ]


@dataclass
class AttPlateSingleSkin(SectionElementList):
    """Single Skin attached plate section."""

    laminate: Laminate
    dimension: float

    @property
    def elmts(self):
        return [Elmt(SectionElmtRectHoriz(self.laminate, self.dimension))]


def att_plate_section_factory(lam_type) -> StiffenerSection:
    table = {SingleSkinLaminate: AttPlateSingleSkin, SandwichLaminate: AttPlateSandwich}
    return table[lam_type]


@dataclass
class PlacedStiffnerSection(SectionElementList):
    stiff_section: StiffenerSection
    angle: float
    anchor_pt: Point2D

    @property
    def elmts(self) -> list[Elmt]:
        return [
            Elmt(
                sect_elmt=self.stiff_section,
                anchor_pt=self.anchor_pt,
                angle=self.angle,
                web=True,
            )
        ]


STIFF_SECTION_OPTIONS = DeSerializerOptions(
    subs_by_attr="name",
    subs_collection_name="stiffener_sections",
    metadata=PrintMetadata(long_name="Stiffener section", abreviation="section"),
)


@dataclass
class Stiffener:
    """Stiffener beam model, in accordance to C3.8.2.6 and C3.8.4,
    including a stiffener profile section and attached plates. Dimensions im m.
    spacing_1 and spacing_2 refer to distance from stiffener to center of the
    unsupported plates on each side.
    """

    stiff_section: StiffenerSectionWithFoot = field(
        metadata={DESERIALIZER_OPTIONS: STIFF_SECTION_OPTIONS}
    )
    span: float = field(metadata={DESERIALIZER_OPTIONS: SPAN_OPTIONS})
    spacing_1: float = field(metadata={DESERIALIZER_OPTIONS: SPACING_1_OPTIONS})
    spacing_2: float = field(metadata={DESERIALIZER_OPTIONS: SPACING_2_OPTIONS})
    stiff_att_plate: int = field(
        metadata={DESERIALIZER_OPTIONS: STIFF_ATT_PLATE_OPTIONS}
    )
    att_plate_1: Laminate = field(metadata={DESERIALIZER_OPTIONS: ATT_PLATE_1_OPTIONS})
    att_plate_2: Laminate = field(metadata={DESERIALIZER_OPTIONS: ATT_PLATE_2_OPTIONS})
    stiff_att_angle: float = field(
        default=0, metadata={DESERIALIZER_OPTIONS: STIFF_ATT_ANGLE_OPTIONS}
    )
    curvature: float = field(
        default=0, metadata={DESERIALIZER_OPTIONS: CURVATURE_OPTIONS}
    )
    bound_cond: BoundaryCondition = field(
        default=BoundaryCondition.FIXED,
        metadata={DESERIALIZER_OPTIONS: BOUND_COND_OPTIONS},
    )

    @property
    def spacings(self):
        return np.array([self.spacing_1, self.spacing_2])

    @property
    def spacing(self):
        """Sum of both spacings"""
        return np.sum(self.spacings)

    @property
    def area(self):
        return self.span * self.spacing

    @property
    def att_plates_lam(self):
        return [self.att_plate_1, self.att_plate_2]

    @property
    def eff_widths(self) -> list[float]:
        xp = list(range(10))
        fp = [0, 0.36, 0.64, 0.82, 0.91, 0.96, 0.98, 0.993, 0.998, 1]
        weff = np.interp(self.length_bet_mom / (self.spacing), xp, fp) * self.spacing
        weffs = [spacing / self.spacing * weff for spacing in self.spacings]
        # since att plates are numbered 1 and 2, but storing list index starts at 0
        index = (
            self.stiff_att_plate - 1
        )  # checking if adding foot with of section gets efffective with greater than spacing
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
        return StiffenerSection(
            SectionElementListChain(
                [
                    att_plate_section_factory(type(laminate))(laminate, dimension)
                    for laminate, dimension in zip(self.att_plates_lam, self.eff_widths)
                ]
                + [
                    PlacedStiffnerSection(
                        stiff_section=self.stiff_section,
                        anchor_pt=Point2D(
                            0,
                            self.att_plates_lam[self.stiff_att_plate - 1].thickness,
                        ),
                        angle=self.stiff_att_angle,
                    )
                ]
            )
        )

    @property
    def curvature_correction_coef(self):
        return 1.15 - 5 * self.curvature / self.span

    @property
    def boundary_cond_coef_bend(self):
        table = {BoundaryCondition.FIXED: 12.0, BoundaryCondition.SIMPLY_SUPPORTED: 8.0}
        return table[self.bound_cond]

    @property
    def boundary_cond_coef_deflection(self):
        table = {BoundaryCondition.FIXED: 1, BoundaryCondition.SIMPLY_SUPPORTED: 5}
        return table[self.bound_cond]

    def bending_momt(self, pressure: float) -> float:
        return (
            pressure
            * self.spacing
            * self.span**2
            * self.curvature_correction_coef
            / self.boundary_cond_coef_bend
        )

    def shear_force(self, pressure: float) -> float:
        return pressure * self.span * self.spacing / 2

    def deflection(self, pressure: float) -> float:
        return (
            pressure
            * self.spacing
            * self.span**4
            * self.boundary_cond_coef_deflection
            / (384 * self.stiff_section_att_plate.bend_stiff().y)
        )

    def linear_strains(self, pressure: float) -> list[float]:
        bend_momt = self.bending_momt(pressure)
        bend_stiff = self.stiff_section_att_plate.bend_stiff_0.y
        return [
            bend_momt * y / bend_stiff
            for y in self.stiff_section_att_plate.limit_z_center()
        ]

    def shear_strain(self, pressure: float):
        return self.stiff_section_att_plate.shear_strain_web(self.shear_force(pressure))

    def rule_check(self, pressure: float):
        # TODO get safety factos from config and strain limits from laminate properties
        strain_linear_limt = 0.0105
        strain_shear_limit = 0.021
        safety_factor = 3
        strains = self.linear_strains(pressure)
        span_deflection_factor = 0.05
        deflection_check = pd.DataFrame(
            {
                "deflection": [
                    Criteria(
                        self.deflection(pressure), span_deflection_factor * self.span, 1
                    )
                ]
            }
        )
        linear_strain_check_bottom = pd.DataFrame(
            {
                "linear_strain_ratio_bottom": [
                    Criteria(np.abs(strains[0]), strain_linear_limt, safety_factor)
                ]
            }
        )
        linear_strain_check_top = pd.DataFrame(
            {
                "linear_strain_ratio_top": [
                    Criteria(np.abs(strains[1]), strain_linear_limt, safety_factor)
                ]
            }
        )
        shear_strain_check = pd.DataFrame(
            {
                "shear_strain_ratio": [
                    Criteria(
                        self.shear_strain(pressure), strain_shear_limit, safety_factor
                    )
                ]
            }
        )
        shear_buckling_strain_check = pd.DataFrame(
            {
                "shear_strain_buckling_ratio": [
                    Criteria(
                        self.shear_strain(pressure),
                        self.stiff_section.shear_buckling_strain(self.span),
                        1,
                    )
                ]
            }
        )
        return pd.concat(
            [
                deflection_check,
                linear_strain_check_bottom,
                linear_strain_check_top,
                shear_strain_check,
                shear_buckling_strain_check,
            ],
            axis=1,
        )
