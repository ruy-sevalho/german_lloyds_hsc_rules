# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 15:07:15 2021

@author: ruy
"""

import styleframe as sf
import numpy as np
import table_formats
import pandas as pd

formats = table_formats.formats
base_style = {
            'shrink_to_fit': False, 
            'font': 'Calibri',
            'font_size': 12,
            'border_type': None,
            'number_format':'0.0000E+#'
             }

header_style={
             'bold': True,
             'bg_color': '999999'}

alternate_rows = {#'fill_pattern_type': ('mediumGray', 'lightGray'),
                  'bg_color': ('ffffff', 'cccccc')}


def create_alternare_stylers(base_style :dict, alternate_rows:dict):
    stylers = [base_style, base_style]
    for key, value in alternate_rows.items():
        for i in range(2):
            stylers[i].update({key, value[i]})
    return stylers

def _style_table(
        table, 
        base_style, 
        header_style = None, 
        alternate_row_styles = None,
        columns_styles = None
        ):
    '''
    returns styler objects from the styleframe module \n
    styler inputs should be in the dict with the options for the styler class \n
    alternate_row_stylers dict values should contain a tuple with 2
    values, one for each alternating row \n
    header_styler and alternate_row_stylers will update the base_styler dict
    '''

    if type(base_style) is dict:
        base_style = sf.Styler(**base_style)
    df = sf.StyleFrame(table, base_style)

    if header_style:
        if type(header_style) is dict:
            header_style = sf.Styler(**header_style)            
        style = sf.Styler.combine(base_style, header_style)
        df.apply_headers_style(style, style_index_header=True)
        
    if alternate_row_styles or columns_styles:
        # size = np.max([i.value for i in df.index.tolist()])
        size =len(df.index.tolist())
        row_styles = [(list(range(0,size,2)),{})]
        if alternate_row_styles:        
            row_styles = [(list(range(i,size,2)),
                           {key: value[i] 
                            for key, value in alternate_row_styles.items()}
                          )
                          for i in range(2)]
            
        if not columns_styles:
            columns_styles = [({},[i.value for i in df.columns.tolist()])]
        
        for col in columns_styles:
            for row in row_styles:
                df.apply_style_by_indexes(
                    row[0],
                    sf.Styler(**col[1],**row[1]),
                    cols_to_style=col[0],
                    overwrite_default_style=False
                    )            
    return df

def _lamina_toxls(name, matrices_dict, matrices_style, header_style, writter):
    def lamina_dict_to_sf2(matrices_dict, matrices_style, header_style):
        def remove_symetric_values(dataframe):
            for i in range(3):
                for j in range(3):
                    if j > i:
                        dataframe[i][j] = None
            return dataframe
        
        matrices_df = {}        
        for units_key, units_system in matrices_dict.items():
            units_level = {}
            for m_key, m_type in units_system.items():
                matrices_level = {}
                for letter, single_m in m_type.items():
                    let = letter
                    if m_key == 'compl':
                        let = letter.lower()
                    col_print=  {0: let, 1: 'matrix', 2: single_m[1]}
                    df = pd.DataFrame(single_m[0])
                    df = remove_symetric_values(df)
                    df = sf.StyleFrame(df, matrices_style)
                    df.rename(columns=col_print, inplace=True)       
                    df.apply_headers_style(
                                      header_style,
                                      style_index_header=True, 
                                      cols_to_style=df.columns.tolist())
                    matrices_level.update({letter: df})
                units_level.update({m_key: matrices_level})
            matrices_df.update({units_key: units_level})
        return matrices_df
    
    def place_matrix(initial_position):
        displacemnts = [(0, 0), (0, 3), (4, 3)]
        row_col = [(initial_position[0] + displacemnt[0],
                    initial_position[1] + displacemnt[1])
                   for displacemnt in displacemnts]
        return row_col
    
    matrices_style = sf.Styler(**matrices_style)
    header_style = sf.Styler(**header_style)
    header_style = sf.Styler.combine(matrices_style, header_style)
    lamina_df = lamina_dict_to_sf2(matrices_dict, matrices_style, header_style) 
    row = 0
    
    for unit_sys in lamina_df.values():
        rows = (row, row+8)
        for m_type, r in zip(unit_sys.values(), rows):    
            positions = place_matrix((r,0))  
            for letter, position in zip(m_type.values(), positions):                 
                letter.to_excel(
                    writter, 
                    sheet_name=name, 
                    best_fit=letter.columns.tolist(),
                    startrow=position[0],
                    startcol=position[1],
                    )
        row += 17
    return

def results_resume_toxls(prefix : str, resumes : dict):
    file = prefix + ' RESULTS SUMMARY'
    wr = sf.StyleFrame.ExcelWriter(file + '.xls')
    sf.StyleFrame.A_FACTOR = 0
    sf.StyleFrame.P_FACTOR = 1
    
    for name, table in resumes.items():
        df = _style_table(
                table, 
                base_style,
                header_style,
                alternate_row_styles=alternate_rows,
                columns_styles=formats[name]
                )
        df.transpose()
        df.to_excel(
            wr, sheet_name = name.upper(), best_fit = df.columns.tolist())
    wr.save()
    wr.close()
    return

def panels_toxls(prefix : str, panels_results):
    file = prefix + ' PANELS'
    wr = sf.StyleFrame.ExcelWriter(file + '.xls')
    sf.StyleFrame.A_FACTOR = 0
    sf.StyleFrame.P_FACTOR = 1
    
    for name, panel in panels_results.items():
        df = _style_table(
                panel, 
                base_style,
                header_style,
                alternate_row_styles=alternate_rows,
                columns_styles=formats['panels_plies']
                )
        df.to_excel(
            wr, sheet_name = name.upper(), best_fit = df.columns.tolist())
        
    wr.save()
    wr.close()
    return

def laminates_toxls(prefix : str, laminates : dict):
    file = prefix + ' LAMINATES'
    wr = sf.StyleFrame.ExcelWriter(file + '.xls')
    sf.StyleFrame.A_FACTOR = 0
    sf.StyleFrame.P_FACTOR = 1
    
    for name, laminate in laminates.items():
        _lamina_toxls(name.upper(), laminate, base_style, header_style, wr)
    
    wr.save()
    wr.close()
    return
    
def results_toxls(resumes, laminates):
    wr = sf.StyleFrame.ExcelWriter('GL_SCANTLING_results.xls')
    sf.StyleFrame.A_FACTOR = 0
    sf.StyleFrame.P_FACTOR = 1
    
    for name, table in resumes.items():
        df = _style_table(
                table, 
                base_style,
                header_style,
                alternate_row_styles=alternate_rows,
                columns_styles=formats[name]
                )
        df.to_excel(
            wr, sheet_name = name.upper(), best_fit = df.columns.tolist())
    
    for name, laminate in laminates.items():
        _lamina_toxls(name.upper(), laminate, base_style, header_style, wr)
    
    wr.save()
    wr.close()
    return
        