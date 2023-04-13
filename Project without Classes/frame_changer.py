# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 15:16:26 2022

@author: Alyssa Blanc
"""

"""PLACE FRAMES"""
#get the row in a column for insertion
def get_row(frm, c):
    """
    Get the next empty row in a column

    Parameters
    ----------
    frm : tkinter.Frame
        Parent frame.
    c : int
        Column number.

    Returns
    -------
    r : int
        Row number.

    """
    
    r = 0
    
    #analyze the children in the frame
    for w in frm.winfo_children():
        info = w.grid_info()
        if 'column' in info:
            #if the column matches the desired column of placement
            if info['column'] == c:
                r += 1
    
    return r

"""DESTROY FRAMES"""
#destroy all frames in a window
def destroy_all(frm):
    """
    Destroy all children in a frame

    Parameters
    ----------
    frm : tkinter.Frame
        Parent frame.

    Returns
    -------
    None.

    """
    
    for widget in frm.winfo_children():
        widget.destroy()
    
    return

#destroy frame at specific coordinate
def destroy_one(frm, r, c):
    """
    Destroy one child in a frame

    Parameters
    ----------
    frm : tkinter.Frame
        Parent frame.
    r : int
        Row number of child being destroyed.
    c : int
        Column number of child being destroyed.

    Returns
    -------
    None.

    """
    
    #look at all children
    for w in frm.winfo_children():
        info = w.grid_info()
        if 'row' and 'column' in info:
            #if at the desired location
            if info['row'] == r and info['column'] == c:
                w.destroy()
    
    return

#destroy all the frames in a specific column
def destroy_column(frm, c):
    """
    Destroy all children in a given column

    Parameters
    ----------
    frm : tkinter.Frame
        Parent frame.
    c : int
        Column number.

    Returns
    -------
    None.

    """
    
    #look at all the children
    for w in frm.winfo_children():
        info = w.grid_info()
        if 'column' in info:
            #if in the desired column
            if info['column'] == c:
                w.destroy()
    
    return

"""LOCATE FRAMES"""
#get the toolbar widget below a frame
def get_toolbar(w):
    """
    Get the toolbar of a given frmae

    Parameters
    ----------
    w : tkinter.Canvas
        Canvas of toolbar.

    Returns
    -------
    wid : matplotlib_backends.NavigationToolbar2Tk
        Toolbar of window.

    """
    
    #get cordinate of toolbar
    event_cord = w.grid_info()
    tool_cord = (event_cord['row'] + 1, event_cord['column'])
    
    #get the toolbar
    for wid in w.master.winfo_children():
        info = wid.grid_info()
        #check row and column
        if info['row'] == tool_cord[0] and info['column'] == tool_cord[1]:
            return wid
    
    return
