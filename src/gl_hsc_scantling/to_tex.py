# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 12:22:24 2021

@author: ruy
"""

import pylatex as pyl

INPUT = 'Input'
VESSEL_INPUT_CAPTION = 'Vessel Parameters'
VESSEL_OUTPUT_CAPTION = 'Vessel Output'
FIBER_CAPTION = 'Fibers'
MATRIX_CAPTION = 'Matrices'
LAMINA_COMP_CAPTION = 'Lamina - properties calculated from components'
LAMINATE_PRE_CAPTION = 'Lamina - properties defimied by user'


class Center(pyl.base_classes.Environment):
    pass


def add_table(doc, caption, table_array):
    with doc.create(pyl.Table(position='h')) as table:
        table.add_caption(caption)
        with table.create(Center()):
            with table.create(pyl.Tabular('l r l')) as tabular:
                tabular.add_row(table_array[0])
                tabular.add_hline()
                for row in table_array[1:]:
                    tabular.add_row(row)


def to_tex(session, file_name='report'):
    vessel = session.vessel
    vessel_input = vessel.input_print()
    geometry_options = pyl.NoEscape(
        r'text={7in,10in}, a4paper, centering')
    document_options = ['11pt', 'a4paper']
    doc_kwargs = {
        'document_options': document_options,
        'geometry_options': geometry_options,
    }
    doc = pyl.Document(**doc_kwargs)
    with doc.create(pyl.Section('Vessel')):
        add_table(doc, VESSEL_INPUT_CAPTION, vessel_input)
        add_table(doc, VESSEL_OUTPUT_CAPTION, vessel.output_print())

    with doc.create(pyl.Section('Materials')):
        pass

    doc.generate_tex(file_name)
