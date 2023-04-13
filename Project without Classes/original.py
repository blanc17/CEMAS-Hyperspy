# -*- coding: utf-8 -*-
"""
Created on Tue May 31 14:46:18 2022

@author: Alyssa Blanc
"""

#%matplotlib qt

import tkinter as tk
import tkinter.font as font
from tkinter.filedialog import askopenfilename, asksaveasfilename
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import hyperspy.api as hs
import numpy as np
import matplotlib.pyplot as plt
import math
import re
#import hyperspyui
import os
#import hyperspyui as hsui
from matplotlib.backends import backend_tkagg
from matplotlib.figure import Figure
#import hyperspy.io as hsio
import matplotlib
import scipy
import matplotlib.patches as mpatches
from hyperspy.misc.elements import elements as elements_db
#import hyperspy.drawing as hsd
from PIL import ImageTk, Image
from os.path import exists
from shell_files import k_shells, l_shells
import matplotlib.path as mpltPath
#from matplotlib.backend_bases import MouseButton

FigureCanvas = backend_tkagg.FigureCanvasTkAgg

class Line:
    def __init__(self, line, color, ele):
        self.name = line
        self.full_name = ele + '_' + line
        self.bool = tk.BooleanVar()
        self.bool.set(False)
        self.color = tk.StringVar()
        self.color.set(color)
        self.map = tk.BooleanVar()
        self.map.set(False)

class Element:
    def __init__(self, ele, r, c, color, frame):
        
        self.name = ele
        self.row = r
        self.column = c
        
        self.lines = []
        if self.name not in disabled_elements:
            for line in elements_db[self.name]['Atomic_properties']['Xray_lines']:
                l = Line(line, color, ele)
                self.lines.append(l)
                
        self.shell = tk.IntVar()
        self.shell.set(0)
        
        self.button = tk.Button(master=frame, text=self.name, font=font.Font(size=7), state= 'disabled')
        self.button.bind("<Button-1>", self.element_button_pressed)
        self.button.bind('<Enter>', self.mouse_over_element)
        self.button.bind('<Leave>', self.mouse_leaving_element)
        self.button.bind("<Button-3>", self.right_click_element)
        self.button.grid(row=r, column=c, sticky='nesw')
        
        return
    
    def reset_variables(self):
        
        #reset the button
        self.reset_buttons()
        
        #make the global variables false
        for line in self.lines:
            line.bool.set(False)
            line.map.set(False)
            
        self.shell.set(0)
        
        return
    
    def reset_buttons(self):
        
        #if element should be disabled
        if self.name in disabled_elements:
            self.button.configure(state='disabled', bg='RosyBrown1')
        #else, reset it normally
        else:
            self.button.configure(state='normal', bg='SystemButtonFace')
        
        return
    
    def change_button_color(self):
        
        #if already enabled
        if self.button.cget('bg') == 'CadetBlue1':
            self.button.configure(bg='SystemButtonFace')
        #if not already enabled
        elif self.button.cget('bg') == 'SystemButtonFace':
            self.button.configure(bg='CadetBlue1')
            
        return
    
    def element_button_pressed(self, event):

        global displayingModel, displayingAnalysis, displayingMaps, displayingOverlay
        
        #get the background color
        color_string = self.button.cget('bg')
        #remove proper elements
        if color_string=='CadetBlue1':
            #remove the element if disabling the button
            s.metadata.Sample.elements.remove(self.name)
            i=0
            while i < len(s.metadata.Sample.xray_lines):
                line = s.metadata.Sample.xray_lines[i]
                split = s.metadata.Sample.xray_lines[i].partition('_')
                eleName = split[0]
                if self.name == eleName:
                    s.metadata.Sample.xray_lines.remove(line)
                    i -= 1
                i += 1
                #set global lines
                for l in poss_lines:
                    for line in self.lines:
                        if line.name == l:
                            line.bool.set(False)
                            line.map.set(False)

        else:
            #add the color if enabling the element
            s.add_elements([self.name])
            s.add_lines()            
            #set global lines
            for l in poss_lines:
                for line in self.lines:
                    if line.name == l:
                        line.bool.set(True)
                        line.map.set(False)

        #change the button color
        self.change_button_color()
        
        #If they prefer speed
        """
        #delete model and analysis
        while len(frm_display.winfo_children()) > 1:
            frm_display.winfo_children()[1].destroy()
        global btn_analysis, displayingModel, displayingAnalysis
        btn_analysis.configure(state='disabled')
        displayingModel = False
        displayingAnalysis = False
        """
        
        #display graphs
        if displayingModel:
            show_model()
        if displayingAnalysis:
            #show models
            show_chi_squared()
            show_residual()
        if displayingMaps:
            show_individual_maps()
        if displayingOverlay:
            plot_overlay()
            
        #show lines
        line_plot(True)
        
        return
    
    #if mouse scrolls over element
    def mouse_over_element(self, event):
        global sTEM
        #if button can be pressed
        if self.button.cget('state') == 'normal':
            
            #make array of lines
            global be
            max_energy = 0
            if signal=='EDS_TEM':
                max_energy = len(s.data)/be
            elif signal=='EDS_SEM' and shape_made == True:
                #print(sTEM.data)
                max_energy = len(sTEM.data)/be
                
            test_lines = []
            for l in poss_lines:
                for line in elements_db[self.name]['Atomic_properties']['Xray_lines']:
                    #if line is in possible lines array
                    if line == l:
                        #check the energy of the line is valid
                        energy = elements_db[self.name]['Atomic_properties']['Xray_lines'][line]['energy (keV)']
                        #if less than the max, can be inserted into the menu
                        if energy < max_energy:
                            name = self.name + '_' + l
                            test_lines.append(name)
            matplotlib.use('tkagg')
            
            line_plot(test_lines)
                
        return
    
    #if mouse leaaves element
    def mouse_leaving_element(self, event):
        
        matplotlib.use('nbagg')
        
        return
    
    #if element is right clicked, display menu
    def right_click_element(self, event):

        #if button can be pressed
        if self.button.cget('state') == 'normal':
            #make general menu
            m = tk.Menu(event.widget, tearoff=0)
            #max energy of the signal
            
            #make array of lines
            global be
            max_energy = 0
            if signal=='EDS_TEM':
                max_energy = len(s.data)/be
            elif signal=='EDS_SEM' and shape_made == True:
                #print(sTEM.data)
                max_energy = 20
            #iterate through the possible lines
            for l in poss_lines:
                for line in self.lines:
                    if line.name == l:
                        energy = elements_db[self.name]['Atomic_properties']['Xray_lines'][line.name]['energy (keV)']
                        if energy < max_energy:
                            if line.full_name in s.metadata.Sample.xray_lines:
                                #make bool true
                                line.bool.set(True)
                            else:
                                line.bool.set(False)
                            #add a checkbox to the menu
                            m.add_checkbutton(label=line.name, onvalue=True, offvalue=False, variable=line.bool, command = add_line)
                            
        m.tk_popup(event.x_root, event.y_root)

        return

#some global variables

#element arrays
element_array = [['H','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','He'],
                ['Li','Be','0','0','0','0','0','0','0','0','0','0','B','C','N','O','F','Ne'],
                ['Na','Mg','0','0','0','0','0','0','0','0','0','0','Al','Si','P','S','Cl','Ar'],
                ['K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr'],
                ['Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe'],
                ['Cs','Ba','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn'],
                ['Fr','Ra','Lr','Rf','Db','Sg','Bh','Hs','Mt','Ds','Rg','Cn','Uut','Fl','Uup','Lv','Uus','Uuo'],
                ['0','0','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','0','0'],
                ['0','0','Ac','Th','Pa','U','Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No','0','0']]
disabled_elements = ['Li','Lr', 'Rf','Db','Sg','Bh','Hs','Mt','Ds','Rg','Cn','Uut','Fl','Uup','Lv','Uus','Uuo','Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No']

#possible element lines array
poss_lines = ['Ka', 'Kb', 'La', 'Lb1', 'Ma', 'Mb']

#color array
color_array = ['Greys',
               'Purples',
               'Blues',
               'Greens',
               'Oranges',
               'Reds']

#variables for if display is true
displayingData=False
displayingModel=False
displayingAnalysis=False
displayingMaps=False
displayingOverlay=False

#shell dictionary
shell_dic = {}

#plot the lines in a pop-out window
def line_plot(var):
    global s, sTEM
    
    #show lines
    matplotlib.use('nbagg')
    if signal == 'EDS_TEM':
        matplotlib.use('tkagg')
        s.plot(var)
        
    elif signal == 'EDS_SEM' and shape_made == True:
        matplotlib.use('tkagg')
        while len(sTEM.data) != 4096:
            array = list(sTEM.data)
            array.append(0)
            sTEM.data = array
        sTEM.metadata.Sample.elements = s.metadata.Sample.elements
        sTEM.metadata.Sample.xray_lines = s.metadata.Sample.xray_lines
        
        sTEM.plot(var)
    
    return

#add line of element to s
def add_line():
    
    global s
    
    #go through all possible variables
    for ele in elements:
        for line in ele.lines:
            
            #if true, add to s            
            if line.bool.get():
                                                
                s.add_elements([ele.name])
                s.add_lines([line.full_name])
                
                #set button color
                if ele.button.cget('bg') == 'SystemButtonFace':
                    ele.button.configure(bg='CadetBlue1')
                
            #if false, remove from xray_lines
            else:
                #check if the line exists
                if line.full_name in s.metadata.Sample.xray_lines:
                                        
                    s.metadata.Sample.xray_lines.remove(line.full_name)
                    
                    #see if all of the element's lines are false
                    all_false = True
                    for l in ele.lines:
                        #if one is true
                        if l.bool.get():
                            all_false = False
                    #if all false, remove from elements
                    if all_false:
                        s.metadata.Sample.elements.remove(ele.name)
                                
                    #change button color
                    if ele.button.cget('bg') == 'CadetBlue1':
                        ele.button.configure(bg='SystemButtonFace')
                    
                    #if in overlay, make false
                    line.map.set(False)
                    
    #show lines
    line_plot(True)

    #redisplay info
    global displayingModel, displayingAnalysis, displayingMaps, displayingOverlay
    #display graphs
    if displayingModel:
        show_model()
    if displayingAnalysis:
        #show models
        show_chi_squared()
        show_residual()
    if displayingMaps:
        show_individual_maps()
    if displayingOverlay:
        plot_overlay()
      
    return

