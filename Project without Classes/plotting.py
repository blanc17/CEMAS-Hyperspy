# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 14:30:05 2022

@author: Alyssa Blanc
"""
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import frame_changer as fc
import matplotlib
import manipulate_text as mtxt
import format_frames as ff
import matplotlib.patches as mpatches
import drawing_shapes as ds


"""HELPER METHODS"""
#create the x axis
def x_axis(array, beam):
    """
    Create an x-axis

    Parameters
    ----------
    array : np.ndarray; np.memmap
        Array to get the length of the x-axis.
    beam : float
        Beam energy.

    Returns
    -------
    x : list
        X-axis.

    """
    x = []
    x_len = len(array)/beam
    
    for i in np.arange(0, x_len, 0.005):
        x.append(round(i, 3))
    
    return x

#create empty y axis
def y_axis(array):
    """
    Create y-axis

    Parameters
    ----------
    array : np.ndarray, mp.memmap
        Array to get an empty Y-axis.

    Returns
    -------
    y : list
        Y-axis.

    """
    y = []
    for i in range(len(array)):
        y.append(0)
        
    return y

def shorten_y(axis, new_len):
    """
    Shorten the y-axis data to match the length of the x-axis

    Parameters
    ----------
    axis : list, numpy.ndarray
        Initial y-axis.
    new_len : int
        Desired length of y-axis.

    Returns
    -------
    y : list
        Final y-axis.

    """
    
    y = []
    print(new_len)
    
    for i in range(new_len):
        y.append(axis[i])
    
    return y

#plot the element lines in a pop-out window
def plot_lines(d, var):
    """
    Plot the lines of the in a pop-out window

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    var : bool, list
        Variable to determine if all lines in the data or theoretical lines in
        the data should be printed on the figure.

    Returns
    -------
    None.

    """
    
    matplotlib.use('nbagg')
    
    #if TEM
    if d.signal == 'EDS_TEM':
        
        matplotlib.use('tkagg')
        d.s.plot(var)
        
    #if SEM
    elif d.signal == 'EDS_SEM' and d.shape.made == True:
        
        matplotlib.use('tkagg')
        
        #force data to be the proper length
        while len(d.sTEM.data) != 4096:
            array = list(d.sTEM.data)
            array.append(0)
            d.sTEM.data = array
        
        #update elements and lines
        d.sTEM.metadata.Sample.elements = d.s.metadata.Sample.elements
        d.sTEM.metadata.Sample.xray_lines = d.s.metadata.Sample.xray_lines
        
        d.sTEM.plot(var)
    
    return

"""PLOTTING SIGNALS"""
#plot linear data
def plot_linear(d, x, y, name, r, c):
    """
    Plots 2D representation of the data

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    x : list
        X-axis.
    y : numpy.ndarry, list
        Y-axis.
    name : str
        Name of graph.
    r : int
        Row number.
    c : int
        Column number.

    Returns
    -------
    None.

    """
    
    matplotlib.use('nbagg')
    
    #make new frame
    frm = tk.Frame(d.frame)
    frm.rowconfigure(0, weight=1)
    frm.columnconfigure(0, weight=1)
    frm.grid(row=r, column=c, sticky='nsew')
    
    #make new variable for plot
    p = plt
    
    #create figure to display
    fig = p.figure(figsize=(8,4))
    
    #plot the data
    if name != 'Model':
        fig.add_subplot(111).plot(x, y, 'r')
    #if figure is a model, plot model
    else:
        y_data = d.m.signal
        fig.add_subplot(111).plot(x, y_data, 'r.', x, y, 'b')
        
    #format plot
    p.title('%s data'%name)
    p.xlabel('Energy axis (keV)')
    p.ylabel('Intensity')
    
    #create canvas
    can = FigureCanvasTkAgg(fig, master=frm)
    can.draw()
    can.get_tk_widget().grid(row=0, column=0, sticky='nsew')
    
    #create toolbar
    t = NavigationToolbar2Tk(can, frm, pack_toolbar=False)
    t.update()
    t.grid(row=1, column=0, sticky='ew')
    
    return

#plot 2D images like spd data
def plot_2D(frame, array, name, c):
    """
    Plots 2D image mapping of data

    Parameters
    ----------
    frame : tk.Frame
        Frame to place data in.
    array : list
        List storing image made of pixels and intensities.
    name : str
        Name of graph.
    c : int
        Column number.

    Returns
    -------
    cnv : tk.Canvas
        Tkinter canvas with image.

    """
    
    #make frame
    frm = tk.Frame(frame)
    
    #make plot
    p = plt
    
    #make the figure
    fig = p.figure(figsize=(8,5))
    #update the image
    p.imshow(array, cmap='gray')
    p.title(name)
    p.xlabel('x axis')
    p.ylabel('y axis')
    p.colorbar()
    
    #make the canvas
    cnv = FigureCanvasTkAgg(fig, master=frm)
    cnv.draw()
    
    #grid the canvas
    r = fc.get_row(frame, c)
    cnv.get_tk_widget().grid(row=0, column=0, sticky='nesw')
    
    #make a toolbar
    tool = NavigationToolbar2Tk(cnv, frm, pack_toolbar=False)
    tool.update()
    tool.grid(row=1, column=0, sticky='new')
    
    #grid the frame
    frm.grid(row=r, column=c, sticky='nesw')
    
    return cnv

"""TEM PLOTTING"""
#model data
def show_model(d, button):
    """
    Displays a model of the data

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    button : tk.Button
        Tkinter button for analysis of the data.

    Returns
    -------
    None.

    """
    
    matplotlib.use('nbagg')
    
    #display loading text
    mtxt.load(d.text)
    
    #destroy the old frame for the model
    fc.destroy_one(d.frame, 1, 0)
    r, c = 0, 0
    if d.signal == 'EDS_TEM':
        d.m = d.s.create_model()
        r, c = 1, 0
    elif d.signal == 'EDS_SEM':
        d.m = d.sTEM.create_model
        r, c = 3, 0
    d.m.fit_background()
    d.s_model = d.m.as_signal()
    
    #plot the figure
    plot_linear(d, d.x_axis, d.s_model.data, 'Model', r, c)
    d.model = True
    
    #clear loading bar
    mtxt.clear_text(d.text)
    
    #update buttons
    button.configure(state='normal')
    
    return

#residual data
def show_residual(d):
    """
    Shows the residual of the model compared to the data

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.

    Returns
    -------
    None.

    """
    
    matplotlib.use('nbagg')
    
    #get data
    y_axis = []
    r, c = 0, 0
    for i in range(len(d.x_axis)):
        if d.signal == 'EDS_TEM':
            y_axis.append(int(d.s.data[i] - d.s_model.data[i]))
            r, c = 0, 1
        elif d.signal == 'EDS_SEM':
            y_axis.append(int(d.sTEM.data[i] - d.s_model.data[i]))
            r, c = 4, 0
        
    #plot the data
    plot_linear(d, d.x_axis, y_axis, 'Residual', r, c)
    d.residual = True
    
    return
    
#chi-squared
def show_chi_squared(d):
    """
    Shows the chi squared of the model and the data

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.

    Returns
    -------
    None.

    """
    
    matplotlib.use('nbagg')
    
    #get data
    y_axis = []
    r, c = 0, 0
    for i in range(len(d.x_axis)):
        num = 0
        if d.signal == 'EDS_TEM':
            num = int(d.s.data[i] - d.s_model.data[i])
            r, c = 1, 1
        elif d.signal == 'EDS_SEM':
            num = int(d.sTEM.data[i] - d.s_model.data[i])
            r, c = 5, 0
        y_axis.append(num**2 / d.s_model.data[i])
        
    #plot the data
    plot_linear(d, d.x_axis, y_axis, 'Chi-Squared', r, c)
    d.chi_squared = True
    
    return
    
"""SEM PLOTTING"""
#change the color of a plot
def change_color(d):
    """
    Change the color of an element map

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All gloal variables.

    Returns
    -------
    None.

    """
    
    matplotlib.use('nbagg')
    
    #delete all of the widgets in the first and second columns
    fc.destroy_column(d.frame, 1)
    fc.destroy_column(d.frame, 2)
    
    #print all color maps
    r = 0
    for l in d.s.metadata.Sample.xray_lines:
        for ele in d.elements:
            for line in ele.lines:
                if line.full_name == l:
                    
                    #plot the element
                    elemental_plot(d, l, line.color.get(), r, 1)
                    r += 1
                    
    #make the overlay if needed
    if d.overlay:
        plot_overlay(d)
    
    return

#plot the individual map
def elemental_plot(d, line, color, r, c):
    """
    Generate a 2D plot of an element

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    line : str
        Name of element line.
    color : str
        String of color.
    r : int
        Row number.
    c : int
        Column number.

    Returns
    -------
    None.

    """
    
    #get the line instensities
    im = d.s.get_lines_intensity([line])
    
    #make the plot
    pl = plt
    
    #make the figure
    fig = pl.figure(figsize=(8, 5))
    
    #update the plot and figure
    pl.imshow(im[0].data, cmap=color)
    pl.title(line)
    pl.xlabel('x axis')
    pl.ylabel('y axis')
    pl.colorbar()
    
    #make the canvas
    can = FigureCanvasTkAgg(fig, master=d.frame)
    can.draw()
    can.get_tk_widget().grid(row=r, column=c, sticky='nesw')
    
    #make the menu
    can.get_tk_widget().bind("<Button-3>", lambda event: ff.color_menu(d, change_color, event))
    
    return

#show the individual element maps
def show_individual_maps(d, button):
    """
    Plot all colored element maps

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All changing variables.
    button : tk.Button
        Button to enable the analysis of 2D models.

    Returns
    -------
    None.

    """
    
    matplotlib.use('nbagg')
    
    #destroy all children in column 1
    fc.destroy_column(d.frame, 1)
    
    #print all color maps
    r = 0
    for l in d.s.metadata.Sample.xray_lines:
        for ele in d.elements:
            for line in ele.lines:
                if line.full_name == l:
                    
                    #plot the element
                    elemental_plot(d, l, line.color.get(), r, 1)
                    r += 1
    
    #make displaying maps true
    d.maps = True
    
    #change button state
    button.configure(state='normal')
    
    return

def plot_overlay(d):
    """
    Plots a 2D image that can enable lines to be drawn on it

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.

    Returns
    -------
    None.

    """
    
    matplotlib.use('nbagg')
    
    #make frame
    frm = tk.Frame(d.frame)
    frm.grid(row=0, column=2, sticky='nesw')
    
    #get intensities
    im = d.s.get_lines_intensity()
    
    #make plot
    pl = plt
    
    #make figure
    fig = pl.figure(figsize=(8, 5))
    
    #update plot and figure
    pl.title('Overlay')
    pl.xlabel('x axis')
    pl.ylabel('y axis')
    
    #get the number of elements in the overlay
    num = 0
    for ele in d.elements:
        for line in ele.lines:
            
            #if in map
            if line.map.get():
                num += 1
                
    #if zero, remove all plots in column 2
    if num == 0:
        fc.destroy_column(d.frame, 2)
    else:
        
        #set alpha
        decrement = 1.0 / num
        a = 0
        legend = []
        
        #iterate
        for ele in d.elements:
            for line in ele.lines:
                
                #if the line is in the map
                if line.map.get():
                    
                    #get color and alpha
                    color = line.color.get()
                    alpha = 1.0 - (a * decrement)
                    
                    #get the element being displayed
                    index = 0
                    for x in range(len(im)):
                        if im[x].metadata.Sample.xray_lines[0] == line.full_name:
                            index = x
                            
                    #plot the image
                    pl.imshow(im[index].data, cmap=color, alpha=alpha)
                    
                    #update legend
                    patch = mpatches.Patch(color=color.lower()[:-1], label=line.full_name)
                    legend.append(patch)
                    
                    a += 1
        
        #plot legend
        pl.legend(handles=legend)
        
        #make canvas
        can = FigureCanvasTkAgg(fig, master=frm)
        can.draw()
        can.get_tk_widget().grid(row=0, column=0, sticky='nesw')
        
        #bind to canvas line analysis
        #TODO: bind analysis
        can.get_tk_widget().bind('<Button-1>', lambda event: ds.get_cord(d.shape, event, 'line_begin'))
        can.get_tk_widget().bind('<ButtonRelease-1>', lambda event: ds.end_line(d, event))
        can.get_tk_widget().bind('<Button-3>', lambda event: ds.clear_line(d, event))
        
        #make toolbar
        tool = NavigationToolbar2Tk(can, frm, pack_toolbar=False)
        tool.update()
        tool.grid(row=1, column=0, sticky='nesw')
    
    return

#quit the overlay and plot the data
def quit_overlay(d, w):
    """
    Destroy the overlay window

    Parameters
    ----------
    d : glabal_arrays.Changing_Globals
        All global variables.
    w : tk.Toplevel
        Window for overlay.

    Returns
    -------
    None.

    """
    
    #destroy all of column 2
    fc.destroy_column(d.frame, 2)
    
    #plot the figure
    plot_overlay(d)
    
    #destroy the top window
    w.destroy()
    w.update()
    
    return

#show the overlay map
def show_overlay_map(d):
    """
    Plot the overlay of 2D data

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All gloal variables.

    Returns
    -------
    None.

    """
    
    matplotlib.use('nbagg')
    
    #make pop-out window
    ff.overlay_window(d, quit_overlay)
    
    #set display true
    d.overlay = True
    
    return

#line profile plotting
def plot_profile_vertical(data, r, c, d):
    """
    From the 2D figure, plot a line profile once a line is drawn on the shape

    Parameters
    ----------
    data : dict
        Dictionary of elements and correspoding intensities.
    r : int
        Row number.
    c : int
        Column number.
    d : global_arrays.Changing_Globals
        All global variables.

    Returns
    -------
    None.

    """
    
    matplotlib.use('nbagg')
    
    #make new frame
    frm = tk.Frame(d.frame)
    frm.rowconfigure(0, weight=1)
    frm.columnconfigure(0, weight=1)
    frm.grid(row=r, column=c, sticky='nesw')
    
    #make plot
    pl = plt
    
    #create figure
    fig = pl.figure(figsize=(8,5))
    
    #plot data
    for key, value in data.items():
                
        #make x-axis and y-axis
        x_axis, y_axis = [], []
        for k,v in value.items():
            x_axis.append(k)
            y_axis.append(v)
            
        #get color
        color = 'r'
        for ele in d.elements:
            for line in ele.lines:
                if line.full_name == key:
                    color = line.color.get()[:-1].lower()
                    
        pl.plot(x_axis, y_axis, label=key, color=color)
        
    #format plot
    pl.title('Overlay data')
    pl.xlabel('Pixel')
    pl.ylabel('Intensity')
    pl.legend()
    
    #create canvas
    can = FigureCanvasTkAgg(fig, frm)
    can.draw()
    can.get_tk_widget().grid(row=0, column=0, sticky='nesw')
    
    #create toolbar
    tool = NavigationToolbar2Tk(can, frm, pack_toolbar=False)
    tool.update()
    tool.grid(row=1, column=0, sticky='ew')

    return

#line profile plotting
def plot_profile(data, line, r, c, d):
    """
    From the 2D figure, plot a line profile once a line is drawn on the shape

    Parameters
    ----------
    data : dict
        Dictionary of elements and correspoding intensities.
    r : int
        Row number.
    c : int
        Column number.
    d : global_arrays.Changing_Globals
        All global variables.

    Returns
    -------
    None.

    """
    
    matplotlib.use('nbagg')
    
    #make new frame
    frm = tk.Frame(d.frame)
    frm.rowconfigure(0, weight=1)
    frm.columnconfigure(0, weight=1)
    frm.grid(row=r, column=c, sticky='nesw')
    
    #make plot
    pl = plt
    
    #create figure
    fig = pl.figure(figsize=(8,5))
    
    #plot data
    x_axis, y_axis = [], []
    for x in data:
        x_axis.append(x[0])
        y_axis.append(x[1])
            
    #get color
    color = 'r'
    for ele in d.elements:
        for line in ele.lines:
            if line.full_name == line:
                color = line.color.get()[:-1].lower()
                
    pl.plot(x_axis, y_axis, label=line, color=color)
        
    #format plot
    pl.title('Overlay data')
    pl.xlabel('Pixel')
    pl.ylabel('Intensity')
    pl.legend()
    
    #create canvas
    can = FigureCanvasTkAgg(fig, frm)
    can.draw()
    can.get_tk_widget().grid(row=0, column=0, sticky='nesw')
    
    #create toolbar
    tool = NavigationToolbar2Tk(can, frm, pack_toolbar=False)
    tool.update()
    tool.grid(row=1, column=0, sticky='ew')

    return