# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 15:12:13 2022

@author: Alyssa Blanc
"""

#clear the text box
def clear_text(txt):
    """
    Clear the whole text box

    Parameters
    ----------
    txt : tkinter.Text
        Text box to be cleared.

    Returns
    -------
    None.

    """
    
    txt.configure(state='normal')
    txt.delete(1.0, 'end')
    txt.configure(state='disabled')
    
    return

#pixel output
def pixel_output(txt, pixels):
    """
    Output the waiting messages for loading an image full of pixels

    Parameters
    ----------
    txt : ikinter.Text
        Text box.
    pixels : int
        Number of pixels left to load.

    Returns
    -------
    None.

    """
    
    #delete current text
    clear_text(txt)
    
    txt.configure(state='normal')
    
    #display loading message
    string = ('Loading image... %s pixels left\n\nSome analysis can be done while loading figure' % pixels)
    txt.insert('end', string)
    
    txt.configure(state='disabled')
    
    #update to show the message
    txt.update()
    
    #clear text at end
    clear_text(txt)
    
    return

#general loading output
def load(txt):
    """
    Loading message for small images

    Parameters
    ----------
    txt : tkiner.Text
        Text box.

    Returns
    -------
    None.

    """
    
    #clear text
    clear_text(txt)
    
    txt.configure(state='normal')
    txt.insert('end', 'LOADING FIGURES. PLEASE WAIT.')
    txt.configure(state='disabled')
    
    txt.update()
    
    return

#output data
def output_analysis(d, txt, fd):
    """
    Print the analysis to the window

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    txt : tkinter.Text
        Test box.
    fd : list
        List of data for each element analyzed.

    Returns
    -------
    None.

    """
    
    #clear text
    clear_text(txt)
    
    txt.configure(state='normal')
    
    #insert header
    tem = d.s.metadata.Acquisition_instrument.TEM
    eds = tem.Detector.EDS
    
    txt.insert('end', 'Project: %s\n' %(d.s.metadata.General.original_filename))
    txt.insert('end', 'kV: %d\n'%(tem.beam_energy))
    txt.insert('end', 'Live Time: {:.4f}\n'.format(eds.live_time))
    txt.insert('end', 'Takeoff Angle: {:.1f}\n'.format(eds.elevation_angle))
    txt.insert('end', 'Resolution: {:.4f}\n\n'.format(eds.energy_resolution_MnKa))
    
    #insert column header
    txt.insert('end', 'Element\t\tWeight %\t\tAtomic %\t\tK-Factor\t\tNet Intensity\t\tSigma\n')
        
    #insert all elements
    for ele in fd:
        txt.insert('end', '{} {} \t\t{:.2f}\t\t{:.2f}\t\t{:.2f}\t\t{:.2f}\t\t{:.2f}\n'.format(ele[0], ele[1], ele[2][2], ele[2][1], ele[2][0], ele[2][3], ele[2][4]))
        
    txt.configure(state='disabled')
    
    return