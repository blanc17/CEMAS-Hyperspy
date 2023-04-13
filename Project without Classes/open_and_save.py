# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 13:57:56 2022

@author: Alyssa Blanc
"""
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import manipulate_text as mtxt
import frame_changer as fc
from PIL import ImageTk, Image
from os.path import exists

"""ALL FILES"""

#filepath dropdown menus
def get_filepath(t):
    """
    Allows the user to select the file

    Parameters
    ----------
    t : string
        Type of file selected.

    Returns
    -------
    filepath : str
        Full filepath.
    signal_type : str
        Type of signal to be analyzed.

    """
    
    filepath = ''
    signal_type = ''
    
    if t == '.emd':
        
        filepath = askopenfilename(
            filetypes = [
                ("EMD files", "*.emd"),
                ("All Files", "*.*")
                ]
            )
        signal_type = 'EDS_SEM'
        
    elif t == '.h5':
        
        filepath = askopenfilename(
            filetypes = [
                ("USID files", "*.h5"),
                ("All Files", "*.*")
                ]
            )
        signal_type = 'EDS_SEM'
        
    elif t == '.msa':
        
        filepath = askopenfilename(
            filetypes = [
                ("MSA files", "*.msa"),
                ("All Files", "*.*")
                ]
            )
        signal_type = 'EDS_TEM'
    
    elif t == '.spc':
        
        filepath = askopenfilename(
            filetypes = [
                ("EDAX files", "*.spc"),
                ("All Files", "*.*")
                ]
            )
        signal_type = 'EDS_TEM'
        
    elif t == '.spd':
        
        filepath = askopenfilename(
            filetypes = [
                ("EDAX files", "*.spd"),
                ("All Files", "*.*")
                ]
            )
        signal_type = 'EDS_SEM'
        
    #if the end of the filepath does not match the type
    if t not in filepath:
        filepath = ''
    
    return filepath, signal_type

#clear the display of data and reset buttons and variables
def reset_display(left, d):
    """
    Reset all variables regarding the display

    Parameters
    ----------
    left : tk.Frame
        Frame full of buttons on the left-hand side of the screen.
    d : global_arrays.Changing_Globals
        All global variables.

    Returns
    -------
    None.

    """
    
    #clear text
    mtxt.clear_text(d.text)
    
    #delete all widgets
    fc.destroy_all(d.frame)
    
    #TODO: figure out what method to use once I decide how to add to the left bar
    #dest.destroy_all(left)
    for widget in left.winfo_children():
        if isinstance(widget, tk.Button):
            widget.configure(state='disabled')
    
    #reset all booleas displaying variables
    d.reset()
    
    #reset elements
    for e in d.elements:
        e.reset_variables()
        e.reset_buttons()
    
    return

#enable x-ray lines
def enable_xray_lines(elements, s):
    """
    Enable all x-ray lines in the element

    Parameters
    ----------
    elements : list
        List of all elements.
    s : hs.EDSTEMSpectrum, hs.EDSSEMSpectrum
        HyperSpy spectrum.

    Returns
    -------
    None.

    """
    
    for ele in elements:
        for line in ele.lines:
            if line.full_name in s.metadata.Sample.xray_lines:
                line.bool.set(True)
    
    return

"""EDS_SEM FILES"""

#load image of spd
def load_image(file, frm):
    """
    Load an image from a file

    Parameters
    ----------
    file : str
        Name of file.
    frm : tk.Frame
        Frame to place image in.

    Returns
    -------
    None.

    """
    
    #get file name
    string = file.partition('.')[0] + '.' + 'bmp'
    
    #get image
    if exists(string):
        img = Image.open(string)
        photo = ImageTk.PhotoImage(img)
        
        #make a label of the image
        lbl = tk.Label(frm, image=photo)
        lbl.image = photo
        
        #insert image
        r = fc.get_row(frm, 0)
        lbl.grid(row=r, column=0, sticky='nesw')
    
    return

#get intensities at every pixel
def pixel_intensities(d, pixels):
    """
    Iterate over image to get all pixels

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    pixels : int
        Number of pixels.

    Returns
    -------
    img_array : list
        List of pixel intensities.

    """
    
    img_array = []
    
    #iterate over data
    for n in d.s.data:
        array = []
        for m in n:
            array.append(sum(m))
        img_array.append(array)
        
        #change text in figure
        pixels -= len(d.s.data[0])
        mtxt.pixel_output(d.text, pixels)
    
    return img_array

#save the output
def save_file(txt):
    """
    Save the output of the text box in a text file

    Parameters
    ----------
    txt : tk.Text
        Text box.

    Returns
    -------
    None.

    """
    
    #get name of file path
    filepath = asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    
    if not filepath:
        return
    
    #open and write from the output window
    with open(filepath, mode="w", encoding="utf-8") as output_file:
        text = txt.get("1.0", tk.END)
        output_file.write(text)
    
    return