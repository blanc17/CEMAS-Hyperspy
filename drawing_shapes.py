# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 10:45:25 2022

@author: Alyssa Blanc
"""

import tkinter as tk
import frame_changer as fc
import shape_analysis as sa
import plotting as plot
import manipulate_text as mtxt
import os
import hyperspy.api as hs

"""HELPER FUNCTIONS"""

#get coordinters at event
def get_cord(s, event, ty):
    """
    Get the coordinates at an event

    Parameters
    ----------
    s : global_arrays.Shape
        Shape to be made.
    event : tk.Event
        Event of clicking or releasing the mouse button.
    ty : string
        Type of action that has been performed.

    Returns
    -------
    None.

    """

    #set where the press occured
    if ty == 'begin':
        s.x_start, s.y_start = event.x, event.y
    elif ty == 'end':
        s.x_end, s.y_end = event.x, event.y
    elif ty == 'line_begin':
        s.line_x_start, s.line_y_start = event.x, event.y
    elif ty == 'line_end':
        s.line_x_end, s.line_y_end = event.x, event.y
    
    #get the toolbar widget
    tool_w = fc.get_toolbar(event.widget)
    
    #get the message from the toolbar
    string = tool_w.message.get()
    split = string.partition(' ')
    
    #get x
    x = split[0]
    x = x.partition('=')[2]
    
    #get y
    split = split[2].partition('\n')
    y = split[0]
    y = y.partition('=')[2]
    
    #set the cordinates
    if ty == 'begin':
        s.x0 = round(float(x))
        s.y0 = round(float(y))
    elif ty == 'end':
        s.x1 = round(float(x))
        s.y1 = round(float(y))
    elif ty == 'line_begin':
        s.line_x0 = round(float(x))
        s.line_y0 = round(float(y))
    elif ty == 'line_end':
        s.line_x1 = round(float(x))
        s.line_y1 = round(float(y))
    
    return

#get width of line
def get_width(entry):
    """
    Get the width of the line entered in the text box

    Parameters
    ----------
    entry : tk.Entry, tk.StringVar
        Entry box containing the line width.

    Returns
    -------
    width : int
        Width of line (in pixels).

    """
    
    width = 1
    string = entry.get()
    if (string.isnumeric()):
        width = int(string)
        #if width is 0, change variable
        if width == 0:
            
            width = 1
            entry.delete(0, tk.END)
            entry.insert(0, '1')
    
    return width

#delete the physical model
def delete_diagram(s, widget):
    """
    Delete the shape image from a diagram

    Parameters
    ----------
    s : global_arrays.Shape
        Shape to be deleted.
    widget : tk.Frame, tk.Canvas
        Tkinter widget to delete the drawing from.

    Returns
    -------
    None.

    """
    
    for shape in s.drawn_lines:
        widget.delete(shape)
    widget.delete(s.drawing)
    
    return

"""DRAWING ON SEM MAP"""

#get the starting point
def start_point(event, clicked, shape):
    """
    When a map is clicked, get the starting point

    Parameters
    ----------
    event : tk.Event
        Mouse button is clicked.
    clicked : tk.StringVar
        Variable regarding the type of shape to be made.
    shape : global_arrays.Shape
        Shape variable.

    Returns
    -------
    None.

    """
        
    shape.name = clicked.get()
    
    if shape.name == 'Polygon':
        
        if len(shape.points) == 0:
            
            #set where the press occured
            get_cord(shape, event, 'begin')
            
            #add to lists
            shape.points.append(tuple((shape.x_start, shape.y_start)))
            shape.cords.append(tuple((shape.x0, shape.y0)))
                        
        else:
            
            shape.x_start = shape.x_end
            shape.y_start = shape.y_end
            shape.x0 = shape.x1
            shape.y0 = shape.y1
            
            return
            
    else:
        
        get_cord(shape, event, 'begin')
    
    return

def end_point(event, d, button):
    """
    Gets the endpoint of a shape when the mouse button releases

    Parameters
    ----------
    event : tk.Event 
        Mouse button is released.
    d : global_arrays.Changing_Globals
        All global variables.
    button : tk.Button
        Overlay button to enable.

    Returns
    -------
    None.

    """
        
    get_cord(d.shape, event, 'end')
    
    #if shape has been made, delete it
    delete_diagram(d.shape, event.widget)
    d.shape.made = False
    d.shape.drawn_lines = []
    
    #destroy graph currently at location
    fc.destroy_one(d.frame, d.spectra_row, 0)
       
    # #get sTEM info
    sFile = os.path.abspath('map20210514093205751_0.spc')
    d.sTEM = hs.load(sFile, 'EDS_TEM')
    d.sTEM.add_lines()
    d.sTEM.metadata.Sample.elements = d.s.metadata.Sample.elements
    d.sTEM.metadata.Sample.xray_lines = d.s.metadata.Sample.xray_lines
    
    """make the shape"""
    #axis
    y_axis = []
    s = d.shape
    
    #line
    if d.shape.name == 'Line':
        
        width = get_width(d.shape.width)
        
        d.shape.drawing = event.widget.create_line(s.x_start, s.y_start, s.x_end, 
                                             s.y_end, fill='red', width=width)
        
        y_axis = sa.analysis_over_line(d, width)
            
    #rectangle
    elif d.shape.name == 'Rectangle':
        
        d.shape.drawing = event.widget.create_rectangle(s.x_start, s.y_start, 
                                                  s.x_end, s.y_end, 
                                                  outline='red', width=1)
        
        y_axis = sa.analysis_over_rectangle(d)
                
    elif d.shape.name == 'Oval':
        
        d.shape.drawing = event.widget.create_oval(s.x_start, s.y_start, s.x_end, 
                                             s.y_end, outline='red', width=1)
        
        y_axis = sa.analysis_over_oval(d)
    
    elif d.shape.name == 'Polygon':
        
        #draw the shape
        draw_polygon(event.widget, d.shape)
        
        y_axis = sa.analysis_over_polygon(d)
                
    #plot the data
    x_axis = plot.x_axis(d.s.data[0][0], d.beam)
    
    r = fc.get_row(d.frame, 0)
    
    #make y_axis the same length as the x_axis
    if len(y_axis) > len(x_axis):
        y_axis = plot.shorten_y(y_axis, len(x_axis))
    #TODO: figure out why no plot
    plot.plot_linear(d, x_axis, y_axis, 'Spectra', r, 0)
    
    #set sTEM
    d.sTEM.data = y_axis

    d.shape.made = True
    
    #enable button
    button.configure(state='normal')
    
    # #TODO: make method to show line results (sTEM)

    return

#clear the shape
def clear_shape(event, d, button):
    """
    Clear all important shape-related information

    Parameters
    ----------
    event : tk.Event
        Right-click with mouse.
    d : global_arrays.Changing_Globals
        All global variables.
    button : tk.Button
        Disable analysis button.

    Returns
    -------
    None.

    """
    
    #clear the shape from the screen
    delete_diagram(d.shape, event.widget)
    
    #reset variables
    d.shape.made = False
    d.shape.points.clear()
    d.shape.cords.clear()
    d.shape.drawn_lines.clear()
    
    #delete the frame
    fc.destroy_one(d.frame, 2, 0)
    
    button.configure(state='disabled')
    
    return

#draw polygon
def draw_polygon(widget, s):
    """
    Draws a polygon on the figure

    Parameters
    ----------
    widget : tk.Canvas, tk.Frame
        Where the polygon needs placed.
    s : global_arrays.Changing_Globals
        All global variables.

    Returns
    -------
    None.

    """
    
    s.points.append(tuple((s.x_end, s.y_end)))
    
    #make all lines in the figure
    for i in range(len(s.points) - 1):
        s.drawing = widget.create_line(s.points[i][0], s.points[i][1], 
                                       s.points[i + 1][0], s.points[i + 1][1], 
                                       fill='red', width=1)
        s.drawn_lines.append(s.drawing)
        
    #make final line
    i = len(s.points) - 1
    s.drawing = widget.create_line(s.points[i][0], s.points[i][1], 
                                   s.points[0][0], s.points[0][1], 
                                   fill='red', width='1')
    s.drawn_lines.append(s.drawing)
    
    #s.points.append(tuple((s.x_end, s.y_end)))
    s.cords.append(tuple((s.x1, s.y1)))
    
    return
#TODO: figure out why the overlay line is printing incorrectly
"""DRAWING ON OVERLAY"""
def end_line(d, event):
    """
    When the drawing of a line ends, perform the line analysis

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    event : tk.Event
        Mouse is released.

    Returns
    -------
    None.

    """
    
    s = d.shape
    
    #get end cords
    get_cord(s, event, 'line_end')
    
    #if the shape had been made, delete it
    if s.line_made:
        event.widget.delete(s.line)
    
    #get the width
    width = get_width(s.width)
    
    #display waiting message
    mtxt.load(d.text)
    
    #make line
    s.line = event.widget.create_line(s.line_x_start, s.line_y_start,  s.line_x_end, s.line_y_end, fill='black', width=width)
    
    sa.line_profile_analysis(d, width)
    
    #clear text
    mtxt.clear_text(d.text)
    
    #set the boolean value
    s.line_made = True
    
    return

def clear_line(d, event):
    """
    Clear the line from the overlay

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    event : tk.Event
        Right-click with mouse.

    Returns
    -------
    None.

    """
    
    #delete the line
    event.widget.delete(d.shape.line)
    d.shape.line_made = False
    
    #destroy the spectra below the overlay
    fc.destroy_one(d.frame, 1, 2)
    
    return

#TODO: consider changing get_cord to return the cordinates and not care about if statements