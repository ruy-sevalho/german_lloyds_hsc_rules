from dataclass_tools.tools import DeSerializerOptions, NamePrint, PrintMetadata
from pylatex import NoEscape
from pylatex.base_classes import CommandBase

from .abrevitation_registry import abv_registry


class TextSubscript(CommandBase):
    pass


MATRIX_OPTIONS = DeSerializerOptions(
    subs_by_attr="name",
    subs_collection_name="matrices",
    metadata=PrintMetadata(long_name="matrix"),
)
FIBER_OPTIONS = DeSerializerOptions(
    subs_by_attr="name",
    subs_collection_name="fibers",
    metadata=PrintMetadata(long_name="fiber"),
)
LAMINATE_OPTIONS = DeSerializerOptions(
    subs_by_attr="name",
    subs_collection_name="laminates",
    metadata=PrintMetadata(long_name="Laminate"),
)
ATT_PLATE_1_OPTIONS = DeSerializerOptions(
    subs_by_attr="name",
    subs_collection_name="laminates",
    metadata=PrintMetadata(
        long_name="Laminate attached plate 1",
        abreviation=NoEscape(r"lam\textsubscript{1}"),
    ),
)
ATT_PLATE_2_OPTIONS = DeSerializerOptions(
    subs_by_attr="name",
    subs_collection_name="laminates",
    metadata=PrintMetadata(
        long_name="Laminate attached plate 2",
        abreviation=NoEscape(r"lam\textsubscript{2}"),
    ),
)
LAMINATE_WEB_OPTIONS = DeSerializerOptions(
    subs_by_attr="name",
    subs_collection_name="laminates",
    metadata=PrintMetadata(long_name="Web laminate"),
)
LAMINATE_FLANGE_OPTIONS = DeSerializerOptions(
    subs_by_attr="name",
    subs_collection_name="laminates",
    metadata=PrintMetadata(long_name="Flange laminate"),
)
NAME_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(long_name="Name", abreviation="Name")
)
DENSITY_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Density", abreviation=NoEscape(r"$\rho$"), units="kg/m**3"
    )
)
abv_registry.append(DENSITY_OPTIONS)
MODULUS_X_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Modulus of elasticity - x direction",
        abreviation=NoEscape(r"E\textsubscript{x}"),
        units="kPa",
    )
)
abv_registry.append(MODULUS_X_OPTIONS)
MODULUS_Y_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Modulus of elasticity - y direction",
        abreviation=NoEscape(r"E\textsubscript{y}"),
        units="kPa",
    )
)
abv_registry.append(MODULUS_Y_OPTIONS)
MODULUS_XY_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Modulus of elasticity - shear",
        abreviation=NoEscape(r"G\textsubscript{xy}"),
        units="kPa",
    )
)
abv_registry.append(MODULUS_XY_OPTIONS)
POISSON_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Poisson coef", abreviation=NoEscape(r"$\nu$"), units=""
    )
)
abv_registry.append(POISSON_OPTIONS)
POISSON_XY_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name=NoEscape("Poisson\textsubscript{xy} coef"),
        abreviation=NoEscape(r"$\nu$\textsubscript{xy}"),
        units="",
    )
)
abv_registry.append(POISSON_XY_OPTIONS)
POISSON_YX_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name=NoEscape("Poisson\textsubscript{yx} coef"),
        abreviation=NoEscape(r"$\nu$\textsubscript{yx}"),
        units="",
    )
)
abv_registry.append(POISSON_YX_OPTIONS)
THICKNESS_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Thickness",
        abreviation="t",
        units="m",
    )
)
CORE_THICKNESS_OPTIONS = DeSerializerOptions(
    overwrite_key="core_thickness",
    metadata=PrintMetadata(
        long_name="Core thickness",
        abreviation="core t",
        units="m",
    ),
)
abv_registry.append(THICKNESS_OPTIONS)
F_MASS_CONT_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Fiber mass content",
        abreviation=NoEscape(r"$\psi$"),
        units="percent",
    )
)
abv_registry.append(F_MASS_CONT_OPTIONS)
F_AREA_DENSITY_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Fiber area density",
        abreviation=NoEscape(r"m\textsubscript{f}"),
        units="kg / m**2",
    )
)
abv_registry.append(F_AREA_DENSITY_OPTIONS)
MAX_STRAIN_X_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Ultimate strain - tensile or compressive",
        abreviation=NoEscape(r"$\epsilon_{ult}$"),
        units="percent",
    )
)
abv_registry.append(MAX_STRAIN_X_OPTIONS)
MAX_STRAIN_XY_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Ultimate strain - shear",
        abreviation=NoEscape(r"$\gamma$\textsubscript{ult}"),
        units="percent",
    )
)
abv_registry.append(MAX_STRAIN_XY_OPTIONS)
MULTIPLE_OPTIONS = DeSerializerOptions(metadata=PrintMetadata(long_name="Repeat"))
SYMMETRIC_OPTIONS = DeSerializerOptions(metadata=PrintMetadata(long_name="Symmetric"))
ANTI_SYMMETRIC_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(long_name="Antisymmetric")
)
CORE_MATERIAL_OPTIONS = DeSerializerOptions(
    subs_by_attr="name",
    overwrite_key="core_material",
    subs_collection_name="core_materials",
    metadata=PrintMetadata(long_name="Core material", abreviation="core material"),
)
STRENGTH_SHEAR_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Shear strenght",
        abreviation=NoEscape(r"$\tau$\textsubscript{ult}"),
        units="kPa",
    )
)
abv_registry.append(STRENGTH_SHEAR_OPTIONS)
MODULUS_SHEAR_OPTIONS = MODULUS_XY_OPTIONS
STRENGTH_TENSION_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Tension strenght",
        abreviation=NoEscape(r"$\sigma$\textsubscript{T ult}"),
        units="kPa",
    )
)
abv_registry.append(STRENGTH_TENSION_OPTIONS)
MODULUS_TENSION_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Modulus tension",
        abreviation=NoEscape(r"E\textsubscript{T}"),
        units="kPa",
    )
)
abv_registry.append(MODULUS_TENSION_OPTIONS)
STRENGTH_COMP_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Compression strenght",
        abreviation=NoEscape(r"$\sigma$\textsubscript{C ult}"),
        units="kPa",
    )
)
abv_registry.append(STRENGTH_COMP_OPTIONS)
MODULUS_COMP_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Modulus compression",
        abreviation=NoEscape(r"E\textsubscript{C}"),
        units="kPa",
    )
)
abv_registry.append(MODULUS_COMP_OPTIONS)
RESIN_ABSORPTION_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Resin absorption",
        abreviation="RA",
        units="kg /  m**2",
    )
)
abv_registry.append(RESIN_ABSORPTION_OPTIONS)
CORE_TYPE_OPTIONS = DeSerializerOptions(metadata=PrintMetadata(long_name="Type"))
CORE_THICKNESS_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(long_name="Core thickness", abreviation="core t", units="m")
)
DIMENSION_WEB_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Web height", abreviation=NoEscape(r"Web\textsubscript{H}"), units="m"
    )
)
DIMENSION_FLANGE_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Flange width",
        abreviation=NoEscape(r"Flange\textsubscript{W}"),
        units="m",
    )
)
DEADRISE_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Deadrise", abreviation=NoEscape(r"$\alpha$"), units="degree"
    )
)
AIR_GAP_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Air gap", abreviation=NoEscape(r"air\textsubscript{gap}"), units="m"
    )
)
DECKHOUSE_BREADTH_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Deckhouse breadth",
        abreviation=NoEscape(r"DH\textsubscript{B}"),
        units="m",
    )
)
DIM_X_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="x dimension",
        abreviation=NoEscape(r"dim\textsubscript{x}"),
        units="m",
    )
)
DIM_Y_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Y dimension",
        abreviation=NoEscape(r"dim\textsubscript{Y}"),
        units="m",
    )
)
CURVATURE_X_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Curvature in the x direction",
        abreviation=NoEscape(r"c\textsubscript{x}"),
        units="m",
    )
)
CURVATURE_Y_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Curvature in the y direction",
        abreviation=NoEscape(r"c\textsubscript{y}"),
        units="m",
    )
)
CHINE_OPTIONS = DeSerializerOptions(metadata=PrintMetadata(long_name="Chine"))
CHINE_ANGLE_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Chine angle",
        abreviation=NoEscape(r"chine\textsubscript{$\alpha$}"),
        units="degree",
    )
)
BOUND_COND_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Boundary condition",
        abreviation=NoEscape(r"B\textsubscript{C}"),
    )
)
SPACING_1_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Spacing 1",
        abreviation=NoEscape(r"space\textsubscript{1}"),
        units="m",
    )
)
SPACING_2_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Spacing 2",
        abreviation=NoEscape(r"space\textsubscript{2}"),
        units="m",
    )
)
SPAN_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Span",
        abreviation="span",
        units="m",
    )
)
STIFF_ATT_PLATE_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Stiffener attachment plate",
        abreviation=NoEscape(r"att\textsubscript{plate}"),
        units="m",
    )
)
STIFF_ATT_ANGLE_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Stiffener attachment angle",
        abreviation=NoEscape(r"$\theta$\textsubscript{att}"),
        units="degree",
    )
)
