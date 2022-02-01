from gl_hsc_scantling.common_field_options import (
    F_AREA_DENSITY_OPTIONS,
    F_MASS_CONT_OPTIONS,
    THICKNESS_OPTIONS,
)

from .tex import PrintOptions, ReportConfig

MODULUS_PRINT_OPTIONS = PrintOptions(convert_units="GPa")
DENSITY_PRINT_OPTIONS = PrintOptions(round_precision=0)
MAX_STRAIN_PRINT_OPTIONS = PrintOptions()
F_MASS_CONT_PRINT_OPTIONS = PrintOptions(round_precision=0)
F_AREA_DENSITY_PRINT_OPTIONS = PrintOptions(round_precision=3)
THICKNESS_PRINT_OPTIONS = PrintOptions(convert_units="mm")

default_report_config = ReportConfig(
    modulus_x=MODULUS_PRINT_OPTIONS,
    modulus_y=MODULUS_PRINT_OPTIONS,
    modulus_xy=MODULUS_PRINT_OPTIONS,
    density=DENSITY_PRINT_OPTIONS,
    max_strain_x=MAX_STRAIN_PRINT_OPTIONS,
    max_strain_xy=MAX_STRAIN_PRINT_OPTIONS,
    f_mass_cont=F_MASS_CONT_PRINT_OPTIONS,
    f_area_density=F_AREA_DENSITY_PRINT_OPTIONS,
    thickness=THICKNESS_PRINT_OPTIONS,
)
