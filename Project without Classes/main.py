# -*- coding: utf-8 -*-
"""
Created on Tue May 31 14:46:18 2022

@author: Alyssa Blanc
"""

#%matplotlib qt

import tkinter as tk
import hyperspy.api as hs
#import numpy as np
#import matplotlib.pyplot as plt
import os
import matplotlib
import global_arrays as glb #DONE
import format_frames as ff #DONE
import open_and_save as oas #DONE
import manipulate_text as mtxt #DONE
import plotting as plot #DONE
import drawing_shapes as ds #DONE
import numeric_analysis as na #IN PROGRESS
import frame_changer as fc

#some global variables
shape = glb.Shape()
d = glb.Changing_Globals()
d.shape = shape

#open file
def open_file(file_type):   
    """
    Opens microscope data for analysis

    Parameters
    ----------
    file_type : string
        .type of file to open.

    Returns
    -------
    None.

    """
    
    matplotlib.use('nbagg')
    
    #open file
    filepath, signal_type = oas.get_filepath(file_type)
    
    if not filepath:
        return
    
    #clear display of previous data and reset buttons        
    oas.reset_display(frm_left_bar, d)
    
    #set global signal type
    d.signal = signal_type

    #load the file (as laxy if too large)
    file_size = os.path.getsize(filepath)
    if file_size < 1000000000:
        d.s = hs.load(filepath, d.signal)
    else:
        d.s = hs.load(filepath, d.signal, lazy=True)   
    
    #get the beam energy of the signal
    if file_type != '.emd':
        
        #get the beam energy of the signal
        be = 200
        if len(d.s.data) / be != 20.48:
            if d.signal == 'EDS_TEM':
                be = d.s.metadata.Acquisition_instrument.TEM.beam_energy
            else:
                be = d.s.metadata.Acquisition_instrument.SEM.beam_energy 
        d.beam = be
        
        #enable elements
        for ele in elements:
            if ele.name in d.s.metadata.Sample.elements:
                ele.change_button_color()  
                
        #add lines to the element
        d.s.add_lines()
                
    if d.signal == 'EDS_TEM':
        
        d.s.add_lines()
        
        #enable xray lines
        oas.enable_xray_lines(elements, d.s)
        
        #create axes  
        #print(d.beam)
        d.x_axis = plot.x_axis(d.s.data, d.beam)
        y_axis = d.s.data
        
        #plot the data
        plot.plot_linear(d, d.x_axis, y_axis, 'Raw', 0, 0)
            
        #enable model button
        global btn_lines, btn_model
        btn_lines.configure(state='normal')
        btn_model.configure(state='normal')

        #plot the image with lines
        matplotlib.use('tkagg')
        d.s.plot(True)
        
    elif d.signal == 'EDS_SEM': 
        
        #enable map button
        global btn_map
        btn_map.configure(state='normal')
        
        #load image if it exists
        oas.load_image(filepath, d.frame)
        
        #choose plotting actions based on type of file
        if file_type == '.spd':
            d.s.add_lines()
            
            #enable xray lines
            for ele in elements:
                for line in ele.lines:
                    if line.full_name in d.s.metadata.Sample.xray_lines:
                        line.bool.set(True)
                                
            #if they don't want the popup windows
            pixel_num = len(d.s.data) * len(d.s.data[0])
            
            #plot in plane
            
            #display initial waiting text
            mtxt.pixel_output(d.text, pixel_num)
            
            #make an array of pixels
            img_array = oas.pixel_intensities(d, pixel_num)
            
            #plot the 2D image
            can = plot.plot_2D(d.frame, img_array, 'Spectrum Image', 0)
            d.spectra_row = fc.get_row(d.frame, 0)
            
            #bind functions to the canvas
            can.get_tk_widget().bind('<Button-1>', lambda event: ds.start_point(event, clicked, d.shape))
            can.get_tk_widget().bind('<ButtonRelease-1>', lambda event: ds.end_point(event, d, btn_lines))
            can.get_tk_widget().bind('<Button-3>', lambda event: ds.clear_shape(event, d, btn_lines))
            
            #change the button state
            ent_weight.configure(state='normal')
            
        elif file_type == '.emd':
            
            #TODO: finish manipulating data
            for i in d.s:
                print(i.metadata)
                
            return
            
        elif file_type == '.msa':
            
            return
        
        elif file_type == '.h5':
            
            return
            
    #change the gloabl variable to reflect the data is shown
    d.data = True
            
    return
    
