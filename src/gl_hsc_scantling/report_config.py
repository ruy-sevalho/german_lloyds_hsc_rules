from gl_hsc_scantling.common_field_options import (
    F_AREA_DENSITY_OPTIONS,
    F_MASS_CONT_OPTIONS,
    THICKNESS_OPTIONS,
)
from gl_hsc_scantling.composites import PlyStack

from .tex import PrintOptions, ReportConfig

modulus_print_options = PrintOptions(convert_units="GPa")
density_print_options = PrintOptions(round_precision=0)
max_strain_print_options = PrintOptions()
f_mass_cont_print_options = PrintOptions(round_precision=0)
f_area_density_print_options = PrintOptions(round_precision=3)
thickness_print_options = PrintOptions(convert_units="mm")
orientation_print_options = PrintOptions(round_precision=1)
multiple_print_options = PrintOptions(round_precision=0)
strength_shear_print_options = PrintOptions(round_precision=0)
dimenion_web_print_options = PrintOptions(convert_units="mm")
dimenion_flange_print_options = PrintOptions(convert_units="mm")

default_report_config = ReportConfig(
    modulus_x=modulus_print_options,
    modulus_y=modulus_print_options,
    modulus_xy=modulus_print_options,
    density=density_print_options,
    max_strain_x=max_strain_print_options,
    max_strain_xy=max_strain_print_options,
    f_mass_cont=f_mass_cont_print_options,
    f_area_density=f_area_density_print_options,
    thickness=thickness_print_options,
    orientation=orientation_print_options,
    multiple=multiple_print_options,
    strength_shear=strength_shear_print_options,
    modulus_shear=modulus_print_options,
    strength_tens=strength_shear_print_options,
    modulus_tens=modulus_print_options,
    strength_comp=strength_shear_print_options,
    modulus_comp=modulus_print_options,
    resin_absorption=PrintOptions(),
    core_type=PrintOptions(),
    dimension_flange=dimenion_flange_print_options,
    dimension_web=dimenion_web_print_options,
)