#plot the raw data
def plot_data(xAxis, yAxis, n, r, c):
    matplotlib.use('nbagg')
    
    #make new frame for raw data
    frm = tk.Frame(scrollable_frame, relief=tk.RAISED, bd=2)
    frm.rowconfigure(0, weight=1)
    frm.columnconfigure(0, weight=1)
    frm.grid(row=r, column=c, sticky='nsew')
    
    #make a variable for the new plt
    pl = plt
    
    #create figure to disply
    s.add_lines()
    fig = pl.figure(figsize=(8,4))
    
    #if model, execute different plot
    if n == 'Model':
        #get axis values
        yAxisData = m.signal()
        fig.add_subplot(111).plot(xAxis, yAxisData, 'r.', 
                                        xAxis, yAxis, 'b')
    else:
        fig.add_subplot(111).plot(xAxis, yAxis, 'r')
    
    pl.title('%s data'%n)
    pl.xlabel('Energy axis (keV)')
    pl.ylabel('Intensity')
    
    #create a canvas to display
    cnv = FigureCanvasTkAgg(fig, master=frm)
    cnv.draw()
    cnv.get_tk_widget().grid(row=0, column=0, sticky='nsew')
    
    #create a toolbar for the canvas
    tl = NavigationToolbar2Tk(cnv, frm, 
                                      pack_toolbar=False)
    tl.update()
    tl.grid(row=1, column=0, sticky='ew')
    
    return

point_list = []
cord_list = []
points = []

#draw on the canvas
def start_point(event):
    global x_start, y_start, clicked, x0, y0
    if clicked.get() == 'Polygon':
        if len(point_list) == 0:
            x_start, y_start = event.x, event.y

            frm_event_cord = event.widget.grid_info()
            frm_toolbar_cord = (frm_event_cord['row']+1, frm_event_cord['column'])
            
            tool_w = event.widget
            for wid in event.widget.master.winfo_children():
                info = wid.grid_info()
                if info["row"] == frm_toolbar_cord[0]:
                    if info["column"] == frm_toolbar_cord[1]:
                        tool_w = wid
                
            cord_str = tool_w.message.get()
            split = cord_str.partition(' ')
            x_string = split[0]
            x_string = x_string.partition('=')[2]
            split = split[2].partition('\n')
            y_string = split[0]
            y_string = y_string.partition('=')[2]
            
            x0 = round(float(x_string))
            y0 = round(float(y_string))
            
            point_list.append(tuple((x_start, y_start)))
            cord_list.append(tuple((x0, y0)))
            points.append([x0, y0])
        else: 
            x_start = x_end
            y_start = y_end
            x0 = x1
            y0 = y1
            
    else:
        x_start, y_start = event.x, event.y

        frm_event_cord = event.widget.grid_info()
        frm_toolbar_cord = (frm_event_cord['row']+1, frm_event_cord['column'])
        
        tool_w = event.widget
        for wid in event.widget.master.winfo_children():
            info = wid.grid_info()
            if info["row"] == frm_toolbar_cord[0]:
                if info["column"] == frm_toolbar_cord[1]:
                    tool_w = wid
            
        cord_str = tool_w.message.get()
        split = cord_str.partition(' ')
        x_string = split[0]
        x_string = x_string.partition('=')[2]
        split = split[2].partition('\n')
        y_string = split[0]
        y_string = y_string.partition('=')[2]
        
        x0 = round(float(x_string))
        y0 = round(float(y_string))

    return

shape_made = False

def end_point(event):
    global x_end, y_end, shape_made, shape, ent_weight, clicked, drawn_lines, scrollable_frame, s
    x_end, y_end = event.x, event.y
    
    frm_event_cord = event.widget.grid_info()
    frm_toolbar_cord = (frm_event_cord['row']+1, frm_event_cord['column'])
    
    tool_w = event.widget
    for wid in event.widget.master.winfo_children():
        info = wid.grid_info()
        if info["row"] == frm_toolbar_cord[0]:
            if info["column"] == frm_toolbar_cord[1]:
                tool_w = wid
                            
    cord_str = tool_w.message.get()
    split = cord_str.partition(' ')
    x_string = split[0]
    x_string = x_string.partition('=')[2]
    split = split[2].partition('\n')
    y_string = split[0]
    y_string = y_string.partition('=')[2]
    
    global x1, y1
    x1 = round(float(x_string))
    y1 = round(float(y_string))
    
    #if shape has been made, delete it
    if clicked.get() != 'Polygon':
        if shape_made:
            event.widget.delete(shape)
            shape_made = False
            for dl in drawn_lines:
                event.widget.delete(dl)
    else:
        for dl in drawn_lines:
            event.widget.delete(dl)
        if shape_made:
            event.widget.delete(shape)
            shape_made = False
    
    #if widget in scrollable frame r2c0, delete
    for widget in scrollable_frame.winfo_children():
        info = widget.grid_info()
        if 'row'  and 'column' in info:
            if info['row'] == 2 and info['column'] == 0:
                widget.destroy()
       
    #get sTEM info
    sFile = os.path.abspath('map20210514093205751_0.spc')
    global sTEM
    sTEM = hs.load(sFile, 'EDS_TEM')
    sTEM.add_lines()
    sTEM.metadata.Sample.elements = s.metadata.Sample.elements
    sTEM.metadata.Sample.xray_lines = s.metadata.Sample.xray_lines
        
    if clicked.get() == 'Line':
        width = 1
        width_string = ent_weight.get()
        if (width_string.isnumeric()):
            width = int(width_string)
            if width == 0:
                width = 1
                ent_weight.delete(0, tk.END)
                ent_weight.insert(0, '1')
      
        shape = event.widget.create_line(x_start, y_start, x_end, y_end, 
                                         fill='red', width=width)
        analysis_over_line(width)

    #if a rectangle will be made
    elif clicked.get() == 'Rectangle':
        shape = event.widget.create_rectangle(x_start, y_start, x_end, y_end, 
                                              outline='red', width=1)
        analysis_over_rectangle()
    elif clicked.get() == 'Oval':
        shape = event.widget.create_oval(x_start, y_start, x_end, y_end, 
                                         outline='red', width=1)
        analysis_over_oval()
    elif clicked.get() == 'Polygon':
        point_list.append(tuple((x_end, y_end)))
        for i in range(len(point_list) - 1):
            shape = event.widget.create_line(point_list[i][0], point_list[i][1], 
                                             point_list[i+1][0], point_list[i+1][1], 
                                             fill='red', width=1)
            drawn_lines.append(shape)
        i = len(point_list) - 1
        shape = event.widget.create_line(point_list[i][0], point_list[i][1], 
                                         point_list[0][0], point_list[0][1], 
                                         fill='red', width=1)
        drawn_lines.append(shape)
        
        point_list.append(tuple((x_end, y_end)))
        cord_list.append(tuple((x1, y1)))
        points.append([x1, y1])
        
        analysis_over_polygon()
    
    shape_made = True
    global btn_lines
    btn_lines.configure(state='normal')
    
    #TODO: make method to show line results

    return

drawn_lines = []

#perform an analysis over the line made
def analysis_over_line(width):
    global x0, x1, y0, y1, be, sTEM
    
    #if not a straigt line down
    if x1 != x0:
        slope = (y1-y0)/(x1-x0)
        b = round(slope * (-x0) + y0)
                        
        yAxis = []
        for i in range(len(s.data[0][0])):
            yAxis.append(0)
        
        #iterate over all pixels
        for y in range(len(s.data)):
            for x in range(len(s.data[y])):
                #if the point lies on the line based on b
                poss_b = round(y-slope*x)
                if poss_b >= b-width and poss_b <= b+width:
                    #if the x and y coordinates fall within the range
                    if y >= min(y0, y1) and y <= max(y0, y1):
                        if x>= min(x0, x1) and x <= max(x0, x1):
                            yAxis += s.data[y][x]

        xAxis = []
        xlength = len(s.data[y0][x0])/be
        for i in np.arange(0, xlength, 0.005):
            xAxis.append(round(i, 3))
        
        plot_data(xAxis, yAxis, 'Spectra', 2, 0)
        
        sTEM.data = yAxis

    else:        
        min_point = min(y0, y1)
        max_point = max(y0, y1)
        
        yAxis = s.data[min_point][x0]
        while min_point < max_point:
            for x in range(xl0-width, xl0+width+1):
                min_point = min_point + 1
                temp_y = s.data[min_point][x0]
                yAxis += temp_y
        
        xAxis = []
        xlength = len(s.data[y0][x0])/be
        for i in np.arange(0, xlength, 0.005):
            xAxis.append(round(i, 3))
            
        plot_data(xAxis, yAxis, 'Spectra', 2, 0)
        
        sTEM.data = yAxis
    
    return    

def analysis_over_rectangle():
    global x0, x1, y0, y1, be, sTEM, s
    
    yAxis = []
    for i in range(len(s.data[0][0])):
        yAxis.append(0)
    
    #iterate over all pixels
    for y in range(len(s.data)):
        for x in range(len(s.data[y])):
            #if the x and y coordinates fall within the range
            if y >= min(y0, y1) and y < max(y0, y1):
                if x>= min(x0, x1) and x < max(x0, x1):
                    yAxis += s.data[y][x]
    
    xAxis = []
    xlength = len(s.data[y0][x0])/be
    for i in np.arange(0, xlength, 0.005):
        xAxis.append(round(i, 3))
        
    plot_data(xAxis, yAxis, 'Spectra', 2, 0)
    
    sTEM.data = yAxis
    
    return

def analysis_over_oval():
    global x0, x1, y0, y1, be, sTEM, s
    
    #get the midpoint
    h = (x0 + x1) / 2
    k = (y0 + y1) / 2
    
    #get the radius
    rx = abs(h-x0)
    ry = abs(k-y0)
    
    yAxis = []
    for i in range(len(s.data[0][0])):
        yAxis.append(0)
        
    for y in range(len(s.data)):
        for x in range(len(s.data[y])):
            x_check = ((x-h)**2)/(rx**2)
            y_check = ((y-k)**2)/(ry**2)
            if x_check + y_check <=1:
                yAxis += s.data[y][x]
                
    xAxis = []
    xlength = len(s.data[y0][x0])/be
    for i in np.arange(0, xlength, 0.005):
        xAxis.append(round(i, 3))
        
    plot_data(xAxis, yAxis, 'Spectra', 2, 0)
    
    sTEM.data = yAxis
    
    return