#add widgets to all frames

def add_to_left_bar():
    """
    Add buttons into the left frame

    Returns
    -------
    None.

    """
    #make buttons
    global btn_lines, btn_model, btn_analysis, btn_map, btn_overlay, can_lb
    global ent_weight, drop, clicked
    btn_lines = tk.Button(master=frm_left_bar, text='Check Element Lines', command = lambda: plot.plot_lines(d, True), state='disabled')
    check_lines= tk.Checkbutton(frm_left_bar, text='Lock Display', variable=d.plot, onvalue=True, offvalue=False)
    btn_model = tk.Button(master=frm_left_bar, text="Display Model", command = lambda: plot.show_model(d, btn_analysis), state='disabled')
    lbl_weight = tk.Label(master=frm_left_bar, text='Line Weight:')
    ent_weight = tk.Entry(master=frm_left_bar, state = 'disabled')
    lbl_shape = tk.Label(master=frm_left_bar, text='Shape Type:')
    shape.width = ent_weight
    
    #make dropdown menu
    options = [
        'Line',
        'Rectangle',
        'Oval',
        'Polygon'
        ]
    clicked = tk.StringVar()
    clicked.set('Line')
    drop = tk.OptionMenu(frm_left_bar, clicked, *options)
    
    btn_analysis = tk.Button(master=frm_left_bar, text="Run Analysis", command=lambda: na.run_TEM_analysis(d), state='disabled')
    btn_map = tk.Button(master=frm_left_bar, text="Element Maps", command = lambda: plot.show_individual_maps(d, btn_overlay), state='disabled')
    btn_overlay = tk.Button(master=frm_left_bar, text="Overlay Maps", command=lambda: plot.show_overlay_map(d), state='disabled')
    
    #add to frame
    for v in (btn_lines, check_lines, btn_model, btn_analysis, lbl_weight,ent_weight,lbl_shape,drop, btn_map, btn_overlay):
        v.grid(row=fc.get_row(frm_left_bar, 0), column=0, sticky='ew', padx=5, pady=5)
    
"""WINDOW LEVEL"""
#create new window
w = tk.Tk()
ff.format_window(w)
#ff.add_menu(w, open_file, save_file)

"""FIRST LEVEL FRAMES"""
#create all frames in w
frm_main = tk.Frame(w)
ff.format_main(frm_main)

frm_bottom_bar = tk.Frame(w)
ff.format_bottom_bar(frm_bottom_bar)

"""SECOND LEVEL FRAMES"""
#create all frames in main
frm_left_bar = tk.Frame(frm_main, relief=tk.RAISED, bd=2)
ff.format_left_bar(frm_left_bar)
add_to_left_bar()

frm_display = tk.Frame(frm_main)
ff.format_display(frm_display)

#create all frames in bottom bar
frm_element = tk.Frame(frm_bottom_bar, relief=tk.RAISED, bd=2)
ff.format_element(frm_element)
elements = ff.add_to_element(frm_element, d, btn_analysis, btn_overlay)
d.elements = elements

frm_output = tk.Frame(frm_bottom_bar)
ff.format_output(frm_output)
txt_output = ff.add_to_output(frm_output)
d.text = txt_output

#now add menu since txt_output hass been declared
ff.add_menu(w, open_file, txt_output)


"""THIRD LEVEL FRAMES"""
#create all frames in display
canvas = tk.Canvas(frm_display)
scroll_y = tk.Scrollbar(frm_display, orient='vertical', command=canvas.yview)
scroll_x = tk.Scrollbar(frm_display, orient='horizontal', command=canvas.xview)

"""FOURTH LEVEL FRAMES"""
#create all frames in canvas
scrollable_frame = tk.Frame(canvas)
ff.format_canvas(canvas, scroll_y, scroll_x, scrollable_frame)
d.frame = scrollable_frame

#run application
w.mainloop()

""" 
TODO: 
    
    With model manipulation, attempt background removal
        
    Print data with spectra for spds
        
    Consider trying get_lines_intensity on TEM data
    
    Consider adding loading screen for line profile
                
"""