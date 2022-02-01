from dataclass_tools.tools import DeSerializerOptions, NamePrint, PrintMetadata
from pylatex import NoEscape

from .abrevitation_registry import abv_registry

NAMED_FIELD_OPTIONS = DeSerializerOptions(subs_by_attr="name")
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
    metadata=PrintMetadata(long_name="laminate"),
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
        long_name="Modulus - x direction",
        abreviation=NoEscape(r"E\textsubscript{x}"),
        units="kPa",
    )
)
abv_registry.append(MODULUS_X_OPTIONS)
MODULUS_Y_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Modulus - y direction",
        abreviation=NoEscape(r"E\textsubscript{y}"),
        units="kPa",
    )
)
abv_registry.append(MODULUS_Y_OPTIONS)
MODULUS_XY_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Modulus - shear in xy plane",
        abreviation=NoEscape(r"G\textsubscript{xy}"),
        units="kPa",
    )
)
abv_registry.append(MODULUS_XY_OPTIONS)
POISSON_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Poisson", abreviation=NoEscape(r"$\nu$"), units=""
    )
)
abv_registry.append(POISSON_OPTIONS)
POISSON_XY_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Poisson xy",
        abreviation=NoEscape(r"$\nu$\textsubscript{xy}"),
        units="",
    )
)
abv_registry.append(POISSON_XY_OPTIONS)
POISSON_YX_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Poisson yx",
        abreviation=NoEscape(r"$\nu$\textsubscript{xy}"),
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
MAX_STRAIN_XY_OPTIONS = DeSerializerOptions(
    metadata=PrintMetadata(
        long_name="Ultimate strain - shear",
        abreviation=NoEscape(r"$\gamma_{ult}$"),
        units="percent",
    )
)
