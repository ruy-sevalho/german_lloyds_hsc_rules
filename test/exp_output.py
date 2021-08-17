# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 15:23:55 2021

@author: ruy
"""
from collections import namedtuple

ExpPly = namedtuple('ExpPly',
                    ['thickness',
                     'modulus_x',
                     'modulus_y',
                     'modulus_xy',
                     'poisson_xy',
                     'poisson_yx',
                     'name'],
                    defaults='')

ExpLaminate = namedtuple(
    'ExpLaminate',
    ['thickness',
     'stiff_m',
     'name'
     ],
    defaults='')

ExpCore = namedtuple('ExpCore',
                     ['thickness',
                      'name'])

ExpStiffSection = namedtuple(
    'ExpStiffSection',
    ['name',
     ])