def analysis_over_polygon():
    global x0, x1, y0, y1, cord_list, be, s, sTEM
    
    #make list of points for polygon
    p_list = []
    for e in cord_list:
        temp = []
        temp.append(e[0])
        temp.append(e[1])
        p_list.append(temp)
    path = mpltPath.Path(p_list)
    inside = path.contains_points([[220,75]])
    
    if len(cord_list) == 2:
        if x0 != x1 or y0!=y1:
            analysis_over_line(1)
    else:
        #iterate over all pixels
        yAxis = []
        for i in range(len(s.data[0][0])):
            yAxis.append(0)
        
        for y in range(len(s.data)):
            for x in range(len(s.data[y])):
                p = [x, y]
                inside = path.contains_points([p])
                if inside[0]:
                    yAxis += s.data[y][x]
                        
        xAxis = []
        xlength = len(s.data[y0][x0])/be
        for i in np.arange(0, xlength, 0.005):
            xAxis.append(round(i, 3))
            
        plot_data(xAxis, yAxis, 'Spectra', 2, 0)
        
        sTEM.data = yAxis                        
    
    return

#clear lines from the canvas
def clear_shape(event):
    global shape, shape_made, point_list, clicked, drawn_lines, points
    if clicked.get() != 'Polygon':
        event.widget.delete(shape)
    else:
        for s in drawn_lines:
            event.widget.delete(s)
    shape_made=False
    point_list.clear()
    cord_list.clear()
    points.clear()
    
    #if widget in scrollable frame r2c0, delete
    for widget in scrollable_frame.winfo_children():
        info = widget.grid_info()
        if 'row'  and 'column' in info:
            if info['row'] == 2 and info['column'] == 0:
                widget.destroy()
                
    global btn_lines
    btn_lines.configure(state='disabled')
    
    return

#open file
def open_file(file_type):   
    global txt_output
    
    matplotlib.use('nbagg')
    #open file
    filepath = ''
    signal_type = ''

    if file_type == '.spc':
        filepath = askopenfilename(
            filetypes = [
                ("EDAX files", "*.spc"),
                ("All Files", "*.*")
                ]
            )
        signal_type = 'EDS_TEM'
    elif file_type == '.spd':
        filepath = askopenfilename(
            filetypes = [
                ("EDAX files", "*.spd"),
                ("All Files", "*.*")
                ]
            )
        signal_type = 'EDS_SEM'
    elif file_type == '.emd':
        filepath = askopenfilename(
            filetypes = [
                ("EMD files", "*.emd"),
                ("All Files", "*.*")
                ]
            )
        signal_type = 'EDS_SEM'
    elif file_type == '.msa':
        filepath = askopenfilename(
            filetypes = [
                ("MSA files", "*.msa"),
                ("All Files", "*.*")
                ]
            )
        signal_type = 'EDS_SEM'
    elif file_type == '.h5':
        filepath = askopenfilename(
            filetypes = [
                ("USID files", "*.h5"),
                ("All Files", "*.*")
                ]
            )
        signal_type = 'EDS_SEM'
    if not filepath:
        return
    
    #clear display of previous data and reset buttons
    def reset_display():
        txt_output.configure(state='normal')
        #clear text
        txt_output.delete(1.0, 'end')
        txt_output.configure(state='disabled')
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        global displayingModel, displayingAnalysis, displayingMaps
        global displayingOverlay, btn_lines, btn_model, btn_analysis, btn_map
        global btn_overlay, ent_weight
        btn_lines.configure(state='disabled')
        btn_model.configure(state='disabled')
        btn_analysis.configure(state='disabled')
        btn_map.configure(state='disabled')
        btn_overlay.configure(state='disabled')
        ent_weight.configure(state='disabled')
        displayingModel = False
        displayingAnalysis = False
        displayingMaps = False
        displayingOverlay = False
        
        #reset elements
        for ele in elements:
            ele.reset_variables()
        
    reset_display()
    
    #set global signal type
    global signal
    signal = signal_type
    filepath_type = file_type.partition('.')[2]

    #make s a global variable for future use
    global s
    if file_type != '.emd':
        s = hs.load(filepath, signal_type)   
    else:
        s = hs.load(filepath, signal_type, lazy=True)   

    
    #get the beam energy of the signal
    if filepath_type != 'emd':
        global be
        if signal == 'EDS_TEM':
            be = s.metadata.Acquisition_instrument.TEM.beam_energy
        else:
            be = s.metadata.Acquisition_instrument.SEM.beam_energy

    #if wrong path was hit
    if filepath_type == 'spc':
        signal = 'EDS_TEM'
        s.set_signal_type('EDS_TEM')
    
    
    #enable element buttons
    for ele in elements:
        ele.reset_buttons()
         
    
    #enable element buttons
    if filepath_type != 'emd':
        for ele in elements:
            if ele.name in s.metadata.Sample.elements:
                ele.change_button_color()      
            
    if signal == 'EDS_TEM':
        s.add_lines()
        
        #enable xray lines
        for ele in elements:
            for line in ele.lines:
                if line.full_name in s.metadata.Sample.xray_lines:
                    line.bool.set(True)
        
        s.plot(True)
        #create axes  
        global xAxis
        xAxis = []
        xlength = len(s.data)/be    
        print(xlength)
        
        for i in np.arange(0, xlength, 0.005):
            xAxis.append(round(i, 3))
        yAxis = s.data
        
        #plot the data
        plot_data(xAxis, yAxis, 'Raw', 0, 0)
            
        #enable model button
        global btn_lines, btn_model
        btn_lines.configure(state='normal')
        btn_model.configure(state='normal')

        
        matplotlib.use('tkagg')
        s.plot(True)
    elif signal == 'EDS_SEM': 
        #enable map button
        global btn_map
        btn_map.configure(state='normal')
        
        #see if image exists
        img_string = filepath.partition('.')[0] + '.' + 'bmp'
        img_inserted = False
        if exists(img_string):
            image = Image.open(img_string)
            photo = ImageTk.PhotoImage(image)
            label = tk.Label(scrollable_frame, image=photo)
            label.image = photo
            r=0
            #if more frames exist than just one
            for f in scrollable_frame.winfo_children():
                info = f.grid_info()
                if 'row' in info:
                    if info['row']==0:
                        r += 1
            label.grid(row=r, column=0, sticky='nesw')
            
            img_inserted = True
            
        # s.change_dtype('float64')
        # s.decomposition(True, algorithm='NMF', output_dimension=3)
        #factors = s.get_decomposition_factors()
        
        #choose plotting actions based on type of file
        if filepath_type == 'spd':
            s.add_lines()
            
            #enable xray lines
            for ele in elements:
                for line in ele.lines:
                    if line.full_name in s.metadata.Sample.xray_lines:
                        line.bool.set(True)
            
            #to show possible speed without plotting, start comment here
            
            if img_inserted:
                    
                frm_spd = tk.Frame(scrollable_frame, relief=tk.RAISED, bd = 2)
                #if they don't want the popup windows
                pixel_num = len(s.data) * len(s.data[0])
                
                #plot in plane
                #load figure text
                def output_wait():
                    txt_output.configure(state='normal')
                    txt_output.delete(1.0, 'end')
                    #display loading
                    text = ('Loading image... %s pixels left\n\nSome analysis can be done while loading figure' % pixel_num)
                    txt_output.insert('end', text)
                    txt_output.configure(state='disabled')
                output_wait()
                txt_output.update()
                
                image_array=[]
                for n in s.data:
                    line_array=[]
                    for m in n:
                        #intensity=sum(m)
                        line_array.append(sum(m))
                    image_array.append(line_array)
                    #load figure text
                    pixel_num = pixel_num - len(s.data[0])
                    def output_wait(pixels):
                        txt_output.configure(state='normal')
                        txt_output.delete(1.0, 'end')
                        #display loading
                        text = (
                            'Loading image... %s pixels left\n\nSome analysis can be done while loading figure' % pixels)
                        txt_output.insert('end', text)
                        txt_output.configure(state='disabled')
                    output_wait(pixel_num)
                    txt_output.update()
                plt_image = plt
                
                txt_output.configure(state='normal')
                txt_output.delete(1.0, 'end')
                txt_output.configure(state='disabled')
                
                fig = plt_image.figure(figsize=(8, 5))
                plt_image.imshow(image_array, cmap='gray')
                plt_image.title('Spectrum Image')
                plt_image.xlabel('x axis')
                plt_image.ylabel('y axis')
                plt_image.colorbar()
                                
                can = FigureCanvasTkAgg(fig, master=frm_spd)
                can.draw()
                r=0
                for f in scrollable_frame.winfo_children():
                    info = f.grid_info()
                    if 'row' in info:
                        if info['column']==0:
                            r += 1
                #bind ability to draw on canvas
                #can.get_tk_widget().bind('<B1-Motion>', paint)

                can.get_tk_widget().bind('<Button-1>', start_point)
                can.get_tk_widget().bind('<ButtonRelease-1>', end_point)
                can.get_tk_widget().bind('<Button-3>', clear_shape)
                can.get_tk_widget().grid(row=0, column=0, sticky='nesw')
                
                #create a toolbar for the canvas
                can_tool = NavigationToolbar2Tk(can, frm_spd, pack_toolbar=False)
                can_tool.update()
                can_tool.grid(row=1, column=0, sticky='new')
                
                frm_spd.grid(row=r, column=0, sticky='nesw')
                
                ent_weight.configure(state='normal')

            
            # to show possible speed without plotting, end comment here
            
            
            """
            #if they're okay with the popup windows
            matplotlib.use('tkAgg')
            s.plot()
            """
        elif filepath_type == 'emd':
            #TODO: finish manipulating data
            for i in s:
                print(i.metadata)
                #i.add_lines()
                
                #enable xray lines
                for ele in elements:
                    for line in ele.lines:
                        if line.full_name in i.metadata.Sample.xray_lines:
                            line.bool.set(True)
                
                #to show possible speed without plotting, start comment here
                
                if img_inserted:
                        
                    frm_spd = tk.Frame(scrollable_frame, relief=tk.RAISED, bd = 2)
                    #if they don't want the popup windows
                    pixel_num = len(s.data) * len(s.data[0])
                    
                    #plot in plane
                    #load figure text
                    def output_wait():
                        txt_output.configure(state='normal')
                        txt_output.delete(1.0, 'end')
                        #display loading
                        text = ('Loading image... %s pixels left\n\nSome analysis can be done while loading figure' % pixel_num)
                        txt_output.insert('end', text)
                        txt_output.configure(state='disabled')
                    output_wait()
                    txt_output.update()
                    
                    image_array=[]
                    for n in i.data:
                        line_array=[]
                        for m in n:
                            #intensity=sum(m)
                            line_array.append(sum(m))
                        image_array.append(line_array)
                        #load figure text
                        pixel_num = pixel_num - len(s.data[0])
                        def output_wait(pixels):
                            txt_output.configure(state='normal')
                            txt_output.delete(1.0, 'end')
                            #display loading
                            text = (
                                'Loading image... %s pixels left\n\nSome analysis can be done while loading figure' % pixels)
                            txt_output.insert('end', text)
                            txt_output.configure(state='disabled')
                        output_wait(pixel_num)
                        txt_output.update()
                    plt_image = plt
                    
                    txt_output.configure(state='normal')
                    txt_output.delete(1.0, 'end')
                    txt_output.configure(state='disabled')
                    
                    fig = plt_image.figure(figsize=(8, 5))
                    plt_image.imshow(image_array, cmap='gray')
                    plt_image.title('Spectrum Image')
                    plt_image.xlabel('x axis')
                    plt_image.ylabel('y axis')
                    plt_image.colorbar()
                                    
                    can = FigureCanvasTkAgg(fig, master=frm_spd)
                    can.draw()
                    r=0
                    for f in scrollable_frame.winfo_children():
                        info = f.grid_info()
                        if 'row' in info:
                            if info['column']==0:
                                r += 1
                    #bind ability to draw on canvas
                    #can.get_tk_widget().bind('<B1-Motion>', paint)

                    can.get_tk_widget().bind('<Button-1>', start_point)
                    can.get_tk_widget().bind('<ButtonRelease-1>', end_point)
                    can.get_tk_widget().bind('<Button-3>', clear_shape)
                    can.get_tk_widget().grid(row=0, column=0, sticky='nesw')
                    
                    #create a toolbar for the canvas
                    can_tool = NavigationToolbar2Tk(can, frm_spd, pack_toolbar=False)
                    can_tool.update()
                    can_tool.grid(row=1, column=0, sticky='new')
                    
                    frm_spd.grid(row=r, column=0, sticky='nesw')
                    
                    ent_weight.configure(state='normal')
            return
            
        elif filepath_type == 'msa':
            return
        elif filepath_type == 'h5':
            return
        
    #remove O and add Cu??? Possibly? Ask on Thursday?
    
    #change the gloabl variable to reflect the data is shown
    global displayingData
    displayingData = True
            
    return

