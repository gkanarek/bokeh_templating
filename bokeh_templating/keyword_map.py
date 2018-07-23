#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 09:54:47 2018

@author: gkanarek
"""

from inspect import getmembers, isclass, isfunction
from bokeh import models, plotting, layouts
from .bokeh_surface import Surface3d

bokeh_sequences = {}
bokeh_mappings = {"Surface3d": Surface3d} # Note that abstract base classes *are* included

def parse_module(module):
    test = lambda nm, mem: (not nm.startswith("_")) and (module.__name__ in mem.__module__)
    seqs = {nm: mem for nm, mem in getmembers(module, isfunction) if test(nm, mem)}
    maps = {nm: mem for nm, mem in getmembers(module, isclass) if test(nm, mem)}
    return (seqs, maps)

for module in [models, plotting, layouts]:
    seqs, maps = parse_module(module)
    bokeh_sequences.update(seqs)
    bokeh_mappings.update(maps)