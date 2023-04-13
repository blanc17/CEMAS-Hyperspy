# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 15:17:24 2022

@author: Alyssa Blanc
"""
import plotting as plot
import matplotlib.path as mpltPath
import math
import random

"""SEM SHAPE ANALYSIS"""
#line
def analysis_over_line(d, width):
    """
    Numerical analysis of intenisities over a line

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    width : int
        Width of line.

    Returns
    -------
    y_axis : list
        List of all intensities along the line.

    """
    
    y_axis = None
    s = d.shape
    
    #if a vertical line
    if s.x0 == s.x1:
        
        #get min and max points
        min_point = min(s.y0, s.y1)
        max_point = max(s.y0, s.y1)
        
        #get y axis
        y_axis = d.s.data[min_point][s.x0]
        while min_point < max_point:
            for x in range(s.x0 - width, s.x0 + width):
                min_point += 1
                y_axis += d.s.data[min_point][s.x0]
        
    #if not a veritcal line
    else:
        
        slope = (s.y1 - s.y0) / (s.x1 - s.x0)
        b = round(s.y0 - (slope * s.x0))
        
        y_axis = plot.y_axis(d.s.data[0][0])
        
        #iterater over all of the pixels
        for y in range(len(d.s.data)):
            for x in range(len(d.s.data[y])):
                
                #if the point lies on the line based on b
                poss_b = round(y - (slope * x))
                if poss_b >= b-width and poss_b <= b+width:
                    
                    #if the x and y cordinates fall within the line
                    if y >= min(s.y0, s.y1) and y <= max(s.y0, s.y1):
                        if x >= min(s.x0, s.x1) and x <= max(s.x0, s.x1):
                            
                            y_axis += d.s.data[y][x]
              
    return y_axis

#rectangle
def analysis_over_rectangle(d):
    """
    Numerical analysis of intensities in a rectangle

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.

    Returns
    -------
    y_axis : list
        List of all intensities in the rectangle.

    """
    
    #make the y axis
    y_axis = plot.y_axis(d.s.data[0][0])
    s = d.shape
    
    #iterate over all the pixels
    for y in range(len(d.s.data)):
        for x in range(len(d.s.data[y])):
            
            #if x and y cords fall in the box
            if y >= min(s.y0, s.y1) and y <= max(s.y0, s.y1):
                if x >= min(s.x0, s.x1) and x <= max(s.x0, s.x1):
                    
                    y_axis += d.s.data[y][x]
    
    return y_axis

#oval
def analysis_over_oval(d):
    """
    Numerical analysis of all intensities in an oval

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.

    Returns
    -------
    y_axis : list
        List of all intensisites in the oval.

    """
    
    s = d.shape
    
    #get the midpoint
    h = (s.x0 + s.x1) / 2
    k = (s.y0 + s.y1) / 2
    
    #get the radius
    rx = abs(h - s.x0)
    ry = abs(k - s.y0)
    
    #make the y_axis
    y_axis = plot.y_axis(d.s.data[0][0])
    
    #iterate over pixels
    for y in range(len(d.s.data)):
        for x in range(len(d.s.data[y])):
            
            #check both x and y
            x_check = (((x - h)**2) / (rx**2))
            y_check = (((y - k)**2) / (ry**2))
            
            #if inside oval
            if x_check + y_check <= 1:
                y_axis += d.s.data[y][x]
    
    return y_axis

#polygon
def analysis_over_polygon(d):
    """
    Numerical analysis of all intensities in a polygon

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.

    Returns
    -------
    y_axis : list
        List of all intensities in the polygon.

    """
    
    s = d.shape
    
    #make y_axis
    y_axis = plot.y_axis(d.s.data[0][0])
        
    #make lint of points for polygon
    p_list = []
    for e in s.cords:
        temp = []
        temp.append(e[0])
        temp.append(e[1])
        p_list.append(temp)
        
    path = mpltPath.Path(p_list)
    
    #if the polygon is only a line
    if len(s.cords) == 2:
        if s.x0 != s.x1 or s.y0 != s.y1:
            y_axis = analysis_over_line(d, 1)
            
    #if it is more than a line
    else:
        
        #iterate over all pixels
        for y in range(len(d.s.data)):
            for x in range(len(d.s.data[y])):
                p = [x, y]
                
                #see if the point lies inside the polygon
                inside = path.contains_points([p])
                if inside[0]:
                    y_axis += d.s.data[y][x]
                    
    
    return y_axis

"""OVERLAY ANALYSIS"""
#check perpendicular points
def check_perp(d, width, x, y, slope, b, p, intensity):
    """
    Check all values that line in the perpendicular of a line

    Parameters
    ----------
    d : global_arrays.Changing_GLobals
        All global variables.
    width : int
        Width of line.
    x : int
        X coordinate.
    y : int
        y coordinate.
    slope : int
        Slope of line.
    b : int
        Y-intercept of line.
    p : numpy.float64
        Initial intensity at a point.
    intensity : list
        List of intensities.

    Returns
    -------
    None.

    """

    
    #check all points
    for yy in range(len(d.s.data)):
        for xx in range(len(d.s.data[yy])):
            
            #if the point is not the same
            if yy != y and xx != x:
                
                #if the point lies on the slope
                poss_b = round(yy - (slope * xx))
                if poss_b >= b - 1 and poss_b <= b + 1:
                    
                    distance = math.sqrt((xx - x)**2 + (yy - y)**2)
                    if distance <= width:
                        
                        p += intensity[0].data[yy][xx]
    
    return

#check points
def check_points(d, width, slope, b, mm, intensity, line, y_axis):
    """
    Check all points within a figure for linear analysis

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    width : int
        Width of line (in pixels).
    slope : int
        slope of line.
    b : int
        Y-intercept of line.
    mm : dict
        Min and max values of a line.
    intensity : list
        List of intensities.
    line : str
        Line name.
    y_axis : dict
        Dictionary of y-axis data.

    Returns
    -------
    None.

    """
    
    #get the slope of the perpendicular
    perp_slope = -1 * (1.0 / slope)
    #get the min and max possible perp b
    #get the y's
    y_min = slope * mm['min_x'] + b
    y_max = slope * mm['max_x'] + b
    #get the b's
    b_min = y_min - (perp_slope * mm['min_x'])
    b_max = y_max - (perp_slope * mm['max_x'])
    #switch values if need be
    if b_min > b_max:
        temp = b_min
        b_min = b_max
        b_max = temp
    
    #iterate over all pixels
    for y in range(len(d.s.data)):
        for x in range(len(d.s.data[y])):
            
            #if the point lies on the line
            poss_b = round(y - (slope * x))
            if poss_b >= b - 1 and poss_b <= b + 1:
                
                #if the x and y cords fall within range
                if y >= mm['min_y'] and y <= mm['max_y']:
                    if x >= mm['min_x'] and x <= mm['max_x']:
                        
                        p = intensity[0].data[y][x]
                        
                        # #account for all points along the line width
                        # perp_slope = -1 * (1.0 / slope)
                        # perp_b = y - (perp_slope * x)
                        
                        # #check perpendicular points
                        # check_perp(d, width, x, y, perp_slope, perp_b, p, intensity)
                        
                        #add to the axis
                        if x in y_axis[line]:
                            y_axis[line][x][y] = p
                        else:
                            y_axis[line][x] = {}
                            y_axis[line][x][y] = p
                            
    #check the perpendicular for every point
    for y in range(len(d.s.data)):
        for x in range(len(d.s.data[y])):
            dis = shortest_distance(x, y, slope, -1, b)
            if dis <= width and dis != 0:
                #check if point is perpendicular to line
                b = y - (perp_slope * x)
                if b >= b_min and b <= b_max:
                    #check distances to each point already in the line
                    min_dis = len(d.s.data) * len(d.s.data[y])
                    min_x = len(d.s.data[y])
                    min_y = len(d.s.data)
                    print(x)
                    print(y)
                    print(dis)
                    for x1 in y_axis[line]:
                        for y1 in y_axis[line][x1]:
                            poss_min = math.dist([x,y], [x1, y1])
                            print(poss_min)
                            #set the minimum distance
                            if poss_min < min_dis:
                                min_dis = poss_min
                                min_x = x1
                                min_y = y1
                    #add the intensity to the closest point
                    p = intensity[0].data[y][x]
                    p_current = y_axis[line][min_x][min_y]
                    y_axis[line][min_x][min_y] = p + p_current
    
    return

#shortest distance funtion for points
def shortest_distance(x1, y1, a, b, c):
    
    d = abs((a * x1 + b * y1 + c)) / (math.sqrt(a * a + b * b))
    return d


#check points
def check_points_2(d, width, slope, b, mm, intensity, line, y_axis):
    """
    Check all points within a figure for linear analysis

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    width : int
        Width of line (in pixels).
    slope : int
        slope of line.
    b : int
        Y-intercept of line.
    mm : lint
        Min and max values of a line.
    intensity : list
        List of intensities.
    line : str
        Line name.
    y_axis : list
        List of y-axis data.

    Returns
    -------
    None.

    """
    
    #iterate over all pixels
    for y in range(len(d.s.data)):
        for x in range(len(d.s.data[y])):
            
            #if the point lies on the line
            poss_b = round(y - (slope * x))
            if poss_b >= b - 1 and poss_b <= b + 1:
                
                #if the x and y cords fall within range
                if y >= mm[2] and y <= mm[3]:
                    if x >= mm[0] and x <= mm[1]:
                        
                        p = intensity[0].data[y][x]
                        
                        #account for all points along the line width
                        perp_slope = -1 * (1.0 / slope)
                        perp_b = y - (perp_slope * x)
                        
                        #check perpendicular points
                        check_perp(d, width, x, y, perp_slope, perp_b, p, intensity)
                        
                        #add to the axis
                        array = y_axis[line]
                        array.append(p)
                        y_axis.update({line: array})
    
    return

#TODO: Update method so a dictionary of points is used
def line_profile_analysis(d, width):
    """
    Analyze the elements and their intensities over a line

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    width : int
        Width of line.

    Returns
    -------
    None.

    """
    
    s = d.shape
    
    #get the coordinates of the max and min values of the line
    x0, x1, y0, y1 = s.line_x0, s.line_x1, s.line_y0, s.line_y1
    #dictionary of min and max
    min_max = {'min_x': min(x0, x1), 'max_x': max(x0, x1), 
               'min_y': min(y0, y1), 'max_y': max(y0, y1)}
    
    y_axis = {}
    #if a veritcal line is drawn
    if x0 == x1:
        
        #iterate over lines
        for ele in d.elements:
            for line in ele.lines:
                
                #if the line is on the map
                if line.map.get():
                    
                    #add line to dictionary
                    if line.full_name not in y_axis:
                        y_axis[line.full_name] = {}
                        
                    intensity = d.s.get_lines_intensity([line.full_name])
                    
                    #iterate over points
                    y = min_max['min_y']
                    for y in range(min_max['min_y'], min_max['max_y'] + 1):
                    #while y < min_max['max_y']:
                        
                        p = intensity[0].data[y][x0]
                        
                        #account for width
                        for x in range(x0 - width, x1 + width):
                            if x != x0:
                                p += intensity[0].data[y][x]
                                
                        #add to the axis
                        dic = y_axis[line.full_name]
                        dic[y] = p
                        y_axis.update({line.full_name: dic})
                        
                        plot.plot_profile_vertical(y_axis, 1, 2, d)
    
    #TODO: make horizontal case
    #if line drawn is not vertical
    else:
        
        #get slope and b
        slope = (y1 - y0) / (x1 - x0)
        b = round(y0 - (slope * x0))
        
        #iterate over all lines
        for ele in d.elements:
            for line in ele.lines:
                
                #if the line is in the map
                if line.map.get():
                    
                    #add line to dictionary
                    if line.full_name not in y_axis:
                        y_axis[line.full_name] = {}
                        
                    #get intensity
                    intensity = d.s.get_lines_intensity([line.full_name])
                    
                    #check all points
                    check_points(d, width, slope, b, min_max, intensity, line.full_name, y_axis)
                           
                    #print(y_axis)
                    
                    #TODO: check slope and make y_axis
                    dic = {}
                    if slope >= -1 and slope <= 1:
                        #use x_axis variables
                        dic = use_x_axis(y_axis, line.full_name)
                    else:
                        #use y_axis variables
                        print('not yet')

                    #plot the line profile
                    #TODO: figure out how to get all of the lines on one image
                    plot.plot_profile(dic, line.full_name, 1, 2, d)
    
    return

def use_x_axis(axis, line):
    """
    Develop an array based off of the x-axis of the picture

    Parameters
    ----------
    y_axis : dict
        All points and intensisties of the graph.

    Returns
    -------
    dic : list
        Intensity data.

    """
    
    temp = {}
    for x in axis[line]:
        temp[x] = 0
        i = 0
        #sum every instensity for every y coordinate
        for y in axis[line][x]:
            temp[x] += axis[line][x][y]
            i+=1
        #take avearge
        temp[x] = temp[x] / i
    
    #put in numerical order
    dic = []
    while bool(temp):
        #get the min value
        min_x = random.choice(list(temp.keys()))
        for x in temp:
            if x < min_x:
                min_x = x
        #add the min value to the list
        dic.append([min_x, temp[min_x]])
        #print(dic)
        #remove the value from temp
        del temp[min_x]
          
    return dic

#line profile
def line_profile_analysis_2(d, width):
    """
    Analyze the elements and their intensities over a line

    Parameters
    ----------
    d : global_arrays.Changing_Globals
        All global variables.
    width : int
        Width of line.

    Returns
    -------
    None.

    """
    
    s = d.shape
    
    #set s.line(cord) to something else to make calculation simpler
    x0, x1, y0, y1 = s.line_x0, s.line_x1, s.line_y0, s.line_y1
    
    min_max = [min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)]
    
    y_axis = {}
    #if not a straight, vertical line
    if x0 != x1:
        
        #get slope and b
        slope = (y1 - y0) / (x1 - x0)
        b = round(y0 - (slope * x0))
        
        #iterate over all lines
        for ele in d.elements:
            for line in ele.lines:
                
                #if the line is in the map
                if line.map.get():
                    
                    #add line to dictionary
                    if line.full_name not in y_axis:
                        y_axis[line.full_name] = []
                        
                    #get intensity
                    intensity = d.s.get_lines_intensity([line.full_name])
                    
                    #check all points
                    check_points(d, width, slope, b, min_max, intensity, line.full_name, y_axis)
                    
        #plot line profile
        plot.plot_profile(y_axis, 1, 2, d)
        
    #else if vetical
    else:
        
        #iterate over lines
        for ele in d.elements:
            for line in ele.lines:
                
                #if the line is on the map
                if line.map.get():
                    
                    #add line to dictionary
                    if line.full_name not in y_axis:
                        y_axis[line.full_name] = []
                        
                    intensity = d.s.get_lines_intensity([line.full_name])
                    
                    #iterate over points
                    y = min_max[2]
                    while y < min_max[3]:
                        
                        p = intensity[0].data[y][x0]
                        
                        #account for width
                        for x in range(x0 - width, x1 + width):
                            if x != x0:
                                p += intensity[0].data[y][x]
                                
                        #add to the axis
                        array = y_axis[line.full_name]
                        array.append(p)
                        y += 1
                        y_axis.update({line.full_name: array})
                        
    plot.plot_profile(y_axis, 1, 2, d)

    
    return