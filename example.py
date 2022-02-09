import json
from dataclasses import asdict, fields

from dataclass_tools.tools import (
    DeSerializerOptions,
    PrintMetadata,
    deserialize_dataclass,
    serialize_dataclass,
)
from pylatex import NoEscape, PageStyle

from gl_hsc_scantling.composites import PlyStack

from gl_hsc_scantling.report_config import default_report_config
from gl_hsc_scantling.shortcut import (
    Bottom,
    Core,
    CoreMat,
    Deck,
    Fiber,
    Lamina,
    LaminaMonolith,
    LaminaParts,
    LBar,
    Matrix,
    Panel,
    Ply,
    SandwichLaminate,
    Session,
    Side,
    SingleSkinLaminate,
    Stiffener,
    StructuralElement,
    Vessel,
    WetDeck,
)
from gl_hsc_scantling.stiffeners import (
    Elmt,
    Point2D,
    SectionElementList,
    SectionElmtRectHoriz,
    SectionElmtRectVert,
    Stiffener,
    StiffenerSection,
    StiffenerSectionWithFoot,
)
from gl_hsc_scantling.tex import generate_report

session = Session()

vessel = Vessel(
    name="Catamaran",
    speed=15,
    displacement=6,
    length=10,
    beam=6.5,
    fwd_perp=10,
    aft_perp=0,
    draft=0.51,
    z_baseline=-0.51,
    block_coef=0.4,
    water_plane_area=10,
    lcg=4,
    deadrise_lcg=12,
    dist_hull_cl=4.6,
    type_of_service="PASSENGER",
    service_range="USR",
)

session.add_stuff(vessel)

polyester = Matrix(
    name="polyester", density=1200, modulus_x=3000000, modulus_xy=1140000, poisson=0.316
)
epoxy = Matrix(
    name="epoxy", density=1400, modulus_x=5000000, modulus_xy=1200000, poisson=0.3
)
matrices = [polyester, epoxy]
session.add_stuff(matrices)
# session.matrices.update({matrix.name: matrix for matrix in matrices})

e_glass = Fiber(
    name="e_glass",
    density=2540,
    modulus_x=73000000,
    modulus_y=73000000,
    modulus_xy=30000000,
    poisson=0.18,
)
fibers = [e_glass]
session.add_stuff(fibers)
# session.fibers.update({fiber.name: fiber for fiber in fibers})

e_glass_poly_70_308 = Lamina(
    LaminaParts(
        name="e_glass_poly_70_308",
        fiber=e_glass,
        matrix=polyester,
        f_mass_cont=0.7,
        f_area_density=0.304,
        max_strain_x=0.0105,
        max_strain_xy=0.021,
    )
)
et_0900 = Lamina(
    LaminaMonolith(
        name="et_0900",
        modulus_x=14336000,
        modulus_y=39248000,
        modulus_xy=4530000,
        poisson_xy=0.09,
        thickness=0.000228,
        f_mass_cont=0.7,
        f_area_density=0.304,
        max_strain_x=0.0105,
        max_strain_xy=0.021,
    )
)
s = serialize_dataclass(et_0900, printing_format=True, include_names=True)
laminas = [e_glass_poly_70_308, et_0900]
session.add_stuff(laminas)
# session.laminas.update({lamina.name: lamina for lamina in laminas})

H80 = CoreMat(
    name="H80",
    strength_shear=950,
    modulus_shear=23000,
    strength_tens=2200,
    modulus_tens=85000,
    strength_comp=1150,
    modulus_comp=80000,
    density=80,
    resin_absorption=0.35,
    core_type="solid",
)
core_mats = [H80]
session.add_stuff(core_mats)

# H80_20mm = Core(name="H80_20mm", core_material=H80, core_thickness=0.02)
# cores = [H80_20mm]
# session.add_stuff(cores)

