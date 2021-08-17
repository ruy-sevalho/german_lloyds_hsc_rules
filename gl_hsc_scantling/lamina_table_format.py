# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 10:51:34 2021

@author: ruy
"""

column_name = ['name']
format_name = {}

columns_Gpa = ['Ex (GPa)', 'Ey (GPa)', 'Gxy (GPa)']
format_Gpa = {'number_format':'0.000'}

columns_mm = ['thickness (mm)']
format_mm = {'number_format':'0.0'}

columns_percentage = ['f mass cont']
format_percentage = {'number_format':'0.00%'}

columns_weight = ['f weight (g/m2)', 't weight (g/m2)']
format_weight = {'number_format':'0.0'}

columns_styles = [
        (columns_Gpa,format_Gpa),
        (columns_percentage, format_percentage),
        (columns_weight, format_weight),
        (columns_mm, format_percentage),
        (column_name, format_name)
        ]