# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 09:38:07 2022

@author: Alyssa Blanc
"""
import global_arrays as glb
import plotting as plot
from hyperspy.misc.elements import elements as elements_db
import matplotlib
import tkinter as tk

#when an element button is pressed
def pressed(d, b, analysis, overlay):
    """
    Actions to perform if a button is pressed

    Parameters
    ----------
    d : glb.Changing_Globals
        All global variables.
    b : tk.Button
        Element button.
    analysis : function
        Function for analysis of elements.
    overlay : function
        Function to create overlay maps.

    Returns
    -------
    None.

    """
    
    #get background color
    color = b.button.cget('bg')
    
    #if blue, remove proper elements
    if color == 'CadetBlue1':
        
        #remove the element
        d.s.metadata.Sample.elements.remove(b.name)
        
        #remove from x-ray lines
        i = 0
        while i < len(d.s.metadata.Sample.xray_lines):
            
            line = d.s.metadata.Sample.xray_lines[i]
            split = line.partition('_')
            ele_name = split[0]
            
            #if the line belongs to the element removed
            if b.name == ele_name:
                
                d.s.metadata.Sample.xray_lines.remove(line)
                i -= 1 #keep program from incrementing
                
            #set global lines
            for l in glb.poss_lines:
                for line in b.lines:
                    if line.name == l:
                        line.bool.set(False)
                        line.bool.set(False)
            
            #increment
            i += 1
            
    #if normal, add the proper elements
    else:
        
        #add the element and set the lines
        d.s.add_elements([b.name])
        d.s.add_lines()
        
        #set globals
        for l in glb.poss_lines:
            for line in b.lines:
                if line.bool.set(True):
                    line.map.set(False)
                    
    #change the button color
    b.change_button_color()
    
    #display the graphs
    if d.model:
        plot.show_model(d, analysis)
    if d.chi_squared:
        plot.show_chi_squared(d)
    if d.residual:
        plot.show_residual(d)
    if d.maps:
        plot.show_individual_maps(d, overlay)
    if d.overlay:
        plot.plot_overlay(d)
        
    #plot lines
    plot.plot_lines(d, True)
    
    return

#get energy
def get_energy(d):
    """
    Get the energy of the sample

    Parameters
    ----------
    d : glb.Changing_Globals
        All global variables.

    Returns
    -------
    float
        Energy of sample.

    """
    
    if d.signal == 'EDS_TEM':
        return len(d.s.data) / d.beam
    elif d.signal == 'EDS_SEM' and d.shape.made == True:
        return len(d.sTEM.data) / d.beam
    
    return

#if mouse scrolls over an element button
def over(d, b):
    """
    Actions to perform if a mouse scrolls over an element

    Parameters
    ----------
    d : glb.Changing_Globals
        All global variables.
    b : tk.Button
        Element button.

    Returns
    -------
    None.

    """
    
    #if the button can be pressed
    if b.button.cget('state') == 'normal':
        
        #get the max energy
        max_energy = get_energy(d)
        
        #make array of lines
        test_lines = []
        for l in glb.poss_lines:
            for line in elements_db[b.name]['Atomic_properties']['Xray_lines']:
                
                #if line is in possible lines array
                if line == l:
                    
                    #check that the energy of the line is valid
                    energy = elements_db[b.name]['Atomic_properties']['Xray_lines'][line]['energy (keV)']
                    if energy < max_energy:
                        name = b.name + '_' + l
                        test_lines.append(name)
                        
        #plot
        matplotlib.use('tkagg')
        plot.plot_lines(d, test_lines)
    
    return

#if mouse leave element
def leaving(event):
    """
    Actions to perform if the mouse leaves the area of the element button

    Parameters
    ----------
    event : tk.Event
        Event of mouse leaving the button.

    Returns
    -------
    None.

    """
    
    matplotlib.use('nbagg')
    
    return

#if element is right-clicked, display menu
def right_clicked(d, b, analysis, overlay, event):
    """
    Actions to perform if an element button is right-clicked

    Parameters
    ----------
    d : glb.Changing_Globals
        All global variables.
    b : tk.Button
        Element button.
    analysis : function
        Function to perform analysis of elements.
    overlay : function
        Function to get element overlays.
    event : tk.Event
        Event of right-clicking an element button.

    Returns
    -------
    None.

    """
    
    #if button can be pressed
    if b.button.cget('state') == 'normal':
        
        #make general menu
        m = tk.Menu(event.widget, tearoff=0)
        
        #get max energy
        max_energy = get_energy(d)
        
        #see which lines should be placed in the menu
        for l in glb.poss_lines:
            for line in b.lines:
                if line.name == l:
                    
                    #make sure energy is proper
                    energy = elements_db[b.name]['Atomic_properties']['Xray_lines'][line.name]['energy (keV)']
                    if energy < max_energy:
                        
                        #see if the line should be added or removed
                        if line.full_name in d.s.metadata.Sample.xray_lines:
                            line.bool.set(True)
                        else:
                            line.bool.set(False)
                        
                        #add checkbox to menu
                        m.add_checkbutton(label=line.name, onvalue=True, offvalue=False, variable=line.bool, command=lambda: add_line(d, analysis, overlay))
                        
        m.tk_popup(event.x_root, event.y_root)
        
    return

#add line to element
def add_line(d, analysis, overlay):
    """
    Add element lines to the sample

    Parameters
    ----------
    d : glb.Changing_Globals
        All global variables.
    analysis : function
        Function for elemental analysis.
    overlay : function
        Function to get elemental overlays.

    Returns
    -------
    None.

    """
    
    #go through all possible variations
    for ele in d.elements:
        for line in ele.lines:
            
            #if true, add to d.s
            if line.bool.get():
                
                d.s.add_elements([ele.name])
                d.s.add_lines([line.full_name])
                
                #set button color
                if ele.button.cget('bg') == 'SystemButtonFace':
                    ele.button.configure(bg='CadetBlue1')
                    
            #if false, remove from x-ray lines
            else:
                #check if the line exists
                if line.full_name in d.s.metadata.Sample.xray_lines:
                    
                    d.s.metadata.Sample.xray_lines.remove(line.full_name)
                    
                    #see if all of the element's lines are false                    
                    all_false = True
                    for l in ele.lines:
                            #if one is true
                            if l.bool.get():
                                all_false = True
                    
                    #if all false, remove from elements
                    if all_false:
                        d.s.metadata.Sample.elements.remove(ele.name)
                        
                        #change button color
                        if ele.button.cget('bg') == 'CadetBlue1':
                            ele.button.configure(bg='SystemButtonFace')
                            
                    #if line in overlay, make false
                    line.map.set(False)
                    
    #show lines
    plot.plot_lines(d, True)
    
    #display info
    if d.model:
        plot.show_model(d, analysis)
    if d.chi_squared:
        plot.show_residual(d)
    if d.residual:
        plot.show_residual(d)
    if d.maps:
        plot.show_individual_maps(d, overlay)
    if d.overlay:
        plot.plot_overlay(d)
                        
    return