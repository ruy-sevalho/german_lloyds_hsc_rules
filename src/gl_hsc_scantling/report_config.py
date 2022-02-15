from dataclasses import dataclass, fields
from typing import Optional
from dataclass_tools.tools import DeSerializerOptions, DESERIALIZER_OPTIONS


@dataclass
class PrintOptions:
    """[summary]"""

    convert_units: Optional[str] = None
    round_precision: int = 2
    label: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ReportConfig:
    modulus_x: PrintOptions = PrintOptions(
        convert_units="GPa",
        label=r"E\textsubscript{x}",
        description="Modulus of elasticity - x direction",
    )
    modulus_y: PrintOptions = PrintOptions(convert_units="GPa")
    modulus_xy: PrintOptions = PrintOptions(convert_units="GPa")
    density: PrintOptions = PrintOptions(round_precision=0)
    max_strain_x: PrintOptions = PrintOptions()
    max_strain_xy: PrintOptions = PrintOptions()
    f_mass_cont: PrintOptions = PrintOptions()
    f_area_density: PrintOptions = PrintOptions()
    thickness: PrintOptions = PrintOptions()
    orientation: PrintOptions = PrintOptions()
    multiple: PrintOptions = PrintOptions()
    strength_shear: PrintOptions = PrintOptions()
    modulus_shear: PrintOptions = PrintOptions()
    strength_tens: PrintOptions = PrintOptions()
    modulus_tens: PrintOptions = PrintOptions()
    strength_comp: PrintOptions = PrintOptions()
    modulus_comp: PrintOptions = PrintOptions()
    resin_absorption: PrintOptions = PrintOptions()
    core_type: PrintOptions = PrintOptions()
    dimension_web: PrintOptions = PrintOptions()
    dimension_flange: PrintOptions = PrintOptions()

    def to_dict(self):
        return {field_.name: getattr(self, field_.name) for field_ in fields(self)}


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
