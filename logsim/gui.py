"""Implement the graphical user interface for the Logic Simulator.
Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import os
import wx
import wx.lib.scrolledpanel as scrolled
import wx.glcanvas as wxcanvas
import random
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface

class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors, network):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        self.scale_x = 50
        self.scale_y = 50

        # Initialise variables for zooming
        self.zoom = 1

        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.signals = []
        self.colours = []

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.max_x = -size.width
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        size = self.GetClientSize()
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a sample signal trace
        
        #GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        #GL.glBegin(GL.GL_LINE_STRIP)
        #for i in range(10):
        #    x = (i * 20) + 10
        #    x_next = (i * 20) + 30
        #    if i % 2 == 0:
        #        y = 75
        #    else:
        #        y = 100
        #    GL.glVertex2f(x, y)
        #    GL.glVertex2f(x_next, y)
        #GL.glEnd()
        
        #Draw signal simulation

        if len(self.signals) > 0:
            # ruler
            for i in range(0, len(self.signals[0][-1])):
                GL.glColor3f(0, 0, 0)
                self.render_text(str(i), 100 + i*self.scale_x,
                                 size.height - 30)
                GL.glColor3f(0.8, 0.8, 0.8)
                GL.glLineWidth(1.0)
                GL.glBegin(GL.GL_LINES)
                GL.glVertex2f(100 + i*self.scale_x, size.height - 40)
                GL.glVertex2f(100 + i*self.scale_x, 0)
                GL.glEnd()

            # signal
            count = 1
            for sig in self.signals:
                GL.glColor3f(sig[1][0], sig[1][1], sig[1][2])
                GL.glLineWidth(3.0)
                self.draw_signal(
                    sig[-1], (100, size.height - count*2*self.scale_y))

                GL.glClearColor(1.0, 1.0, 1.0, 0.0)
                self.render_text(
                    sig[0], 50, size.height - count*2*self.scale_y)
                count += 1

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def draw_signal(self, signal, offset):
        self.max_x = self.scale_x * (len(signal)-1)

        GL.glBegin(GL.GL_LINE_STRIP)
        for i, val in enumerate(signal):
            if val == 1:
                GL.glVertex2f(offset[0]+i*self.scale_x, offset[1])
            else:
                GL.glVertex2f(offset[0]+i*self.scale_x, offset[1]+self.scale_y)

            try:
                next_val = (1-signal[i+1]) * self.scale_y
                GL.glVertex2f(offset[0]+i*self.scale_x, offset[1] + next_val)
            except IndexError:
                pass

        GL.glEnd()
        return

    #run simulation
    def run(self, num):
        size = self.GetClientSize()
        
        self.monitors.reset_monitors()
        self.colours = []
        for i in range(len(self.monitors.monitors_dictionary)):
            self.colours.append(
                (random.uniform(0, 0.9), random.uniform(0, 0.9), random.uniform(0, 0.9)))

        for _ in range(num):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print(("Error! Network oscillating."))

        self.monitors.display_signals()
        self.signals = []

        count = 0
        for (device_id, output_id), value in self.monitors.monitors_dictionary.items():

            monitor_name = self.devices.get_signal_name(
                device_id, output_id)
            self.signals.append(
                [monitor_name, self.colours[count], value])
            count += 1

        try:
            self.render("")
        except wx._core.wxAssertionError:
            pass


class scrolledpanel(scrolled.ScrolledPanel):
    """Configures the scrolled panel on the left to hold all switches"""
    def __init__(self,parent):
        scrolled.ScrolledPanel.__init__(self,parent,size=(200,170))

        self.label1 = wx.StaticText(self, label = "Switch 1")
        self.label2 = wx.StaticText(self, label = "Switch 2")
        self.label3 = wx.StaticText(self, label = "Switch 3")
        self.label4 = wx.StaticText(self, label = "Switch 4")
        self.label5 = wx.StaticText(self, label = "Switch 5")
        self.label6 = wx.StaticText(self, label = "Switch 6")
        self.label7 = wx.StaticText(self, label = "Switch 7")

        self.button1 = wx.ToggleButton(self,label = "On 1")
        self.button2 = wx.ToggleButton(self,label = "On 1")
        self.button3 = wx.ToggleButton(self,label = "On 1")
        self.button4 = wx.ToggleButton(self,label = "On 1")
        self.button5 = wx.ToggleButton(self,label = "On 1")
        self.button6 = wx.ToggleButton(self,label = "On 1")
        self.button7 = wx.ToggleButton(self,label = "On 1")

        self.button1.Bind(wx.EVT_TOGGLEBUTTON, self.onToggleClick)
        self.button2.Bind(wx.EVT_TOGGLEBUTTON, self.onToggleClick)
        self.button3.Bind(wx.EVT_TOGGLEBUTTON, self.onToggleClick)
        self.button4.Bind(wx.EVT_TOGGLEBUTTON, self.onToggleClick)
        self.button5.Bind(wx.EVT_TOGGLEBUTTON, self.onToggleClick)
        self.button6.Bind(wx.EVT_TOGGLEBUTTON, self.onToggleClick)
        self.button7.Bind(wx.EVT_TOGGLEBUTTON, self.onToggleClick)

        sizer = wx.BoxSizer(wx.VERTICAL)
        firstsizer = wx.BoxSizer(wx.HORIZONTAL)
        secondsizer = wx.BoxSizer(wx.HORIZONTAL)
        thirdsizer = wx.BoxSizer(wx.HORIZONTAL)
        fourthsizer = wx.BoxSizer(wx.HORIZONTAL)
        fifthsizer = wx.BoxSizer(wx.HORIZONTAL)
        sixthsizer = wx.BoxSizer(wx.HORIZONTAL)
        seventhsizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(firstsizer,0, wx.ALL, 5)
        sizer.Add(secondsizer,0, wx.ALL, 5)
        sizer.Add(thirdsizer,0, wx.ALL, 5)
        sizer.Add(fourthsizer,0, wx.ALL, 5)
        sizer.Add(fifthsizer,0, wx.ALL, 5)
        sizer.Add(sixthsizer,0, wx.ALL, 5)
        sizer.Add(seventhsizer,0, wx.ALL, 5)

        firstsizer.Add(self.label1, 1, wx.TOP, 10)
        firstsizer.Add(self.button1, 1, wx.TOP, 10)
        secondsizer.Add(self.label2, 1, wx.TOP, 10)
        secondsizer.Add(self.button2, 1, wx.TOP, 10)
        thirdsizer.Add(self.label3, 1, wx.TOP, 10)
        thirdsizer.Add(self.button3, 1, wx.TOP, 10)
        fourthsizer.Add(self.label4, 1, wx.TOP, 10)
        fourthsizer.Add(self.button4, 1, wx.TOP, 10)
        fifthsizer.Add(self.label5, 1, wx.TOP, 10)
        fifthsizer.Add(self.button5, 1, wx.TOP, 10)
        sixthsizer.Add(self.label6, 1, wx.TOP, 10)
        sixthsizer.Add(self.button6, 1, wx.TOP, 10)
        seventhsizer.Add(self.label7, 1, wx.TOP, 10)
        seventhsizer.Add(self.button7, 1, wx.TOP, 10)

        self.SetSizer(sizer)
        self.SetupScrolling()

    def onToggleClick(self, event):
        state = event.GetEventObject().GetValue()

        if state == True:
            #self.Label.SetLabel("Off")
            event.GetEventObject().SetLabel("Off 0")

        else:
            #self.label.SetLabelText("On")
            event.GetEventObject().SetLabel("On 1")

class scrolledpanel2(scrolled.ScrolledPanel):
    """Configures the scrolled panel on the left to hold all switches"""
    def __init__(self,parent):
        scrolled.ScrolledPanel.__init__(self,parent,size=(200,170))
        listofmonitors = ["A","B","C","D","E"]
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        for n in range(len(listofmonitors)):
            a = str(n+1)
            b = 'button' + str(n+1)
            c = 'label' + str(n+1)
            a = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(a,0, wx.ALL, 5)
            self.c = wx.StaticText(self, label = listofmonitors[n])
            self.a = wx.Button(self, wx.ID_ANY, label=b)
            a.Add(self.c,1, wx.TOP, 10)
            a.Add(self.a,1, wx.TOP, 10)

        '''for n in range(len(listofmonitors)):
            a = 'button' + str(n)
            self.a = wx.Button(self, wx.ID_ANY, label=a)
            b = str(n)
            b.Add(self.a,1, wx.TOP, 10)'''
            
            #self.n = wx.StaticText(self, wx.ID_ANY, "Cycles:")

        '''for n in range(len(listofmonitors)):
            a = str(n)
            sizer.Add(self.a,0, wx.ALL, 5)'''

        self.SetSizer(sizer)
        self.SetupScrolling()

    def makeSizer(self,sizername):
        a = str(sizername)
        a_sizer = wx.BoxSizer(wx.HORIZONTAL)

    def onToggleClick(self, event):
        state = event.GetEventObject().GetValue()

        if state == True:
            #self.label.SetLabelText("Off")
            event.GetEventObject().SetLabel("Off 0")

        else:
            #self.label.SetLabeText("On")
            event.GetEventObject().SetLabel("On 1")

class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        #changing the initialisation parameters
        #self.SetBackgroundColour((100, 200, 100))

        # Configure the file menu
        fileMenu = wx.Menu()                       #this adds in a "menu" button
        menuBar = wx.MenuBar()                     #this adds in a menubar which displays buttons such as "file" and maybe "edit"
        fileMenu.Append(wx.ID_ABOUT, "&About")     #the ID is specified so when the "About" button is pressed, that ID is called
        fileMenu.Append(wx.ID_OPEN, "&Open File...") #what does the & do here?
        fileMenu.Append(wx.ID_HELP, "&Help")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors, network)
        self.canvas.run(10)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles:")
        font = wx.Font(10,wx.DECORATIVE, wx.NORMAL, wx.BOLD, True)
        self.text.SetFont(font)
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.text2 = wx.StaticText(self, wx.ID_ANY, "Text based control:")
        self.text2.SetFont(font)
        self.text_box_command = wx.TextCtrl(self, wx.ID_ANY, "",style=wx.TE_PROCESS_ENTER) 
        self.text_box_command.SetHint('Type function here')
        self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        self.clear_button = wx.Button(self, wx.ID_ANY, "clear")
        self.text3 = wx.StaticText(self, wx.ID_ANY, "Switches:")
        self.text3.SetFont(font)
        self.text4 = wx.StaticText(self, wx.ID_ANY, "Monitors:")
        self.text4.SetFont(font)
        
        # Bind events to widgets                #this assigns the functions interacting with the widgets will actually do
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.run_button.Disable()
        self.text_box_command.Bind(wx.EVT_TEXT_ENTER, self.on_text_box_command)
        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear_button)
        
        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)     
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        bottom_sizer = wx.BoxSizer()
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        #main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)  
        main_sizer.Add(left_sizer, 0, wx.ALL, 5)                       #the first number represents the proportion and the second the border
        main_sizer.Add(right_sizer, 5, wx.EXPAND|wx.ALL, 5) 
        right_sizer.Add(self.canvas, 10, wx.EXPAND | wx.ALL, 5)
        right_sizer.Add(bottom_sizer,5, wx.EXPAND | wx.ALL, 5)                      
        
        left_sizer.Add(self.text, 1, wx.TOP, 1)
        left_sizer.Add(self.spin, 1, wx.ALL, 1)
        left_sizer.Add(self.text2, 1, wx.TOP, 5)
        left_sizer.Add(self.text_box_command, 1, wx.ALL, 1)
        left_sizer.Add(self.text3, 1, wx.TOP, 5)
        left_sizer.Add(scrolledpanel(self))
        left_sizer.Add(self.text4, 1, wx.TOP, 5)
        left_sizer.Add(scrolledpanel2(self))
        left_sizer.Add(self.clear_button, 1, wx.ALL, 1)
        left_sizer.Add(self.run_button, 1, wx.ALL, 1)
        bottom_sizer.Add(self.text_box,1, wx.EXPAND|wx.ALL, 5)         #here changing the first number to 0 holds the width fixed and changing it to 1 allows it to stretch as window is resized

        self.SetSizeHints(800, 800)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()                                                 #now the event.GetId() simplies finds out which button was clicked
        if Id == wx.ID_EXIT:
            dlg = wx.MessageDialog(self,"Are you sure you want to exit?","Confirm exit",wx.CANCEL | wx.OK)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_CANCEL:
                print("The user cancelled")
            if result == wx.ID_OK:
                self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_OPEN:
            self.on_open(True)
        if Id == wx.ID_HELP:
            #a = str(UserInterface.help_command(self))
            self.text_box.WriteText(str(UserInterface.help_command(self)))
            self.text_box.WriteText("\n\n")

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.canvas.render(text)
        #Devices.make_switch(self, device_id, initial_state)

    def on_text_box_command(self, event):
        "Handle the event when the user enters text."
        text_box_command_value = self.text_box_command.GetValue()
        text = "".join(["New text box value: ", text_box_command_value])
        self.canvas.render(text)
        if text_box_command_value == "q":
            dlg = wx.MessageDialog(self,"Are you sure you want to exit?","Confirm exit",wx.CANCEL | wx.OK)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_CANCEL:
                print("The user cancelled")
            if result == wx.ID_OK:
                self.Close(True)
         

    def on_open(self, event):
        openFileDialog= wx.FileDialog(self, "Open txt file", "", "", wildcard="TXT files (*.txt)|*.txt", style=wx.FD_OPEN+wx.FD_FILE_MUST_EXIST)

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            print("The user cancelled") 
            return     # the user changed idea...
        print("File chosen=",openFileDialog.GetPath())
        
        path = openFileDialog.GetPath()
        if os.path.exists(path):
            with open(path) as fobj:
                for line in fobj:
                    self.text_box.WriteText(line)
            self.text_box.WriteText("\n\n")
            print(path)

    def on_clear_button(self, event):
        "Handle the event when the user clicks the clear button"
        self.text_box.SetValue("")
        text = "clear button pressed"
        self.canvas.render(text)

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        self.canvas.render(text)