# #open file
# def open_file(file_type):   
#     global txt_output
    
#     matplotlib.use('nbagg')
#     #open file
#     filepath = ''
#     signal_type = ''

#     if file_type == '.spc':
#         filepath = askopenfilename(
#             filetypes = [
#                 ("EDAX files", "*.spc"),
#                 ("All Files", "*.*")
#                 ]
#             )
#         signal_type = 'EDS_TEM'
#     elif file_type == '.spd':
#         filepath = askopenfilename(
#             filetypes = [
#                 ("EDAX files", "*.spd"),
#                 ("All Files", "*.*")
#                 ]
#             )
#         signal_type = 'EDS_SEM'
#     elif file_type == '.emd':
#         filepath = askopenfilename(
#             filetypes = [
#                 ("EMD files", "*.emd"),
#                 ("All Files", "*.*")
#                 ]
#             )
#         signal_type = 'EDS_SEM'
#     elif file_type == '.msa':
#         filepath = askopenfilename(
#             filetypes = [
#                 ("MSA files", "*.msa"),
#                 ("All Files", "*.*")
#                 ]
#             )
#         signal_type = 'EDS_TEM'
#     elif file_type == '.h5':
#         filepath = askopenfilename(
#             filetypes = [
#                 ("USID files", "*.h5"),
#                 ("All Files", "*.*")
#                 ]
#             )
#         signal_type = 'EDS_SEM'
#     if not filepath:
#         return
    
#     #clear display of previous data and reset buttons
#     def reset_display():
#         txt_output.configure(state='normal')
#         #clear text
#         txt_output.delete(1.0, 'end')
#         txt_output.configure(state='disabled')
#         for widget in scrollable_frame.winfo_children():
#             widget.destroy()
#         global displayingModel, displayingAnalysis, displayingMaps
#         global displayingOverlay, btn_lines, btn_model, btn_analysis, btn_map
#         global btn_overlay, ent_weight
#         btn_lines.configure(state='disabled')
#         btn_model.configure(state='disabled')
#         btn_analysis.configure(state='disabled')
#         btn_map.configure(state='disabled')
#         btn_overlay.configure(state='disabled')
#         ent_weight.configure(state='disabled')
#         displayingModel = False
#         displayingAnalysis = False
#         displayingMaps = False
#         displayingOverlay = False
        
#         #reset elements
#         for ele in elements:
#             ele.reset_variables()
        
#     reset_display()
    
#     #set global signal type
#     global signal
#     signal = signal_type
#     filepath_type = file_type.partition('.')[2]

#     #make s a global variable for future use
#     global s
#     if file_type != '.emd':
#         s = hs.load(filepath, signal_type)   
#     else:
#         s = hs.load(filepath, signal_type, lazy=True)   

    
#     #get the beam energy of the signal
#     if filepath_type != 'emd':
#         global be
#         if signal == 'EDS_TEM':
#             be = s.metadata.Acquisition_instrument.TEM.beam_energy
#         else:
#             be = s.metadata.Acquisition_instrument.SEM.beam_energy

#     #if wrong path was hit
#     if filepath_type == 'spc':
#         signal = 'EDS_TEM'
#         s.set_signal_type('EDS_TEM')
    
    
#     #enable element buttons
#     for ele in elements:
#         ele.reset_buttons()
         
    
#     #enable element buttons
#     if filepath_type != 'emd' and filepath_type != 'msa':
#         for ele in elements:
#             if ele.name in s.metadata.Sample.elements:
#                 ele.change_button_color()      
            
#     if signal == 'EDS_TEM':
#         if filepath_type == 'spc':
#             s.add_lines()
            
#             #enable xray lines
#             for ele in elements:
#                 for line in ele.lines:
#                     if line.full_name in s.metadata.Sample.xray_lines:
#                         line.bool.set(True)
            
#             s.plot(True)
#             #create axes  
#             global xAxis
#             xAxis = []
#             xlength = len(s.data)/be    
#             print(xlength)
            
#             for i in np.arange(0, xlength, 0.005):
#                 xAxis.append(round(i, 3))
#             yAxis = s.data
            
#             #plot the data
#             plot_data(xAxis, yAxis, 'Raw', 0, 0)
                
#             #enable model button
#             global btn_lines, btn_model
#             btn_lines.configure(state='normal')
#             btn_model.configure(state='normal')
    
            
#             matplotlib.use('tkagg')
#             s.plot(True)
        
#         elif filepath_type == 'msa':
            
#             print(s.metadata)
            
#             xAxis = []
#             xlength = len(s.data)/ (be*10)  
#             print(xlength)
            
#             for i in np.arange(0, xlength, 0.005):
#                 xAxis.append(round(i, 3))
#             yAxis = s.data
            
#             #plot the data
#             plot_data(xAxis, s.data, 'Raw', 0, 0)
            
#     elif signal == 'EDS_SEM':
#         if filepath_type == 'spc':
#             #enable map button
#             global btn_map
#             btn_map.configure(state='normal')
            
#         #see if image exists
#         img_string = filepath.partition('.')[0] + '.' + 'bmp'
#         img_inserted = False
#         if exists(img_string):
#             image = Image.open(img_string)
#             photo = ImageTk.PhotoImage(image)
#             label = tk.Label(scrollable_frame, image=photo)
#             label.image = photo
#             r=0
#         #if more frames exist than just one
#         for f in scrollable_frame.winfo_children():
#             info = f.grid_info()
#             if 'row' in info:
#                 if info['row']==0:
#                     r += 1
#             label.grid(row=r, column=0, sticky='nesw')
    
#             img_inserted = True
            
#             # s.change_dtype('float64')
#             # s.decomposition(True, algorithm='NMF', output_dimension=3)
#             #factors = s.get_decomposition_factors()
#         if filepath_type == 'msa':
#             print(s.metadata)
            
#         #choose plotting actions based on type of file
#         elif filepath_type == 'spd':
#             s.add_lines()
            
#             #enable xray lines
#             for ele in elements:
#                 for line in ele.lines:
#                     if line.full_name in s.metadata.Sample.xray_lines:
#                         line.bool.set(True)
            
#             #to show possible speed without plotting, start comment here
            
#             if img_inserted:
                    
#                 frm_spd = tk.Frame(scrollable_frame, relief=tk.RAISED, bd = 2)
#                 #if they don't want the popup windows
#                 pixel_num = len(s.data) * len(s.data[0])
                
#                 #plot in plane
#                 #load figure text
#                 def output_wait():
#                     txt_output.configure(state='normal')
#                     txt_output.delete(1.0, 'end')
#                     #display loading
#                     text = ('Loading image... %s pixels left\n\nSome analysis can be done while loading figure' % pixel_num)
#                     txt_output.insert('end', text)
#                     txt_output.configure(state='disabled')
#                 output_wait()
#                 txt_output.update()
                
#                 image_array=[]
#                 for n in s.data:
#                     line_array=[]
#                     for m in n:
#                         #intensity=sum(m)
#                         line_array.append(sum(m))
#                     image_array.append(line_array)
#                     #load figure text
#                     pixel_num = pixel_num - len(s.data[0])
#                     def output_wait(pixels):
#                         txt_output.configure(state='normal')
#                         txt_output.delete(1.0, 'end')
#                         #display loading
#                         text = (
#                             'Loading image... %s pixels left\n\nSome analysis can be done while loading figure' % pixels)
#                         txt_output.insert('end', text)
#                         txt_output.configure(state='disabled')
#                     output_wait(pixel_num)
#                     txt_output.update()
#                 plt_image = plt
                