orientation = [0, 90]
et_0900_20x_input = PlyStack(
    [Ply(material=et_0900, orientation=ang) for ang in orientation], multiple=10
)
et_0900_20x = SingleSkinLaminate(name="et_0900_20x", ply_stack=et_0900_20x_input)
et_0900_20x_45_input = PlyStack(
    [Ply(material=et_0900, orientation=ang) for ang in [45, -45]], multiple=10
)
et_0900_20x_45 = SingleSkinLaminate(
    name="et_0900_20x_45", ply_stack=et_0900_20x_45_input
)
sandwich_skin_input = PlyStack(
    [Ply(material=et_0900, orientation=ang) for ang in orientation], multiple=5
)
sandwich_laminate = SandwichLaminate(
    name="Sandwich Laminate",
    outter_laminate_ply_stack=sandwich_skin_input,
    inner_laminate_ply_stack=sandwich_skin_input,
    core=Core(core_material=H80, core_thickness=0.02),
)
laminates = [et_0900_20x, et_0900_20x_45, sandwich_laminate]
session.add_stuff(laminates)

panel = Panel(dim_x=1, dim_y=1, curvature_x=0.1, curvature_y=0.1, laminate=et_0900_20x)
bottom = Bottom(deadrise=20)
panel_element = StructuralElement(
    name="Bottom Panel", x=5, z=-0.3, vessel=vessel, model=panel, location=bottom
)
session.add_stuff(panel_element)

lbar_input = {
    "name": "lbar_01",
    "section_profile": "LBar",
    "laminate_web": "et_0900_20x_45",
    "dimension_web": 0.05,
    "laminate_flange": "et_0900_20x",
    "dimension_flange": 0.02,
}
d = session.session_dict
lbar_2 = StiffenerSectionWithFoot(
    elmt_container=LBar(
        name="lbar",
        laminate_flange=et_0900_20x,
        dimension_flange=0.2,
        laminate_web=et_0900_20x_45,
        dimension_web=0.05,
    ),
)
lbar = deserialize_dataclass(
    dct=lbar_input,
    dataclass=StiffenerSectionWithFoot,
    dict_of_collections=d,
    build_instance=True,
)
session.add_stuff(lbar)

stiffener = Stiffener(
    stiff_section=lbar,
    span=1,
    spacing_1=0.5,
    spacing_2=0.5,
    stiff_att_plate=1,
    stiff_att_angle=0,
    att_plate_1=et_0900_20x,
    att_plate_2=et_0900_20x,
)
wet_deck = WetDeck(deadrise=0, air_gap=0.7)
stiffener_element = StructuralElement(
    name="Wet Deck 01", x=2, z=0.7, vessel=vessel, model=stiffener, location=wet_deck
)
session.add_stuff(stiffener_element)

panel_wet = Panel(
    dim_x=1, dim_y=1, curvature_x=0.1, curvature_y=0.1, laminate=et_0900_20x
)
panel_wet_deck_element = StructuralElement(
    name="Wet Deck 01",
    x=2,
    z=0.7,
    vessel=vessel,
    model=panel_wet,
    location=wet_deck,
)
session.add_stuff(panel_wet_deck_element)
session_serialized = serialize_dataclass(session)

with open("session.json", "w") as s:
    json.dump(session_serialized, s)

loaded_session = Session()
loaded_session.load_session(session_serialized)
doc = generate_report(session, config=default_report_config)

# bottom_panel_01 = StructuralElement(
#     name="Bottom Panel 01",
#     x=8,
#     z=-0.3,
#     vessel=vessel,
#     model=panel,
#     location=bottom,
# )
# side_panel = StructuralElement(
#     name="Side Panel 01",
#     x=8,
#     z=0.2,
#     vessel=vessel,
#     model=panel,
#     location=Side(),
# )

# side_panel = StructuralElement(
#     name="Side Panel 01",
#     x=6.5,
#     z=0.2,
#     vessel=vessel,
#     model=panel,
#     location=Side(),
# )
