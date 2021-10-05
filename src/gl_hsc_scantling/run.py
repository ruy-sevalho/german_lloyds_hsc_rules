# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 10:26:35 2020

@author: ruy

Automation of German Lloyd 2012 High Speed Craft strucutural rules calculation
"""

import timeit
import pyexcel as p
# import sys
# import copy

from vessel import Vessel
import elementsAssembly as elmAssemb
import elementsStiff as elmStiff
import composites as cp
import read_xls as rd
#import toxls as tx





"""Separating source of input from logic. For now all inputs should normalize
to a dictionary form. Format choosen to easily integrate with json."""


def run(data, **kwargs):
    """Main routine"""
    vessel = Vessel(**data.vessel_input)
    fibers = {row['name']: cp.Fiber(**row)
              for row in data.fibers_input}
    matrices = {row['name']: cp.Matrix(**row)
              for row in data.matrices_input}
    cores_mat_data = {row['name']: cp.Core_mat(**row)
                      for row in data.cores_mat_data_input}
    plies_mat = {row['name']: cp.lamina_factory(row['cloth_type'])(
                                                    fibers[row['fiber_type']],
                                                    matrices[row['matrix_type']],
                                                    **row) 
                 for row in data.plies_composed_input}
    plies_mat.update({row['name']: cp.Lamina(**row)
                      for row in data.plies_monolith_input})
    plies_mat.update({row['name']: cp.Core(cores_mat_data, **row)
                 for row in data.cores_input})
    lam_fact = cp.Laminate_factory()
    laminates = {row['name']: lam_fact.create_laminate(row['lam_type'])(
                                        plies_mat,
                                        **row
                                        )
                 for row 
                 in data.laminates_input}
    stiff_sections = {
        row['name']: elmStiff.stiff_section_factory(row['section_type'])(
                                            laminates,                                        
                                            **row
                                            )
        for row in data.stiff_sections_input
        }
    panels = {row['name']: elmAssemb.panel_factory(
                                row['location'], 
                                type(laminates[row['laminate_']]), 
                                row['chine'],
                                row['bound_cond']
                                )
                            (vessel, laminates[row['laminate_']], **row)
             for row in data.panels_input}
    stiff_elements = {row['name']: elmAssemb.stiff_factory(
                        row['location'], row['bound_cond'])(
                        vessel, 
                        stiff_sections[row['stiff_section_type']], 
                        laminates, **row)
                      for row in data.stiff_elements_input}           
    #Resumed results xls file data and write 
    #Removing the core materials from list to print since they have different 
    #set of attributes.
    # only_plies = dict(filter(
    #     lambda item: type(item[1]) is not cp.Core, plies_mat.items()))
    # plies_print_out =[{'name': key, **value.results} 
    #                   for key, value in only_plies.items()]
    # results_resume = {'plies': plies_print_out}
    # laminates_resume_print_out = [{'name': key, **value.print_out_resume} 
    #                               for key, value in laminates.items()]    
    # panels_resume = [{'name': key, **value.resume}
    #                  for key, value in panels.items()]
    # results_resume = {
    #     'plies': plies_print_out,
    #     'laminates': laminates_resume_print_out,
    #     'panels': panels_resume}    
    # laminates_print_out = {key: value.print_out_matrices('Imp_vector') 
    #                        for key, value in laminates.items()}
    # panels_detailed_resutls = {key: panel.plies_responses
    #                            for key, panel in panels.items()}
    session = {
        'vessel': vessel,
        'fibers': fibers,
        'matrices': matrices,
        'cores_mat_data': cores_mat_data,
        'laminates': laminates,
        'stiff_sections': stiff_sections,
        'panels': panels,
        'stiff_elements': stiff_elements,
        }
    return session


if __name__ == '__main__':
    start = timeit.default_timer()
    input_file = 'GL_SCANTLING.xls'
    data =  rd.read_xls(input_file)
    session = run(data)
    stop = timeit.default_timer()
    execution_time = stop - start
    print("Program Executed in " + str(execution_time))