#                 txt_output.configure(state='normal')
#                 txt_output.delete(1.0, 'end')
#                 txt_output.configure(state='disabled')
                
#                 fig = plt_image.figure(figsize=(8, 5))
#                 plt_image.imshow(image_array, cmap='gray')
#                 plt_image.title('Spectrum Image')
#                 plt_image.xlabel('x axis')
#                 plt_image.ylabel('y axis')
#                 plt_image.colorbar()
                                
#                 can = FigureCanvasTkAgg(fig, master=frm_spd)
#                 can.draw()
#                 r=0
#                 for f in scrollable_frame.winfo_children():
#                     info = f.grid_info()
#                     if 'row' in info:
#                         if info['column']==0:
#                             r += 1
#                 #bind ability to draw on canvas
#                 #can.get_tk_widget().bind('<B1-Motion>', paint)

#                 can.get_tk_widget().bind('<Button-1>', start_point)
#                 can.get_tk_widget().bind('<ButtonRelease-1>', end_point)
#                 can.get_tk_widget().bind('<Button-3>', clear_shape)
#                 can.get_tk_widget().grid(row=0, column=0, sticky='nesw')
                
#                 #create a toolbar for the canvas
#                 can_tool = NavigationToolbar2Tk(can, frm_spd, pack_toolbar=False)
#                 can_tool.update()
#                 can_tool.grid(row=1, column=0, sticky='new')
                
#                 frm_spd.grid(row=r, column=0, sticky='nesw')
                
#                 ent_weight.configure(state='normal')

            
#             # to show possible speed without plotting, end comment here
            
            
#             """
#             #if they're okay with the popup windows
#             matplotlib.use('tkAgg')
#             s.plot()
#             """
#         elif filepath_type == 'emd':
#             #TODO: finish manipulating data
#             for i in s:
#                 print(i.metadata)
#                 #i.add_lines()
                
#                 #enable xray lines
#                 for ele in elements:
#                     for line in ele.lines:
#                         if line.full_name in i.metadata.Sample.xray_lines:
#                             line.bool.set(True)
                
#                 #to show possible speed without plotting, start comment here
                
#                 if img_inserted:
                        
#                     frm_spd = tk.Frame(scrollable_frame, relief=tk.RAISED, bd = 2)
#                     #if they don't want the popup windows
#                     pixel_num = len(s.data) * len(s.data[0])
                    
#                     #plot in plane
#                     #load figure text
#                     def output_wait():
#                         txt_output.configure(state='normal')
#                         txt_output.delete(1.0, 'end')
#                         #display loading
#                         text = ('Loading image... %s pixels left\n\nSome analysis can be done while loading figure' % pixel_num)
#                         txt_output.insert('end', text)
#                         txt_output.configure(state='disabled')
#                     output_wait()
#                     txt_output.update()
                    
#                     image_array=[]
#                     for n in i.data:
#                         line_array=[]
#                         for m in n:
#                             #intensity=sum(m)
#                             line_array.append(sum(m))
#                         image_array.append(line_array)
#                         #load figure text
#                         pixel_num = pixel_num - len(s.data[0])
#                         def output_wait(pixels):
#                             txt_output.configure(state='normal')
#                             txt_output.delete(1.0, 'end')
#                             #display loading
#                             text = (
#                                 'Loading image... %s pixels left\n\nSome analysis can be done while loading figure' % pixels)
#                             txt_output.insert('end', text)
#                             txt_output.configure(state='disabled')
#                         output_wait(pixel_num)
#                         txt_output.update()
#                     plt_image = plt
                    
#                     txt_output.configure(state='normal')
#                     txt_output.delete(1.0, 'end')
#                     txt_output.configure(state='disabled')
                    
#                     fig = plt_image.figure(figsize=(8, 5))
#                     plt_image.imshow(image_array, cmap='gray')
#                     plt_image.title('Spectrum Image')
#                     plt_image.xlabel('x axis')
#                     plt_image.ylabel('y axis')
#                     plt_image.colorbar()
                                    
#                     can = FigureCanvasTkAgg(fig, master=frm_spd)
#                     can.draw()
#                     r=0
#                     for f in scrollable_frame.winfo_children():
#                         info = f.grid_info()
#                         if 'row' in info:
#                             if info['column']==0:
#                                 r += 1
#                     #bind ability to draw on canvas
#                     #can.get_tk_widget().bind('<B1-Motion>', paint)

#                     can.get_tk_widget().bind('<Button-1>', start_point)
#                     can.get_tk_widget().bind('<ButtonRelease-1>', end_point)
#                     can.get_tk_widget().bind('<Button-3>', clear_shape)
#                     can.get_tk_widget().grid(row=0, column=0, sticky='nesw')
                    
#                     #create a toolbar for the canvas
#                     can_tool = NavigationToolbar2Tk(can, frm_spd, pack_toolbar=False)
#                     can_tool.update()
#                     can_tool.grid(row=1, column=0, sticky='new')
                    
#                     frm_spd.grid(row=r, column=0, sticky='nesw')
                    
#                     ent_weight.configure(state='normal')
#             return
            
#         elif filepath_type == 'h5':
#             return
        
#     #remove O and add Cu??? Possibly? Ask on Thursday?
    
#     #change the gloabl variable to reflect the data is shown
#     global displayingData
#     displayingData = True
            
#     return

#save file (DO MORE WITH THIS MAYBE???)
def save_file():
    """Save the current file as a new file."""
    filepath = asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    with open(filepath, mode="w", encoding="utf-8") as output_file:
        text = txt_output.get("1.0", tk.END)
        output_file.write(text)

#check element lines in pop-up window
def check_element_lines():
    global s, sTEM
    
    line_plot(True)
    
    return

#print the model
def show_model(): 
    matplotlib.use('nbagg')
    #do nothing if no data has been chosen
    if not displayingData:
        return
    
    global txt_output
    #load figure text
    def output_wait():
        txt_output.configure(state='normal')
        txt_output.delete(1.0, 'end')
        #display loading
        txt_output.insert('end', 'LOADING FIGURES...........')
        txt_output.configure(state='disabled')
    output_wait()
    txt_output.update()
    
    
    #destory old frame for the model
    global displayingModel
    
    global m, sModel
    m = s.create_model()
    m.fit_background()
    sModel = m.as_signal()
    yAxis = sModel.data
    
    plot_data(xAxis, yAxis, 'Model', 1, 0)
    #change the global variable corresponding to the model
    displayingModel = True
    
    #enable analysis button
    global btn_analysis
    btn_analysis.configure(state='normal')
    
    #clear loading bar
    txt_output.configure(state='normal')
    txt_output.delete(1.0, 'end')
    txt_output.configure(state='disabled')
    return

#plot the elemental figure
def elemental_plot(line, color, row):
    
    plt_image = plt
    
    fig = plt_image.figure(figsize=(8, 5))
    im = s.get_lines_intensity([line])
    plt_image.imshow(im[0].data, cmap=color)
    plt_image.title(line)
    plt_image.xlabel('x axis')
    plt_image.ylabel('y axis')
    plt_image.colorbar()
    
    can = FigureCanvasTkAgg(fig, master=scrollable_frame)
    can.draw()
    can.get_tk_widget().grid(row=row, column=1, sticky='nesw')
    
    #make menu
    can.get_tk_widget().bind("<Button-3>", right_click_color)
    
    return

#change color of maps
def change_color():
    matplotlib.use('nbagg')
    
    #delete all of the widgets in c1
    for widget in scrollable_frame.winfo_children():
        info = widget.grid_info()
        if 'column' in info:
            if info['column'] == 1 or info['column'] == 2:
                widget.destroy()
                
    #for all possible x-ray lines
    r = 0
    for line in s.metadata.Sample.xray_lines:
        for ele in elements:
            for l in ele.lines:
                if line == l.full_name:
                    #plot the figure with the new color
                    elemental_plot(line, l.color.get(), r)
        r += 1
        
    #make overlay if need be
    global displayingOverlay
    if displayingOverlay:
        plot_overlay()
    return

#right click color function
def right_click_color(event):
    
    #get the element used
    row = 0
    info = event.widget.grid_info()
    if 'row' in info:
        row = info['row']
    
    #make manu
    m = tk.Menu(event.widget, tearoff=0)
    
    for ele in elements:
        for line in ele.lines:
            #get variable for color element
            if line.full_name == s.metadata.Sample.xray_lines[row]:
                for color in color_array:
                    m.add_radiobutton(label=color, variable=line.color, value=color, 
                                      command=change_color)

    m.tk_popup(event.x_root, event.y_root)
    return

#show maps for each element
def show_individual_maps():
    
    matplotlib.use('nbagg')

    #display map true
    global displayingMaps 
    displayingMaps = True
    
    for f in scrollable_frame.winfo_children():
        info = f.grid_info()
        if 'column' in info:
            if info['column']==1:
                f.destroy()
        
    #print all color maps
    r = 0
    
    for l in s.metadata.Sample.xray_lines:
        for ele in elements:
            for line in ele.lines:
                if line.full_name == l:
                    #plot the element
                    elemental_plot(l, line.color.get(), r)
                    r += 1
    
    #initialize button overlay
    global btn_overlay
    btn_overlay.configure(state='normal')  
    
    return

#making lines for elemental analysis
def start_line(event):
    global xl_start, yl_start
    xl_start, yl_start = event.x, event.y

    frm_event_cord = event.widget.grid_info()
    frm_toolbar_cord = (frm_event_cord['row']+1, frm_event_cord['column'])
    
    tool_w = event.widget
    for wid in event.widget.master.winfo_children():
        info = wid.grid_info()
        if info["row"] == frm_toolbar_cord[0]:
            if info["column"] == frm_toolbar_cord[1]:
                tool_w = wid
        
    cord_str = tool_w.message.get()
    split = cord_str.partition(' ')
    x_string = split[0]
    x_string = x_string.partition('=')[2]
    split = split[2].partition('\n')
    y_string = split[0]
    y_string = y_string.partition('=')[2]
    
    global xl0, yl0
    xl0 = float(x_string)
    yl0 = float(y_string)
    return

line_made = False


