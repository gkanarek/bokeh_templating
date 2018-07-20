#!/usr/bin/env python3
"""
Created on Mon Feb 20 14:05:03 2017

@author: gkanarek
"""

from keyword_map import bokeh_mappings as mappings, bokeh_sequences as sequences
from bokeh.io import curdoc

# Figures get their own constructor
Figure = mappings.pop("Figure")
del sequences["figure"]

def mapping_factory(tool, element_type):
    def mapping_constructor(loader, node):
        fmt = tool.formats.get(element_type, {})
        value = loader.construct_mapping(node, deep=True)
        ref = value.pop("ref", "")
        callback = value.pop("on_change", [])
        onclick = value.pop("on_click", None)
        fmt.update(value)
        # convert the "range" YAML keyword of a slider into something Bokeh can read
        if element_type == "Slider":
            fmt["start"], fmt["end"], fmt["step"] = fmt.pop("range", [0, 1, 0.1])
        
        # Many of these have hybrid signatures, with both positional and 
        # keyword arguments, so we need to convert an "args" keyword into
        # positional arguments
        arg = fmt.pop("arg", None)
        if arg is not None:
            obj = mappings[element_type](*arg, **fmt)
        else:
            obj = mappings[element_type](**fmt)
        
        # Store the object in the tool's "refs" dictionary
        if ref:
            tool.refs[ref] = obj
        
        # Handle callbacks and on_clicks
        if callback:
            obj.on_change(*callback)
        if onclick:
            obj.on_click(onclick)
            
        yield obj
    
    mapping_constructor.__name__ = element_type.lower() + '_' + mapping_constructor.__name__
    return mapping_constructor

def sequence_factory(tool, element_type):
    def sequence_constructor(loader, node):
        fmt = tool.formats.get(element_type, {})
        value = loader.construct_sequence(node, deep=True)
        obj = sequences[element_type](*value, **fmt)
        yield obj
        
    sequence_constructor.__name__ = element_type.lower() + '_' + sequence_constructor.__name__
    return sequence_constructor

#These constructors need more specialized treatment

def document_constructor(tool, loader, node):
    layout = loader.construct_sequence(node, deep=True)
    for element in layout:
        curdoc().add_root(element)
    tool.document = curdoc()
    yield tool.document

def figure_constructor(tool, loader, node):
    
    fig = loader.construct_mapping(node, deep=True)
    fmt = tool.formats.get('Figure', {})
    
    elements = fig.pop('elements', [])
    cmds = []
    ref = fig.pop("ref", "")
    callback = fig.pop("on_change", [])
    axis = tool.formats.get("Axis", {})
    axis.update(fig.pop("axis", {}))
    
    for key in fig:
        val = fig[key]
        if key in ['text', 'add_tools', 'js_on_event']:
           cmds.append((key, val))
        else:
            fmt[key] = val
    
    figure = Figure(**fmt)
    
    for key, cmd in cmds:
        if key == 'add_tools':
            figure.add_tools(*cmd)
        elif key == 'text':
            figure.text(*cmd.pop('loc'), **cmd)
        elif key == 'js_on_event':
            for event in cmd:
                figure.js_on_event(*event)
    
    for element in elements:
        key = element.pop('kind')
        if key == 'line':
            line_fmt = tool.formats.get('Line', {})
            line_fmt.update(element)
            figure.line('x', 'y', **line_fmt)
        elif key == 'circle':
            circle_fmt = tool.formats.get('Circle', {})
            circle_fmt.update(element)
            figure.circle('x', 'y', **circle_fmt)
        elif key == 'rect':
            rect_fmt = tool.formats.get('Rect', {})
            rect_fmt.update(element)
            figure.rect('rx', 'ry', 'rw', 'rh', **rect_fmt)
        elif key == 'step':
            step_fmt = tool.formats.get('Step', {})
            step_fmt.update(element)
            figure.step('x', 'y', **step_fmt)
        elif key == 'quad':
            quad_fmt = tool.formats.get('Quad', {})
            quad_fmt.update(element)
            figure.quad(**quad_fmt)
            
    for attr, val in axis.items():
        #change axis attributes, hopefully
        setattr(figure.axis, attr, val)
    
    if ref:
        tool.refs[ref] = figure
    if callback:
        figure.on_change(*callback)

    yield figure