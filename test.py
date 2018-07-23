#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 10:03:35 2018

@author: gkanarek
"""

import numpy as np
from bokeh_templating import BokehTemplate

widget_formats = """
Figure:
"""

class TestBokehApp(BokehTemplate):
    
    def pre_init(self):
        self.a, self.b = 4, 2
        
        self.format_string = None #widget_formats
        self.interface_file = "test_interface.yaml"
    
    post_init = None
    
    @property
    def x(self):
        return 4. * np.sin(self.a * np.linspace(0, 2*np.pi, 500))
    
    @property
    def y(self):
        return 3. * np.sin(self.b * np.linspace(0, 2*np.pi, 500))
    
    def controller(self, attr, old, new):
        self.a = self.refs["a_slider"].value
        self.b = self.refs["b_slider"].value
        
        self.refs["figure_source"].data = {'x': self.x, 'y': self.y}

        
TestBokehApp()
    