def end_line(event):
    global xl_end, yl_end, line_made, line, ent_weight
    xl_end, yl_end = event.x, event.y
    
    frm_event_cord = event.widget.grid_info()
    frm_toolbar_cord = (frm_event_cord['row']+1, frm_event_cord['column'])
    
    tool_w = event.widget
    for wid in event.widget.master.winfo_children():
        info = wid.grid_info()
        if info["row"] == frm_toolbar_cord[0]:
            if info["column"] == frm_toolbar_cord[1]:
                tool_w = wid
                
    # print(tool_w.zoom().get())
            
    cord_str = tool_w.message.get()
    split = cord_str.partition(' ')
    x_string = split[0]
    x_string = x_string.partition('=')[2]
    split = split[2].partition('\n')
    y_string = split[0]
    y_string = y_string.partition('=')[2]
    
    global xl1, yl1
    xl1 = float(x_string)
    yl1 = float(y_string)
    
    #if shape has been made, delete it
    if line_made:
        event.widget.delete(line)
        
    width = 1
    width_string = ent_weight.get()
    if (width_string.isnumeric()):
        width = int(width_string)
        if width == 0:
            width = 1
            ent_weight.delete(0, tk.END)
            ent_weight.insert(0, '1')
     
    line = event.widget.create_line(xl_start, yl_start, xl_end, yl_end, 
                                     fill='black', width=width)
    line_profile_analysis(width)
    
    line_made = True
    
    # line_profile = hs.roi.Line2DROI(400, 250, 220, 600)
    # line0 = line_profile.interactive(im0)
    # # Plotting the profile on the same figure
    # hs.plot.plot_spectra([line0, line1])
    

    return

#plot the line profile
def plot_profile(data, r, c, frame):
    
    matplotlib.use('nbagg')
    
    #make new frame for raw data
    frm = tk.Frame(frame, relief=tk.RAISED, bd=2)
    frm.rowconfigure(0, weight=1)
    frm.columnconfigure(0, weight=1)
    frm.grid(row=r, column=c, sticky='nsew')
    
    #make a variable for the new plt
    pl = plt
    
    #create figure to display
    fig = pl.figure(figsize=(8,4))
    
    for key, value in data.items():
        xaxis = []
        xlength = len(value)
        for i in np.arange(0, xlength):
            xaxis.append(round(i, 3))
        color = 'r'
        for ele in elements:
            for line in ele.lines:
                if line.full_name == key:
                    color = line.color.get()[:-1].lower()
        pl.plot(xaxis, value, label=key, color=color)
    
    pl.title('Overlay data')
    pl.ylabel('Intensity')
    pl.legend()
        
    #create a canvas to display
    cnv = FigureCanvasTkAgg(fig, master=frm)
    cnv.draw()
    cnv.get_tk_widget().grid(row=0, column=0, sticky='nsew')
    
    #create a toolbar for the canvas
    tl = NavigationToolbar2Tk(cnv, frm, 
                                      pack_toolbar=False)
    tl.update()
    tl.grid(row=1, column=0, sticky='ew')
    
    return

def line_profile_analysis(width):
    global xl0, xl1, yl0, yl1, be, s
    xl0 = round(xl0)
    xl1 = round(xl1)
    yl0 = round(yl0)
    yl1 = round(yl1)
    
    #if not a straigt line down
    if xl1 != xl0:
        slope = (yl1-yl0)/(xl1-xl0)
        b = round(slope * (-xl0) + yl0)

        #iterate over all pixels
        yaxis = {}
        #for all elements
        for ele in elements:
            for line in ele.lines:
                
                #if the line is in the map
                if line.map.get():
                    
                    #add line to dictionary
                    if line.full_name not in yaxis:
                        yaxis[line.full_name] = []
                    intensity = s.get_lines_intensity([line.full_name])
                    
                    #iterate over x and y
                    for y in range(len(s.data)):
                        for x in range(len(s.data[y])):
                            
                            #if the point lies on the line based on b
                            poss_b = round(y-(slope*x))
                            if poss_b >= b-1 and poss_b <= b+1:
                                
                                #if the x and y cords fall within range
                                if y >= min(yl0, yl1) and y <= max(yl0, yl1):
                                    if x>= min(xl0, xl1) and x <= max(xl0, xl1):
                                        
                                        p = intensity[0].data[y][x]
                                        
                                        #account for all points along the line width
                                        perp_slope = -1 * (1.0 / slope)
                                        perp_b  = y - (perp_slope * x)
                                        
                                        #check all points on perpendicular line
                                        for yy in range(len(s.data)):
                                            for xx in range(len(s.data[yy])):
                                                
                                                if yy !=y and xx != x:
                                                
                                                    #if the point lies on the slope
                                                    poss_perp_b = round(yy - (perp_slope * xx))
                                                    if poss_perp_b >= perp_b - 1 and poss_perp_b <= perp_b + 1:
                                                        
                                                        distance = math.sqrt((xx-x)**2 +(yy-y)**2)
                                                        if distance <= width:
                                                            p += intensity[0].data[yy][xx]
                                        
                                        #add to the axis
                                        array = yaxis[line.full_name]
                                        array.append(p)
                                        yaxis.update({line.full_name: array})
        
        plot_profile(yaxis, 1, 2, scrollable_frame)

    else:      
        min_point = min(yl0, yl1)
        max_point = max(yl0, yl1)
        
        yaxis = {}
        #for all elements
        for ele in elements:
            for line in ele.lines:
                
                #if the line is on the map
                if line.map.get():
                    
                    #add line to dictionary
                    if line.full_name not in yaxis:
                        yaxis[line.full_name] = []
                    intensity = s.get_lines_intensity([line.full_name])
                    
                    #iterate over points
                    
                    y = min_point
                    while y < max_point:
                        
                        p = intensity[0].data[y][xl0]
                        
                        for x in range(xl0-width, xl0+width):
                            if x != xl0:
                                p += intensity[0].data[y][x]
                            
                        #add to the axis
                        array = yaxis[line.full_name]
                        array.append(p)
                        y += 1
                        yaxis.update({line.full_name: array})
        
        plot_profile(yaxis, 1, 2, scrollable_frame)
        
    return    

def clear_line(event):
    
    global line, line_made
    
    event.widget.delete(line)
    line_made=False
    
    #destroy the spectra below the overlay
    for widget in scrollable_frame.winfo_children():
        info = widget.grid_info()
        if 'row' in info and 'column' in info:
            if info['row'] == 1 and info['column'] == 2:
                widget.destroy()
                
    return

#plot the overlay without showing the popup
def plot_overlay():
    matplotlib.use('nbagg')
    
    #show image
    plt_image = plt
    
    fig = plt_image.figure(figsize=(8, 5))
    im = s.get_lines_intensity()

    # global overlay_elements
    # plt_image.imshow(im[0].data, cmap=color)
    plt_image.title('Overlay')
    plt_image.xlabel('x axis')
    plt_image.ylabel('y axis')
    
    #get number of elements in the overlay
    num_ones = 0
    for ele in elements:
        for line in ele.lines:
            #if in map
            if line.map.get():
                num_ones += 1
                
    #if zero, remove plot
    if num_ones == 0:
        for f in scrollable_frame.winfo_children():
            info = f.grid_info()
            if 'column' in info:
                if info['column']==2:
                    f.destroy()
    else:
        frm_overlay = tk.Frame(scrollable_frame, relief=tk.RAISED, bd = 2)

        #make alpha
        decrement = 1.0/num_ones
        a = 0
        legend_array = []
        for ele in elements:
            for line in ele.lines:
                #if line is in map
                if line.map.get():
                    color = line.color.get()
                    alpha = 1.0 - (a * decrement)
                    
                    index = 0
                    #get element being displayed
                    for x in range(len(im)):
                        if im[x].metadata.Sample.xray_lines[0] == line.full_name:
                            index = x
                    
                    plt_image.imshow(im[index].data, cmap=color, alpha=alpha)

                    #legend
                    color_string = color.lower()
                    color_string = color_string[:-1]
                    label = line.full_name
                    
                    patch = mpatches.Patch(color=color_string, 
                                           label=label)
                    legend_array.append(patch)
                    
                    a += 1
                    
        #make legend
        plt.legend(handles=legend_array)
        
        #make canvas
        can = FigureCanvasTkAgg(fig, master=frm_overlay)
        can.draw()
        can.get_tk_widget().grid(row=0, column=0, sticky='nesw')
        
        can.get_tk_widget().bind('<Button-1>', start_line)
        can.get_tk_widget().bind('<ButtonRelease-1>', end_line)
        can.get_tk_widget().bind('<Button-3>', clear_line)
        
        #make toolbar
        tool = NavigationToolbar2Tk(can, frm_overlay, pack_toolbar=False)
        tool.update()
        tool.grid(row=1, column=0, sticky='new')
        
        frm_overlay.grid(row=0, column=2, sticky='nesw')

    return

#show overlay map with different colors
def show_overlay_map():
    matplotlib.use('nbagg')

    #set true for elemental display
    global displayingOverlay
    displayingOverlay = True
    
    #make pop-out window
    w_map = tk.Toplevel()
    w_map.title('Overlay Element Options')
    w_map.columnconfigure(0, weight=3)
    w_map.columnconfigure(1, weight=1)
    
    #make labels
    lbl_element = tk.Label(w_map, text = 'X-Ray Lines', padx = 18)
    #add label to window
    lbl_element.grid(row=0, column = 0, sticky='w')
    
    #make element for each graph
    i = 0    
    for ele in s.metadata.Sample.xray_lines:
        
        for e in elements:
            for line in e.lines:
                if ele == line.full_name:
                    cb = tk.Checkbutton(w_map, text=ele, variable=line.map, onvalue=True, offvalue=False, padx=30)
                    cb.grid(row=i+1, column=0, sticky='w')
        i += 1
    
    #quit overlay window and finish map
    def quit_overlay():
        #plot the figure
        plot_overlay()
        #destroy top window
        w_map.destroy()
        w_map.update()
        
        #destroy the spectra below the overlay
        for widget in scrollable_frame.winfo_children():
            info = widget.grid_info()
            if 'row' in info and 'column' in info:
                if info['row'] == 1 and info['column'] == 2:
                    widget.destroy()
        return
    
    btn_quit_overlay = tk.Button(w_map, text="Make Overlay", command=quit_overlay)
    btn_quit_overlay.grid(row=i+1, column=0, sticky='ew')
        
    return

#add to the shells used dictionary
def shells_used():
    
    global shell_dic, display
    
    for ele in elements:
        if ele.shell.get() == 1:
            shell_dic[ele.name] = [1, 0]
        if ele.shell.get() == 2:
            shell_dic[ele.name] = [0, 1]
    
    return

