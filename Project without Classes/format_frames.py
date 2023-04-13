# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 09:17:25 2022

@author: Alyssa Blanc
"""

import tkinter as tk
import global_arrays as glb
from element_class import Element
from open_and_save import save_file as savef
import manipulate_text as mtxt

"""MAIN WINDOW"""
#main window
def format_window(w):
    """
    Format the main window

    Parameters
    ----------
    w : tk.Tk
        Main window.

    Returns
    -------
    None.

    """
    #make full screen
    w.state('zoomed')
    
    #title
    w.title('THE(TM) HyperSpy Analysis')
    
    #configure
    w.rowconfigure(0, minsize=20, weight=1)
    w.rowconfigure(1, minsize=5, weight=0)
    w.columnconfigure(0, minsize=5, weight=1)
    
    return

def add_menu(w, openf, txt):
    """
    Add menu to the top of the window

    Parameters
    ----------
    w : tk.Tk
        Main window.
    openf : function
        Function to open a file.
    txt : tk.Text
        Tkinter text box.

    Returns
    -------
    None.

    """
    
    menu = tk.Menu(w)
    
    #open button
    open_m = tk.Menu(menu, tearoff=0)
    
    #TODO: temporarily delete some options until they are avaliable
    #open_m.add_command(label='.emd', command=lambda: openf('.emd'))
    #open_m.add_command(label='.h5', command=lambda: openf('.h5'))
    #open_m.add_command(label='.msa', command=lambda: openf('.msa'))
    open_m.add_command(label='.spc', command=lambda: openf('.spc'))
    open_m.add_command(label='.spd', command=lambda: openf('.spd'))
    
    menu.add_cascade(label='Open', menu=open_m)
    
    #save button
    save_m = tk.Menu(menu, tearoff=0)
    
    save_m.add_command(label='Save Output', command=lambda: savef(txt))
    
    menu.add_cascade(label='Save', menu=save_m)
    
    w.config(menu=menu)
    
    return

"""FIRST LEVEL FRAMES"""
#main
def format_main(frm):
    """
    Format the main frame

    Parameters
    ----------
    frm : tk.Frame
        Main frame of the window.

    Returns
    -------
    None.

    """
    
    frm.rowconfigure(0, minsize=0, weight=1)
    frm.columnconfigure(0, weight=0)
    frm.columnconfigure(1, weight=1)
    
    frm.grid(row=0, column=0, sticky='nesw')
    
    return

#bottom bar
def format_bottom_bar(frm):
    """
    Format the botton bar of the window

    Parameters
    ----------
    frm : tk.Frame
        Frame of bottom bar of main window.

    Returns
    -------
    None.

    """
    
    frm.rowconfigure(0, weight=1)
    frm.columnconfigure(0, weight=0)
    frm.columnconfigure(1, weight=1)
    
    frm.grid(row=1, column=0, sticky='esw')
    
    return

"""SECOND LEVEL FRAMES"""
#left bar
def format_left_bar(frm):
    """
    Format the left bar of the main window

    Parameters
    ----------
    frm : tk.Frame
        Frame of left bar.

    Returns
    -------
    None.

    """
    
    frm.columnconfigure(0, minsize=15, weight=0)
    
    frm.grid(row=0, column=0, sticky='nes')
    
    return

#display
def format_display(frm):
    """
    Format the diplay frame of the main window

    Parameters
    ----------
    frm : tk.Frame
        Frame of display.

    Returns
    -------
    None.

    """
    
    frm.rowconfigure(0, weight=1)
    frm.columnconfigure(0, weight=1)
    frm.columnconfigure(1, weight=0)
    
    frm.grid(row=0, column=1, sticky='nesw')
    
    return

#element
def format_element(frm):
    """
    Format periodic table frame

    Parameters
    ----------
    frm : tk.Frame
        Frame of periodic table.

    Returns
    -------
    None.

    """
    
    #format columns
    for i in range(0, 18):
        frm.columnconfigure(i, minsize=26, weight=0)
        
    #format rows
    for i in range(0, 9):
        frm.rowconfigure(i, minsize=26, weight=0)
        
    frm.grid(row=0, column=0, sticky='sw')
            
    return

def add_to_element(frm, d, analysis, overlay):
    """
    Adds buttons to the periodic table for each element

    Parameters
    ----------
    frm : tk.Frame
        Periodic table frame.
    d : glb.Changing_Globals
        All global variables.
    analysis : tk.Button
        Button to perform analysis.
    overlay : tk.Button
        Button to see the overlay.

    Returns
    -------
    elements : list
        List of all element buttons.

    """
    
    elements = []
    color_index = 0 
    
    #rows in periodic table
    for r in range(len(glb.element_array)):
        #columns in periodic table
        for c in range(len(glb.element_array[r])):
            
            string = glb.element_array[r][c]
            
            #if element exists
            if string != '0':
                
                #get the color for the element
                color = glb.color_array[color_index]
                
                #make an Element
                ele = Element(string, r, c, color, frm, d, analysis, overlay)
                elements.append(ele)
                
                #increment color array properly
                color_index += 1
                if color_index == len(glb.color_array):
                    color_index = 0
    
    return elements

#output
def format_output(frm):
    """
    Format the output frame

    Parameters
    ----------
    frm : tk.Frame
        Output frame in main window.

    Returns
    -------
    None.

    """
    
    frm.rowconfigure(0, weight=1)
    frm.columnconfigure(0, weight=1)
    
    frm.grid(row=0, column=1, sticky='nesw')
    
    return

def add_to_output(frm):
    """
    Add a textbox and scrollbars to the output frame

    Parameters
    ----------
    frm : tk.Frame
        Output frame.

    Returns
    -------
    txt : tk.Text
        Output textbox.

    """
    
    #make text box
    txt = tk.Text(frm, state='disabled', height=10, wrap=tk.NONE)
    txt.grid(sticky='nesw')
    
    """SCROLLBARS"""
    #vertical scroll
    y = tk.Scrollbar(frm)
    y.grid(row=0, column=1, sticky='ns')
    txt.configure(yscrollcommand=y.set)
    y.configure(command=txt.yview)
    
    #horizontal scroll
    x = tk.Scrollbar(frm, orient=tk.HORIZONTAL)
    x.grid(row=1, column=0, sticky='ew')
    txt.configure(xscrollcommand=x.set)
    x.configure(command=txt.xview)
    
    return txt

"""THIRD LEVEL FRAMES"""
def format_canvas(cnv, y, x, frm):
    """
    Format the canvas in the display frame

    Parameters
    ----------
    cnv : tk.Canvas
        Canvas to be placed in display window.
    y : tk.Scrollbar
        Vertical scroolbar.
    x : tk.Scrollbar
        Horizontal scrollbar.
    frm : tk.Frame
        Display frame.

    Returns
    -------
    None.

    """
    
    #bind the scrolling
    frm.bind(
        "<Configure>",
        lambda e: cnv.configure(
        scrollregion=cnv.bbox("all")
            )
        )
    
    cnv.create_window((0, 0), window=frm, anchor="nw")
    cnv.configure(yscrollcommand=y.set)
    cnv.configure(xscrollcommand=x.set)
    
    #bind scrolling to mouse wheel
    def on_mousewheel(event):
        scroll_num = int(-1*(event.delta/120))
        cnv.yview_scroll(scroll_num, 'units')
        return
    cnv.bind_all('<MouseWheel>', on_mousewheel)
    
    #grid everything
    cnv.grid(row=0, column=0, sticky='nesw')
    y.grid(row=0, column=1, sticky='ns')
    x.grid(row=1, column=0, sticky='ew')
    
    return

"""OTHER TKINTER MENUS/FRAMES"""
#color pop-up menu
def color_menu(d, function, event):
    """
    Add a color po-up menu for the different graphs

    Parameters
    ----------
    d : glb.Changing_Globals
        All global variables.
    function : function
        DColor-changing function.
    event : tk.Event
        Right-click to open menu.

    Returns
    -------
    None.

    """
    
    #get the element used
    row = 0
    info = event.widget.grid_info()
    if 'row' in info:
        row = info['row']
        
    #make menu
    m = tk.Menu(event.widget, tearoff=0)
    
    #add options to menu
    for ele in d.elements:
        for line in ele.lines:
            
            #get variable for color element
            if line.full_name == d.s.metadata.Sample.xray_lines[row]:
                for color in glb.color_array:
                    m.add_radiobutton(label=color, variable=line.color, value=color, command = lambda: function(d))
                    
    #plot the menu
    m.tk_popup(event.x_root, event.y_root)
    
    return

#overlay pop-up menu
def overlay_window(d, function):
    """
    Open a pop-up menu for choosing elements in the overlay

    Parameters
    ----------
    d : glb.Changing_Globals
        All global variabels.
    function : function
        Function for choosing elements.

    Returns
    -------
    None.

    """
    
    #make the pop-up window
    w = tk.Toplevel()
    w.title('Overlay Element Options')
    w.columnconfigure(0, weight=3)
    w.columnconfigure(1, weight=1)
    
    #make labels
    lbl = tk.Label(w, text='X-Ray Lines', padx=18)
    lbl.grid(row=0, column=0, sticky='w')
    
    #make element for each graph
    i = 1
    for ele in d.s.metadata.Sample.xray_lines:
        
        for e in d.elements:
            for line in e.lines:
                if ele == line.full_name:
                    
                    #make button
                    cb = tk.Checkbutton(w, text=ele, variable=line.map, onvalue=True, offvalue=False, padx=30)
                    cb.grid(row=i, column=0, sticky='w')
                    
        i += 1
        
    #make button to quit overlay
    btn = tk.Button(w, text='Make Overlay', command=lambda: function(d, w))
    btn.grid(row=i, column=0, sticky='ew')
    
    
    return

#shell pop-up window
def shell_window(d, sI, disp, shell_dic, function, finish):
    """
    Open a pop-up window for choosing elements and their shells for analysis

    Parameters
    ----------
    d : glb.Changing_Globals
        All global variables.
    sI : list
        List of shells.
    disp : dict
        Dictionary of what to display.
    shell_dic : dict
        Dictionary of shells.
    function : function
        Function to activate when a shell is selected.
    finish : function
        Function to close window and finish analysis.

    Returns
    -------
    None.

    """
    
    w = tk.Toplevel()
    w.title('Shell Analysis Options')
    w.columnconfigure(0, weight=3)
    w.columnconfigure(1, weight=1)
    w.columnconfigure(2, weight=1)
    
    #make labels
    lbl_element = tk.Label(w, text = 'Element')
    lbl_K = tk.Label(w, text = 'K ')
    lbl_L = tk.Label(w, text = 'L ')
    
    #add label to window
    lbl_element.grid(row=0, column = 0, sticky='nesw')
    lbl_K.grid(row=0, column=1, sticky='nesw')
    lbl_L.grid(row=0, column=2, sticky='nesw')

    i = 1
    for ele in d.elements:
        if ele.name in disp:
            
            lbl_element_name = tk.Label(w, text = ele.name)
            lbl_element_name.grid(row = i, column = 0, sticky='nesw')
            
            #if the option for the K-shell exists
            if disp[ele.name][0] == 1:
                bu = tk.Radiobutton(w, variable=ele.shell, value=1, command=lambda:function(d.elements, shell_dic))
                bu.grid(row=i, column=1, sticky='nesw')
           
            #if the option for the L-shell exists
            if disp[ele.name][1] == 1:
                bu = tk.Radiobutton(w, variable=ele.shell, value=2, command=lambda:function(d.elements, shell_dic))
                bu.grid(row=i, column=2, sticky='nesw')
            
            #if the option for no K-shell
            if disp[ele.name][0] == 0 and disp[ele.name][1] == 1:
                bu = tk.Radiobutton(w, variable=ele.shell, value=0, state='disabled', command=lambda:function(d.elements, shell_dic))
                bu.grid(row=i, column=1, sticky='nesw')
            i += 1
    
    btn_quit = tk.Button(w, text="Finish Quantification",
                         command=lambda: quit_shell_window(finish, d, shell_dic, sI, w))
    btn_quit.grid(row=i, column=0, sticky='ew')
    
    #configure rows
    for x in range(i):
        w.rowconfigure(x, weight=1)
    
    return

#quit window
def quit_shell_window(finish, d, shell, sI, w):
    """
    Quits the shell pop-up window and finishes the analysis

    Parameters
    ----------
    finish : function
        Function to finish the analysis on the data.
    d : glb.Changing_Globals
        All global variables.
    shell : dict
        Dictionary of shells.
    sI : list
        List of shell information.
    w : tk.Toplevel
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    #finish analysis
    final_data = finish(d, shell, sI)
    
    #TODO: place text in window
    mtxt.output_analysis(d, d.text, final_data)
    
    #destroy window
    w.destroy()
    w.update()
    
    return