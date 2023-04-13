# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 08:03:53 2022

@author: Alyssa Blanc
"""

import matplotlib
import plotting as plot
import re
import format_frames as ff
from shell_files import k_shells, l_shells
import hyperspy.api as hs

#add to the shells used dictionary
def shells_used_function(elements, shells):
    """
    Determine what shells will be used in the analysis

    Parameters
    ----------
    elements : list
        List of all elements.
    shells : list
        List of all shells.

    Returns
    -------
    None.

    """
        
    for ele in elements:
        if ele.shell.get() == 1:
            shells[ele.name] = [1, 0]
        if ele.shell.get() == 2:
            shells[ele.name] = [0, 1]
    
    return

#get peaks of all elements
def get_peaks(d):
    """
    Find all of the peaks in the data

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.

    Returns
    -------
    array : list
        List of a tuple of elements, x-coordinat of height, and height.

    """
    
    array = []
    
    #get intensities
    sI = d.m.get_lines_intensity()
    
    #iterate
    for x in sI:
        
        #get element
        ele = x.metadata.Sample.xray_lines[0]
        
        #get x-cord
        string = x.metadata.General.title
        x_cord_str = re.findall('\d+\.\d+', string)
        x_cord = float(x_cord_str[0])
        
        for y in d.m.active_components:
            if ele == y.name:
                x_cord = y.centre.value
                
        #get height
        xI = int(x_cord * d.beam)
        height = d.s_model.data[xI]
        
        #add to list
        array.append(tuple([ele, x_cord, height]))
    
    return array

def run_TEM_analysis(d):
    """
    Run a TEM analysis of a line

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.

    Returns
    -------
    None.

    """
    
    matplotlib.use('nbagg')
    
    #only run if model is showing
    if not d.model:
        return
    
    #make a current shell and update all elements
    shell_dic = {}
    for ele in d.elements:
        ele.shell.set(0)
    
    #plot residual and chi_squared
    plot.show_residual(d)
    plot.show_chi_squared(d)
    
    #perform k-factor analysis
    choose_shell(d, shell_dic)
    
    return

#choose shell to analyze
def choose_shell(d, shell_dic):
    """
    Select the shells to be used with a pop-up display window

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variabels.
    shell_dic : dict
        Dictionary of shells in the data.

    Returns
    -------
    None.

    """
    
    #make display dictionary
    display = {}
    
    #get intensities
    sI = d.m.get_lines_intensity()
    #add intensities to display
    for x in sI:
        ele = x.metadata.Sample.elements[0]
        display[ele] = [0, 0]
        
    #see if the element has a Ka and/or La line to display
    for x in sI:
        split = x.metadata.Sample.xray_lines[0].partition('_')
        
        #using binary system, determine [Ka, La]
        line = display[split[0]]
        if split[2] == 'Ka':
            line[0] = 1
        elif split[2] == 'La':
            line[1] = 1
            
        display[split[0]] = line
        
    #create a window for the shell options
    ff.shell_window(d, sI, display, shell_dic, shells_used_function, finish_analysis)
    
    display.clear()
    
    return

"""FINISH THE ANALYSIS"""

#get k-factors
def get_k_factors(shells):
    """
    Get the k-factor for each element in shells

    Parameters
    ----------
    shells : dict
        Dictionary of shells.

    Returns
    -------
    array : list
        List of tuples of k-factors in shells.

    """
    
    array = []
    for key in shells:
        
        #if k is being used, check k_shells
        if shells[key][0] == 1:
            for k in k_shells:
                if key == k[0]:
                    array.append(tuple([key, 'K', k[1]]))
                    
        #if l is being used, check l_shells
        elif shells[key][1] == 1:
            for l in l_shells:
                if key == l[0]:
                    array.append(tuple([key, 'L', l[1]]))
                        
    return array

#get intensities
def get_intensities(k_factors, sI):
    """
    Get the intsities of different elements in the sample

    Parameters
    ----------
    k_factors : list
        List of k-factors.
    sI : list
        List of intensities.

    Returns
    -------
    array : TYPE
        DESCRIPTION.

    """
    
    array = []
    for ele in k_factors:
        for i in sI:
            
            #add intensities
            name = ele[0] + '_' + ele[1] + 'a'
            if name == i.metadata.Sample.xray_lines[0]:
                array.append(i)
    
    return array

#isolate k-factors
def isolate_k(k_f):
    """
    Isolate the k-factors from the k-factor tuple list

    Parameters
    ----------
    k_f : list
        List of tuples of k-factors.

    Returns
    -------
    array : List
        List of k-factors.

    """
    
    array = []
    for k in k_f:
        array.append(k[2])
    
    return array

def weight_percents(comp, fd):
    """
    Get the wieght percents of each element in the data

    Parameters
    ----------
    comp : list
        List of the composition of the element.
    fd : list
        List of many attributes, including element percents.

    Returns
    -------
    None.

    """
        
    #create array of atomic percents
    ap = []
    for i in range(len(comp)):
        ap.append(comp[i].data[0])
    
    #create array of element percents
    ep = []
    for i in range(len(comp)):
        ep.append(fd[i][0])
        
    #get weight
    w = hs.material.atomic_to_weight(ap, ep)
    
    #add to final data
    for i in range(len(w)):
        fd[i][2].append(w[i])
    
    return

#get sigma values to find error
def get_sigma(d, fd):
    """
    Get the sigma for each line in the data

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    fd : list
        List of data.

    Returns
    -------
    None.

    """
    
    peak = get_peaks(d)
    
    for p in peak:
        
        eV = p[1]
        
        peak_height, peak_i, false_alarms = 0, 0, 0
        
        i = int(eV * d.beam)
        while peak_height == 0 and false_alarms < 10:
            
            #if larger than left
            if d.s.data[i] > d.s.data[i + 1]:
                
                #if larger than right
                if d.s.data[i] > d.s.data[i + 1]:
                    
                    #check if actually peak
                    if (d.s.data[i] > d.s.data[i - 2] and d.s.data[i] > d.s.data[i + 2]):
                        
                        peak_height = d.s.data[i]
                        peak_i = i / float(d.beam)
                        
                    #if not actually the peak
                    else:
                        false_alarms += 1
                        if d.s.data[i - 2] > d.s.data[i + 2]:
                            i -= 2
                        else:
                            i += 2
                            
                #if right is larger
                else:
                    i += 1
                
            #if left is larger
            else:
                i -= 1
                
        #if loop times out
        if peak_height == 0:
            peak_height = d.s.data[i]
            peak_i = i / float(d.beam)
            
        #get the difference of the eV
        diff = abs(peak_i - eV)
        
        #divide by sigma
        sig = 0
        for x in d.m.active_components:
            if p[0] == x.name:
                sig = diff / x.sigma.value
                
        #add to final data
        for i in range(len(fd)):
            ele = fd[i][0] + '_' + fd[i][1] + 'a'
            if p[0] == ele:
                fd[i][2].append(sig)
    
    return

#finish analysis after window closes
def finish_analysis(d, shells, sI):
    """
    Finish the analysis of the TEM data

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    shells : list
        List of shells in the element.
    sI : list
        List of data regarding the sample.

    Returns
    -------
    final_data : list
        List of everything relating to the final data.

    """
        
    #get k factors of each element
    k_factors_ele = get_k_factors(shells)
    
    #get intensities
    intensities = get_intensities(k_factors_ele, sI)
    
    #isolate k-factors
    k_factors = isolate_k(k_factors_ele)
    
    #finalize data
    final_data = []
    
    #add base data to final data
    for ele in k_factors_ele:
        final_data.append(tuple([ele[0], ele[1], [ele[2]]]))
        
    #perform k-factor quantification
    if len(intensities) == 0:
        return
    composition = d.s.quantification(method='CL', intensities=intensities, factors=k_factors, composition='atomic')
    
    #add the atomic percents to the final data
    for i in range(len(composition)):
        final_data[i][2].append(composition[i].data[0])
        
    #add weight percents to the final data
    weight_percents(composition, final_data)
    
    #add intensities to the final data
    for i in range(len(final_data)):
        for j in range(len(sI)):
            ele_shell = final_data[i][0] + '_' + final_data[i][1] + 'a'
            eS = sI[j].metadata.Sample.xray_lines[0]
            if ele_shell == eS:
                final_data[i][2].append(sI[j].data[0])
                
    #get sigma and add to final data
    get_sigma(d, final_data)
    
    return final_data