#run analysis and show models
def show_residual():
    matplotlib.use('nbagg')
    global s, sModel      
    #get data
    yAxis = []
    for i in range(0, len(xAxis)):
        yAxis.append(int(s.data[i]-sModel.data[i]))
          
    #plot_data(xAxis, yAxis, 'Residual', 2, 0)
    plot_data(xAxis, yAxis, 'Residual', 0, 1)
    return

#show chi-squared analysis
def show_chi_squared():
    matplotlib.use('nbagg')
    global s, sModel
    #get data
    yAxis = []
    for i in range(0, len(xAxis)):
        num = (int(s.data[i]-sModel.data[i]))
        yAxis.append(num**2/sModel.data[i])

    plot_data(xAxis, yAxis, 'Chi_Squared', 1, 1)
    return

#run analysis
def run_analysis():
    matplotlib.use('nbagg')
    global be
    #only run analiysis if the model has been analyzed
    if not displayingModel:
        return
    #clear the current shell
    global shell_dic
    shell_dic.clear()
    show_residual()
    show_chi_squared()
    def k_factor_analysis():
        ''' Consider changing location of peaks function'''
        #get peak values of all elements
        def get_peaks(array):
            #get intensities
            sI = m.get_lines_intensity()
            #iterate over sI to get peaks
            for x in sI:
                #get element
                ele = x.metadata.Sample.xray_lines[0]
                #get xCord
                str = x.metadata.General.title
                xCordStr = re.findall("\d+\.\d+", str)
                xCord = float(xCordStr[0])
                for y in m.active_components:
                    if ele == y.name:
                        xCord = y.centre.value

                xIndex = int(xCord * be)
                height = sModel.data[xIndex]
                #add to list
                array.append(tuple([ele, xCord, height]))
        peak= []
        get_peaks(peak)
        #allow users to choose the k or l shell for analysis
        def use_k_or_l():
            #get element
            global display
            display = {}
            sI = m.get_lines_intensity()
            #add the elements that need displayed to an array
            for x in sI:
                ele = x.metadata.Sample.elements[0]
                display[ele] = [0, 0]
            #see if the element has a Ka and/or La to display
            for x in sI:
                split = x.metadata.Sample.xray_lines[0].partition('_')
                #gets the array from the display based on the element
                mini = display[split[0]]
                #using a binary system to determine [Ka, La]
                if split[2] == 'Ka':
                    mini[0] = 1
                elif split[2] == 'La':
                    mini[1] = 1
                display[split[0]] = mini
            #create window for shell options
            def shell_choices(display):
                
                w_choices = tk.Toplevel()
                w_choices.title('Shell Analysis Options')
                w_choices.columnconfigure(0, weight=3)
                w_choices.columnconfigure(1, weight=1)
                w_choices.columnconfigure(2, weight=1)
                
                #make labels
                lbl_element = tk.Label(w_choices, text = 'Element')
                lbl_K = tk.Label(w_choices, text = 'K ')
                lbl_L = tk.Label(w_choices, text = 'L ')
                
                #add label to window
                lbl_element.grid(row=0, column = 0, sticky='nesw')
                lbl_K.grid(row=0, column=1, sticky='nesw')
                lbl_L.grid(row=0, column=2, sticky='nesw')

                i = 1
                for ele in elements:
                    if ele.name in display:
                        
                        lbl_element_name = tk.Label(w_choices, text = ele.name)
                        lbl_element_name.grid(row = i, column = 0, sticky='nesw')
                        
                        #if the option for the K-shell exists
                        if display[ele.name][0] == 1:
                            bu = tk.Radiobutton(w_choices, variable=ele.shell, value=1, command=shells_used)
                            bu.grid(row=i, column=1, sticky='nesw')
                       
                        #if the option for the L-shell exists
                        if display[ele.name][1] == 1:
                            bu = tk.Radiobutton(w_choices, variable=ele.shell, value=2, command=shells_used)
                            bu.grid(row=i, column=2, sticky='nesw')
                        
                        #if the option for no K-shell
                        if display[ele.name][0] == 0 and display[ele.name][1] == 1:
                            bu = tk.Radiobutton(w_choices, variable=ele.shell, value=0, state='disabled', command=shells_used)
                            bu.grid(row=i, column=1, sticky='nesw')
                        i += 1
                
                #add button to finish computations
                def quit_window():
                    #finish computations
                    def analysis_continued():
                        #get k factors of each element
                        kFactorsEle = []
                        def get_k_factors(array):
                            for key in shell_dic:
                                #if K shell being used, check kAll
                                if shell_dic[key][0] == 1:
                                    for k in k_shells:
                                        if key == k[0]:
                                            array.append(tuple([key, 'K', 
                                                                k[1]]))
                                #if L shell being used, check kAll
                                elif shell_dic[key][1] == 1:
                                    for l in l_shells:
                                        if key == l[0]:
                                            array.append(tuple([key, 'L', 
                                                                l[1]]))
                        get_k_factors(kFactorsEle)
                        #get intensities
                        intense = []
                        def get_intensities(array):
                            for ele in kFactorsEle:
                                for i in sI:
                                    #add intensities
                                    name = ele[0] + '_' + ele[1] + 'a'
                                    if name == i.metadata.Sample.xray_lines[0]:
                                        array.append(i)
                        get_intensities(intense)
                        #isolate k-factors
                        kfactors = []
                        def isolate_k_factors(array):
                            for k in kFactorsEle:
                                kfactors.append(k[2])
                        isolate_k_factors(kfactors)
                        
                        #finalized data array, organizing k, atomic%, weight%, 
                        #net intensity, and error (in order)
                        global final_data
                        final_data = []
                        for ele in kFactorsEle:
                            final_data.append(
                                tuple([ele[0], ele[1], [ele[2]]]))
                        #perform k-factor quantification
                        if len(intense) == 0:
                            return
                        cu = 'atomic'
                        composition = s.quantification(
                            method="CL", intensities=intense, factors=kfactors, 
                            composition_units=cu)
                            
                        #add the atomic percents to the final data
                        for i in range(len(composition)):
                            final_data[i][2].append(composition[i].data[0])
                        #add the weight percents to the final data
                        def weight_percents():
                            weight = []
                            atomic_percents = []
                            #create array of atomic percents
                            for i in range(len(composition)):
                                atomic_percents.append(composition[i].data[0])
                            element_percents = []
                            for i in range(len(composition)):
                                element_percents.append(final_data[i][0])
                            weight = hs.material.atomic_to_weight(
                                atomic_percents, element_percents)
                            for i in range(len(weight)):
                                final_data[i][2].append(weight[i])
                        weight_percents()
                        
                        #add intensities to the final data
                        for i in range(len(final_data)):
                            for j in range(len(sI)):
                                eleShell = final_data[i][0] + '_' + final_data[i][1] + 'a'
                                eS = sI[j].metadata.Sample.xray_lines[0]
                                if eleShell == eS:
                                    final_data[i][2].append(sI[j].data[0])
                                    
                        def get_sigma():
                            #add net errors percents/sigma
                            for i in peak:
                                eV = i[1]
                                peakHeight = 0
                                peakIndex = 0
                                falseAlarms = 0
                                index = int(eV*be)
                                while peakHeight==0 and falseAlarms < 10:
                                    #if larger than left
                                    if s.data[index] > s.data[index-1]:
                                        #if larger than right
                                        if s.data[index] > s.data[index + 1]:
                                            #check if actually peak
                                            if (s.data[index] > s.data[index-2] and s.data[index] > s.data[index + 2]):
                                                peakHeight = s.data[index]
                                                peakIndex = index/float(be)
                                            #else not actually the peak
                                            else:
                                                falseAlarms += 1
                                                if s.data[index-2] > s.data[index+2]:
                                                    index -= 2
                                                else:
                                                    index += 2
                                        #if right is larger
                                        else:
                                            index += 1
                                    #if left is larger
                                    else:
                                        index -= 1
                                #if loop times out
                                #CONSIDER DEVELOPING METHOD FOR HIDDEN PEAKS
                                if peakHeight==0:
                                    peakHeight = s.data[index]
                                    peakIndex=index/float(be)
                                #get the difference of the eV
                                difference = abs(peakIndex - eV)
                                #divide by sigma
                                sig = 0
                                global m
                                for x in m.active_components:
                                    if i[0] == x.name:
                                        sig = difference/x.sigma.value
                                #add to final data
                                for j in range(len(final_data)):
                                    eleShell = final_data[j][0] + '_' + final_data[j][1] + 'a'
                                    if i[0] == eleShell:
                                        final_data[j][2].append(sig)
                        get_sigma()
                    analysis_continued()
                    
                    #place analysis text in window
                    def insert_text():
                        global txt_output
                        txt_output.configure(state='normal')
                        #clear text
                        txt_output.delete(1.0, 'end')
                        
                        #insert new text
                        txt_output.insert(
                            'end', 'Project: %s\n' %(
                                s.metadata.General.original_filename))
                        txt_output.insert(
                            'end', 'kV: %d\n'%(
                                s.metadata.Acquisition_instrument.TEM.beam_energy))
                        txt_output.insert(
                            'end', 'Live Time: {:.4f}\n'.format(
                                s.metadata.Acquisition_instrument.TEM.Detector.EDS.live_time))
                        txt_output.insert(
                            'end', 'Takeoff Angle: {:.1f}\n'.format(
                                s.metadata.Acquisition_instrument.TEM.Detector.EDS.elevation_angle))
                        txt_output.insert(
                            'end', 'Resolution: {:.4f}\n\n'.format(
                                s.metadata.Acquisition_instrument.TEM.Detector.EDS.energy_resolution_MnKa))
                        
                        #insert element header
                        txt_output.insert(
                            'end', 'Element\t\tWeight %\t\tAtomic %\t\tK-Factor\t\tNet Intensity\t\tSigma\n')

                        #insert all elements
                        
                        for ele in final_data:
                            txt_output.insert(
                                'end', '{} {} \t\t{:.2f}\t\t{:.2f}\t\t{:.2f}\t\t{:.2f}\t\t{:.2f}\n'.format(
                                    ele[0], ele[1], ele[2][2], ele[2][1],
                                    ele[2][0], ele[2][3], ele[2][4]))

                        txt_output.configure(state='disabled')
                    insert_text()
                    
                    #destroy top window
                    w_choices.destroy()
                    w_choices.update()
                    return
                btn_quit = tk.Button(w_choices, text="Finish Quantification",
                                     command=quit_window)
                btn_quit.grid(row=i, column=0, sticky='ew')
                
                #configure rows
                for x in range(i):
                    w_choices.rowconfigure(x, weight=1)
            shell_choices(display)
            display.clear()
        use_k_or_l()
    k_factor_analysis()
    #change gloabal analysis variable
    global displayingAnalysis
    displayingAnalysis = True
    
