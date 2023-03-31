import tkinter as tk
import re

#class for main window
class window(tk.Tk):
    #initialize
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #placeholder variables for left bar functions
        self.display_locked = False
        self.width = 1
        self.line_type = tk.StringVar()
        self.line_type.set('line')

        #add a title
        self.wm_title('THE(TM) HyperSpy Analysis')
        #resize the window
        self.wm_state('zoomed')

        #create a menu for the main window
        self.make_menu()

        #create the main frames
        frm_main = tk.Frame(self,highlightbackground="blue", highlightthickness=2)
        frm_main.pack(side='top', fill='both', expand=True,)
        frm_bottom = tk.Frame(self,highlightbackground="red", highlightthickness=2)
        frm_bottom.pack(side='bottom', fill='x', expand=False)

        #create usable frames
        self.left_bar = LeftBar(frm_main, self)
        self.left_bar.pack(side='left', fill='y', expand=False)


    #make a menu for the top bar
    def make_menu(self):

        menu = tk.Menu()

        #Add an open button with different types to open
        open = tk.Menu(menu, tearoff=0)
        for M in (Spc, Spd):
            M(open, self)
        menu.add_cascade(label='Open', menu=open)

        #add a save button 
        save = tk.Menu(menu, tearoff=0)
        Save(save, self)
        menu.add_cascade(label='Save', menu=save)

        #add the menu to the window
        self.configure(menu=menu)
    
    #make a function for opening files
    def open_file(self, file_type:str):
        print(file_type)
    #make a function for saving files
    def save_file(self):
        print('Save')

    #functions for setting constant variables
    def set_width(self, event:tk.Event, entry:tk.Entry):

        #remove letters
        num = re.sub("[^0-9]", "", entry.get())
        #set width
        if num == '' or num == '0':
            num = '1'
        self.width = int(num)
        #update entry
        entry.delete(0, tk.END)
        entry.insert(0, num)
    

    #temporary placeholders for buttons in the left bar
    #TODO: figure out what to do with functions
    def plot_lines(self):
        print('plot_lines')
    def show_model(self):
        print('show_model')
    def run_TEM_analysis(self):
        print('run_TEM_analysis')
    def show_maps(self):
        print('show_maps')
    def show_overlay(self):
        print('show_overlay')

#Classes for Menu
class Spc():
    #initialize
    def __init__(self, button:tk.Menu, main:window):
        button.add_command(label='.spc', command= lambda:main.open_file('.spc'))
class Spd():
    #initialize
    def __init__(self, button:tk.Menu, main:window):
        button.add_command(label='.spd', command= lambda:main.open_file('.spd'))
class Save():
    #initialize:
    def __init__(self, button:tk.Menu, main:window):
        button.add_command(label='Save Output', command=main.save_file)

#Classes for frames
class LeftBar(tk.Frame):
    #initialize
    def __init__(self, parent:tk.Frame, main=window):
        tk.Frame.__init__(self, parent, relief=tk.RAISED, bd=2)

        #add commands to the left bar
        for M in (Lines, Analysis1D, Analysis2D):
            m = M(self, main)
            m.pack(side='top', fill='x', expand=False, padx=5, pady=5)

    def lb_pack(self, button:tk.Button):
        button.pack(side='top', fill='x', expand=False, padx=5, pady=5)
 
#Classes for left bar functions
class Lines(tk.Frame):
    #initialize
    def __init__(self, parent:LeftBar, main:window):
        tk.Frame.__init__(self, parent)
        #Add the buttons and checkmark for line analysis
        #TODO: figure out a good location for the function
        self.button = tk.Button(self, text='Check Element Lines', command = main.plot_lines, state='disabled')
        parent.lb_pack(self.button)
        self.check = tk.Checkbutton(self, text='Lock Display', variable = main.display_locked, onvalue=True, offvalue=False)
        parent.lb_pack(self.check)
class Analysis1D(tk.Frame):
    #initialize
    def __init__(self, parent:LeftBar, main:window):
        tk.Frame.__init__(self, parent)
        #Add the buttons for TEM analysis
        #TODO: figure out a good location for the functions
        self.model = tk.Button(self, text="Display Model", command = main.show_model, state='disabled')
        parent.lb_pack(self.model)
        self.analysis = tk.Button(self, text='Run Analysis', command = main.run_TEM_analysis, state = 'disabled')
        parent.lb_pack(self.analysis)
class Analysis2D(tk.Frame):
    #initialize
    def __init__(self, parent:LeftBar, main:window):
        tk.Frame.__init__(self, parent)
        #Add the buttons for SEM analysis
        #TODO: figure out a good location for the functions
        self.maps = tk.Button(master=self, text="Element Maps", command = main.show_maps, state='disabled')
        parent.lb_pack(self.maps)
        self.overlay = tk.Button(master=self, text="Overlay Maps", command= main.show_overlay, state='disabled')
        parent.lb_pack(self.overlay)
        #add attributes for changing width and line type
        #width
        frm_width = tk.Frame(self)
        lbl_width = tk.Label(frm_width, text='Line Weight: ')
        parent.lb_pack(lbl_width)
        ent_width = tk.Entry(frm_width, state='disabled')
        parent.lb_pack(ent_width)
        ent_width.bind('<KeyRelease>', lambda event: main.set_width(event, ent_width))
        parent.lb_pack(frm_width)
        #type of line
        frm_type = tk.Frame(self)
        lbl_width = tk.Label(frm_type, text='Shape Type: ')
        parent.lb_pack(lbl_width)
        #TODO: attempt turning into a dictionary
        option = [Line, Rectangle, Oval, Polygon]
        drop_down = tk.OptionMenu(frm_type, main.line_type, *option)
        parent.lb_pack(drop_down)
        parent.lb_pack(frm_type)

        


#types of lines to draw
class Line():
    #intitialize
    def __init__(self):
        print('line')
class Rectangle():
    #intitialize
    def __init__(self):
        print('line')
class Oval():
    #intitialize
    def __init__(self):
        print('line')
class Polygon():
    #intitialize
    def __init__(self):
        print('line')

#run the program
if __name__ == '__main__':
    w = window()
    w.mainloop()