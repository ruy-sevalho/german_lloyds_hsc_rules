# -*- coding: utf-8 -*-
"""
Created on Tue May 18 10:12:31 2021

@author: ruy
"""


import pyexcel as p
from .session import InputDict


def read_xls(input_file):
    vessel = p.get_records(
        file_name=input_file,
        sheet_name="VESSEL",
        name_columns_by_row=-1,
        name_rows_by_column=0,
        start_column=1,
    )[0]
    fibers = p.get_records(
        file_name=input_file,
        sheet_name="FIBERS",
        name_columns_by_row=-1,
        name_rows_by_column=0,
        start_column=1,
    )
    matrices = p.get_records(
        file_name=input_file,
        sheet_name="MATRICES",
        name_columns_by_row=-1,
        name_rows_by_column=0,
        start_column=1,
    )
    cores_mat = p.get_records(
        file_name=input_file,
        sheet_name="CORE MAT",
        name_columns_by_row=-1,
        name_rows_by_column=0,
        start_column=1,
    )
    cores = p.get_records(
        file_name=input_file,
        sheet_name="CORES",
        name_columns_by_row=-1,
        name_rows_by_column=0,
        start_column=1,
    )
    plies_composed = p.get_records(
        file_name=input_file,
        sheet_name="PLIES COMPOSED",
        name_columns_by_row=-1,
        name_rows_by_column=0,
        start_column=1,
    )
    plies_monolith = p.get_records(
        file_name=input_file,
        sheet_name="PLIES MONOLITH",
        name_columns_by_row=-1,
        name_rows_by_column=0,
        start_column=1,
    )

    single_skin_laminates = p.get_records(
        file_name=input_file, sheet_name="SINGLE SKIN LAMINATES"
    )
    plies_unpositioned = {
        laminate["name"]: p.get_records(
            file_name=input_file, sheet_name=laminate["name"]
        )
        for laminate in single_skin_laminates
    }
    for ply in plies_unpositioned.values():
        for i, element in enumerate(ply):
            ply[i] = dict(element)

    for laminate in single_skin_laminates:
        laminate.update({"plies_unpositioned": plies_unpositioned[laminate["name"]]})
    single_skin_laminates = single_skin_laminates
    sandwhich_laminates = p.get_records(
        file_name=input_file,
        sheet_name="SANDWHICH LAMINATES",
        # name_rows_by_column=0,
    )
    stiff_sections = p.get_records(
        file_name=input_file, sheet_name="STIFF SECTION LIST"
    )
    sections_builder = {
        stiff["name"]: p.get_records(
            file_name=input_file,
            sheet_name=stiff["name"],
            name_columns_by_row=-1,
            name_rows_by_column=0,
            start_column=1,
        )[0]
        for stiff in stiff_sections
    }
    for stiff in stiff_sections:
        stiff.update(
            {**sections_builder[stiff["name"]], "section_type": stiff["section_type"]}
        )
    stiff_sections = stiff_sections
    panels = p.get_records(
        file_name=input_file,
        sheet_name="PANELS",
        name_columns_by_row=-1,
        name_rows_by_column=0,
        start_column=1,
    )
    stiff_elements = p.get_records(
        file_name=input_file,
        sheet_name="STIFFENERS",
        name_columns_by_row=-1,
        name_rows_by_column=0,
        start_column=1,
    )
    return InputDict(
        name=input_file,
        vessel=vessel,
        fibers=fibers,
        matrices=matrices,
        cores_mat=cores_mat,
        cores=cores,
        plies_composed=plies_composed,
        plies_monolith=plies_monolith,
        single_skin_laminates=single_skin_laminates,
        sandwhich_laminates=sandwhich_laminates,
        panels=panels,
        stiff_sections=stiff_sections,
        stiff_elements=stiff_elements,
    )