#create new window
w = tk.Tk()
width= w.winfo_screenwidth()
height= w.winfo_screenheight()
w.geometry("%dx%d" % (width, height))

#create all frames
frm_main = tk.Frame(w, relief=tk.RAISED, bd=2)

# frm_lb = tk.Frame(frm_main, relief=tk.RAISED, bd=2)
# can_lb = tk.Canvas(frm_lb, relief=tk.RAISED, bd=2)
# yscroll = tk.Scrollbar(frm_lb, orient='vertical', command=can_lb.yview)
# frm_left_bar = tk.Frame(can_lb, relief=tk.RAISED, bd=2)
frm_left_bar = tk.Frame(frm_main, relief=tk.RAISED, bd=2)

frm_display = tk.Frame(frm_main, relief=tk.RAISED, bd=2)
canvas = tk.Canvas(frm_display, relief=tk.RAISED, bd=2)
scrolly = tk.Scrollbar(frm_display, orient='vertical', command=canvas.yview)
scrollx = tk.Scrollbar(frm_display, orient='horizontal', command=canvas.xview)
scrollable_frame = tk.Frame(canvas, relief=tk.RAISED, bd=2)
frm_bottom_bar = tk.Frame(w, relief=tk.RAISED, bd=2)
frm_element = tk.Frame(frm_bottom_bar, relief=tk.RAISED, bd=2)
frm_output = tk.Frame(frm_bottom_bar, relief=tk.RAISED, bd=2)

#format all frames
def format_frames():
    def form_window():
        w.title("THE(TM) HyperSpy Analysis")
        w.rowconfigure(0, minsize=20, weight=1)
        w.rowconfigure(1, minsize=5, weight=0)
        w.columnconfigure(0, minsize=5, weight=1)
    form_window()
    def form_top_bar():
        #frm_top_bar.rowconfigure(0, minsize=1, weight=1)
        return
    form_top_bar()
    def form_main():
        frm_main.rowconfigure(0, minsize=0, weight=1)
        frm_main.columnconfigure(0, weight=0)
        frm_main.columnconfigure(1, weight=1)
    form_main()
    def form_left_bar():
        frm_left_bar.columnconfigure(0, weight=0)
        # frm_lb.rowconfigure(0, weight=1)
        # frm_lb.columnconfigure(0, weight=1)
        # frm_lb.columnconfigure(1, weight=0)
        #can_lb.columnconfigure(0, weight=1)
        #frm_left_bar.columnconfigure(0, weight=0)
    form_left_bar()
    def form_element():
        for i in range(0, 18):
            frm_element.columnconfigure(i, minsize=26, weight=0)
        for i in range(0, 9):
            frm_element.rowconfigure(i, minsize=26, weight=0)
    form_element()
    def form_output():
        frm_output.rowconfigure(0, weight=1)
        frm_output.columnconfigure(0, weight=1)
    form_output()
    def form_bottom_bar():
        frm_bottom_bar.rowconfigure(0, weight=1)
        frm_bottom_bar.columnconfigure(0, weight=0)
        frm_bottom_bar.columnconfigure(1, weight=1)
    form_bottom_bar()
    def form_canvas():
        scrollable_frame.rowconfigure(0, weight=1)
        scrollable_frame.rowconfigure(1, weight=1)
        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)
    # form_canvas()
    def form_display():
        frm_display.rowconfigure(0, weight=1)
        frm_display.columnconfigure(0, weight=1)
        frm_display.columnconfigure(1, weight=0)
        
    form_display()
format_frames()

# #make scrollable frame for left bar
# frm_lb.bind(
#     "<Configure>",
#     lambda e: can_lb.configure(
#         scrollregion=can_lb.bbox("all")
#         )
#     )        
# can_lb.create_window((0, 0), window=frm_left_bar, anchor="nw")
# can_lb.configure(yscrollcommand=yscroll.set)
# def on_mousewheel(event):
#     scroll_num = int(-1*(event.delta/120))
#     can_lb.yview_scroll(scroll_num, 'units')
#     return
# can_lb.bind_all('<MouseWheel>', on_mousewheel)

# can_lb.grid(row=0, column=0, sticky='ns')
# yscroll.grid(row=0, column=1, sticky='ns')

#add widgets to all frames
def add_to_frames():
    def add_to_top_bar():
        menu_bar =  tk.Menu(w)
        #open button
        open_menu = tk.Menu(menu_bar, tearoff=0)
        open_menu.add_command(label='.spc', command=lambda: open_file('.spc'))
        open_menu.add_command(label='.spd', command=lambda: open_file('.spd'))
        open_menu.add_command(label='.emd', command=lambda: open_file('.emd'))
        open_menu.add_command(label='.msa', command=lambda: open_file('.msa'))
        open_menu.add_command(label='.h5', command=lambda: open_file('.h5'))

        #open_menu.add_separator()
        #open_menu.add_command(label='Exit')
        menu_bar.add_cascade(label='Open', menu=open_menu)
        
        #save button
        save_menu = tk.Menu(menu_bar, tearoff=0)
        save_menu.add_command(label='Save Output', command=save_file)
        menu_bar.add_cascade(label='Save', menu=save_menu)
        w.config(menu=menu_bar)

    add_to_top_bar()
    def add_to_left_bar():
        #make buttons
        global btn_lines, btn_model, btn_analysis, btn_map, btn_overlay, can_lb
        global ent_weight, drop, clicked
        btn_lines = tk.Button(master=frm_left_bar, text='Check Element Lines', 
                              command = check_element_lines, state='disabled')
        btn_model = tk.Button(master=frm_left_bar, text="Display Model", 
                              command = show_model, state='disabled')
        lbl_weight = tk.Label(master=frm_left_bar, text='Line Weight:')
        ent_weight = tk.Entry(master=frm_left_bar, state = 'disabled')
        lbl_shape = tk.Label(master=frm_left_bar, text='Shape Type:')
        
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
        
        btn_analysis = tk.Button(master=frm_left_bar, text="Run Analysis", 
                                 command=run_analysis, state='disabled')
        btn_map = tk.Button(master=frm_left_bar, text="Element Maps", 
                            command=show_individual_maps, state='disabled')
        btn_overlay = tk.Button(master=frm_left_bar, text="Overlay Maps", 
                                command=show_overlay_map, state='disabled')
        
        #add to frame
        btn_lines.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        btn_model.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        btn_analysis.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        lbl_weight.grid(row=3, column=0, sticky='ew', padx=5, pady=0)
        ent_weight.grid(row=4, column=0, sticky='ew', padx=5, pady=5)
        lbl_shape.grid(row=5, column=0, sticky='ew', padx=5, pady=0)
        drop.grid(row=6, column=0, sticky='ew', padx=5, pady=5)
        btn_map.grid(row=7, column=0, sticky='ew', padx=5, pady=5)
        btn_overlay.grid(row=8, column=0, sticky='ew', padx=5, pady=5)
        
        #print(frm_left_bar.cget('width'))
        #can_lb.configure(width=frm_left_bar.cget('width'), height=frm_left_bar.cget('height'))

    add_to_left_bar()
    def add_to_output():
        global txt_output
        txt_output = tk.Text(frm_output, state='disabled', height=10, 
                             wrap=tk.NONE)
        txt_output.grid(sticky='nesw')
        #add scrollbars
        sby = tk.Scrollbar(frm_output)
        sby.grid(row=0, column=1, sticky='ns')
        txt_output.configure(yscrollcommand=sby.set)
        sby.configure(command=txt_output.yview)
        
        sbx = tk.Scrollbar(frm_output, orient=tk.HORIZONTAL)
        sbx.grid(row=1, column=0, sticky='ew')
        txt_output.configure(xscrollcommand=sbx.set)
        sbx.configure(command=txt_output.xview)
        return
    add_to_output()
    def add_to_display():
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
                )
            )        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrolly.set)
        canvas.configure(xscrollcommand=scrollx.set)
        def on_mousewheel(event):
            scroll_num = int(-1*(event.delta/120))
            canvas.yview_scroll(scroll_num, 'units')
            return
        canvas.bind_all('<MouseWheel>', on_mousewheel)
        
        canvas.grid(row=0, column=0, sticky='nesw')
        scrolly.grid(row=0, column=1, sticky='ns')
        scrollx.grid(row=1, column=0, sticky='ew')
        
        return
    add_to_display()
add_to_frames()

#add elements to element frame
buttonFont= font.Font(size=7)

elements = []
ci = 0
#iterate over array
for n in range(len(element_array)):
    for m in range(len(element_array[n])):
        if element_array[n][m] != '0':
            
            #get the color for the element
            color = color_array[ci]
            
            #make a name for the button
            element = Element(element_array[n][m], n, m, color, frm_element)
            elements.append(element)
            
            #increment color array properly
            ci += 1
            if ci == len(color_array):
                ci = 0

#pack the frames into the window
def pack_window():
    #pack into wimdow
    frm_main.grid(row=0, column=0, sticky='nesw')
    #frm_lb.grid(row=0, column=0, sticky='nes')
    frm_left_bar.grid(row=0, column=0, sticky='nes')
    frm_display.grid(row=0, column=1, sticky='nesw')
    frm_bottom_bar.grid(row=1, column=0, sticky='esw')
    frm_element.grid(row=0, column=0, sticky='sw')
    frm_output.grid(row=0, column=1, sticky='nesw')
pack_window()


#run application
w.mainloop()

""" 
TODO: 
    More comments
    Make README file
    
    With model manipulation, attempt background removal
        
    Print data with spectra for spds
        
    Consider trying get_lines_intensity on TEM data
    
    Consider adding loading screen for line profile
    
    Ask about how they'd prefer width(aka w or w/2)
    
    Consider re-doing EVERYTHING
    
    Make sure be accounts for units
"""