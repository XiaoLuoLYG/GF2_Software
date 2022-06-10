
"""

Implement the graphical user interface for the Logic Simulator.
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
import sys

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

        # GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        # GL.glBegin(GL.GL_LINE_STRIP)
        # for i in range(10):
        #    x = (i * 20) + 10
        #    x_next = (i * 20) + 30
        #    if i % 2 == 0:
        #        y = 75
        #    else:
        #        y = 100
        #    GL.glVertex2f(x, y)
        #    GL.glVertex2f(x_next, y)
        # GL.glEnd()

        # Draw signal simulation

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

    # run simulation
    def run(self, num, reset=False):
        size = self.GetClientSize()
        if reset:
            self.monitors.reset_monitors()
            self.colours = []
            for i in range(len(self.monitors.monitors_dictionary)):
                self.colours.append(
                    (random.uniform(0, 0.9),
                     random.uniform(0, 0.9), random.uniform(0, 0.9)))

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
    def __init__(self,parent,names, devices, network, monitors):
        scrolled.ScrolledPanel.__init__(self,parent,size=(200,130))

        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network

        self.monitors.get_signal_names()

        listofswitches = []
        for i in self.devices.devices_list:
            if i.device_kind == 7:
                listofswitches.append(self.names.get_name_string(i.device_id))

        sizer = wx.BoxSizer(wx.VERTICAL)
        global label
        label = []
        global button
        button = []
        for n in range(len(listofswitches)):
            a = str(n+1)
            a = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(a,0, wx.ALL, 5)
            setattr(self, "button%s" % str(n+1), 
                    wx.ToggleButton(self,label = listofswitches[n]))
            btn = getattr(self, "button%s" % str(n+1))
            btn.Bind(wx.EVT_TOGGLEBUTTON, self.onToggleClick)
            setattr(self, "label%s" % str(n+1),
                    wx.StaticText(self,label = "On"))
            lbl = getattr(self, "label%s" % str(n+1))
            label.append(lbl) 
            button.append(btn)
            a.Add(lbl, 1, wx.TOP, 10)
            a.Add(btn, 1, wx.TOP, 10)
        
        self.SetSizer(sizer)
        self.SetupScrolling()

    def onToggleClick(self, event):
        state = event.GetEventObject().GetValue()
        b=event.GetEventObject()
        c=event.GetEventObject().GetLabel()
        print(label)
        print(button)
        if state == True:
            thebutton = event.GetEventObject()
            order = "s"+" "+thebutton.GetLabel()+" "+"0"
            print(order)
            self.command_interface(event, order)
            print(thebutton.GetName())
            thelabel = label[button.index(b)]
            thelabel.SetLabel("Off")

        else:
            thebutton = event.GetEventObject()
            order = "s"+" "+thebutton.GetLabel()+" "+"1"
            print(order)
            self.command_interface(event, order)
            print(thebutton.GetName())
            thelabel = label[button.index(b)]
            thelabel.SetLabel("On")

    def command_interface(self, event, order):
        """Read the command entered and call the corresponding function."""
        #print("Logic Simulator: interactive command line user interface.\n"
        #      "Enter 'h' for help.")
        #print(self.devices.find_devices(self.devices.SWITCH))
        #print(self.monitors.get_signal_names())
        self.cycles_completed = 0  # number of simulation cycles completed

        self.character = ""  # current character
        self.line = ""  # current string entered by the user
        self.cursor = 0  # cursor position
        
        self.get_line(order)  # get the user entry
        command = self.read_command()  # read the first character
        
        #gui = Gui("Logic Simulator", path, names, devices, network,
                      #monitors)

        if command == "q":
            dlg = wx.MessageDialog(self,"Are you sure you want to exit?","Confirm exit",wx.CANCEL | wx.OK)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_CANCEL:
                print("The user cancelled")
            if result == wx.ID_OK:
                self.Close(True)
        if command == "h":
            self.help_command()
        elif command == "s":
            self.switch_command()
        elif command == "m":
            self.monitor_command()
        elif command == "z":
            self.zap_command()
        elif command == "r":
            self.run_command()
        elif command == "c":
            self.continue_command()
        else:
            print("Invalid command. Enter 'h' for help.")

        del self.line

    def get_line(self,order):
        """Print prompt for the user and update the user entry."""
        #self.cursor = 0
        #self.line = input("#: ")
        #while self.line == "":  # if the user enters a blank line
            #self.line = input("#: ")
        self.line = order

    def read_command(self):
        """Return the first non-whitespace character."""
        self.skip_spaces()
        return self.character
        #del self.character 

    def get_character(self):
        """Move the cursor forward by one character in the user entry."""
        if self.cursor < len(self.line):
            self.character = self.line[self.cursor]
            self.cursor += 1
        else:  # end of the line
            self.character = ""

    def skip_spaces(self):
        """Skip whitespace until a non-whitespace character is reached."""
        self.get_character()
        while self.character.isspace():
            self.get_character()

    def read_string(self):
        """Return the next alphanumeric string."""
        self.skip_spaces()
        name_string = ""
        if not self.character.isalpha():  # the string must start with a letter
            print("Error! Expected a name.")
            return None
        while self.character.isalnum():
            name_string = "".join([name_string, self.character])
            self.get_character()
        return name_string

    def read_name(self):
        """Return the name ID of the current string if valid.

        Return None if the current string is not a valid name string.
        """
        name_string = self.read_string()
        if name_string is None:
            return None
        else:
            name_id = self.names.query(name_string)
        if name_id is None:
            print("Error! Unknown name.")
        return name_id

    def read_signal_name(self):
        """Return the device and port IDs of the current signal name.

        Return None if either is invalid.
        """
        device_id = self.read_name()
        if device_id is None:
            return None
        elif self.character == ".":
            port_id = self.read_name()
            if port_id is None:
                return None
        else:
            port_id = None
        return [device_id, port_id]

    def read_number(self, lower_bound, upper_bound):
        """Return the current number.

        Return None if no number is provided or if it falls outside the valid
        range.
        """
        self.skip_spaces()
        number_string = ""
        if not self.character.isdigit():
            print("Error! Expected a number.")
            return None
        while self.character.isdigit():
            number_string = "".join([number_string, self.character])
            self.get_character()
        number = int(number_string)

        if upper_bound is not None:
            if number > upper_bound:
                print("Number out of range.")
                return None

        if lower_bound is not None:
            if number < lower_bound:
                print("Number out of range.")
                return None

        return number

    def switch_command(self):
        """Set the specified switch to the specified signal level."""
        switch_id = self.read_name()
        if switch_id is not None:
            switch_state = self.read_number(0, 1)
            if switch_state is not None:
                if self.devices.set_switch(switch_id, switch_state):
                    print("Successfully set switch.")
                else:
                    print("Error! Invalid switch.")

    def monitor_command(self):
        """Set the specified monitor."""
        monitor = self.read_signal_name()
        if monitor is not None:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                print("Successfully made monitor.")
            else:
                print("Error! Could not make monitor.")

    def zap_command(self):
        """Remove the specified monitor."""
        monitor = self.read_signal_name()
        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                print("Successfully zapped monitor")
            else:
                print("Error! Could not zap monitor.")

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                return False
        self.monitors.display_signals()
        return True

    def run_command(self):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        cycles = self.read_number(0, None)

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles

    def continue_command(self):
        """Continue a previously run simulation."""
        cycles = self.read_number(0, None)
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                print("Error! Nothing to continue. Run first.")
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                print(" ".join(["Continuing for", str(cycles), "cycles.",
                                "Total:", str(self.cycles_completed)]))

class scrolledpanel2(scrolled.ScrolledPanel):
    """Configures the scrolled panel on the left to hold all switches"""
    def __init__(self,parent,names, devices, network, monitors):
        scrolled.ScrolledPanel.__init__(self,parent,size=(200,130))

        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network

        listofmonitors = []
        for (device_id, output_id), value in self.monitors.monitors_dictionary.items():

            listofmonitors.append(self.devices.get_signal_name(
                device_id, output_id))

        sizer = wx.BoxSizer(wx.VERTICAL)

        for n in range(len(listofmonitors)):
            a = str(n+1)
            b = 'button' + str(n+1)
            c = 'label' + str(n+1)
            a = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(a,0, wx.ALL, 5)
            self.c = wx.StaticText(self, label = listofmonitors[n])
            self.a = wx.ToggleButton(self,label = listofmonitors[n])
            self.a.Bind(wx.EVT_TOGGLEBUTTON, self.onToggleClick)
            a.Add(self.c,1, wx.TOP, 10)
            a.Add(self.a,1, wx.TOP, 10)

        self.SetSizer(sizer)
        self.SetupScrolling()

    def onToggleClick(self, event):
        state = event.GetEventObject().GetValue()

        if state == True:
            button = event.GetEventObject()
            order = "z"+" "+button.GetLabel()
            print(order)
            self.command_interface(event, order)

        else:
            button = event.GetEventObject()
            order = "m"+" "+button.GetLabel()
            print(order)
            self.command_interface(event, order)

    def command_interface(self, event, order):
        """Read the command entered and call the corresponding function."""
        #print("Logic Simulator: interactive command line user interface.\n"
        #      "Enter 'h' for help.")
        #print(self.devices.find_devices(self.devices.SWITCH))
        #print(self.monitors.get_signal_names())
        self.cycles_completed = 0  # number of simulation cycles completed

        self.character = ""  # current character
        self.line = ""  # current string entered by the user
        self.cursor = 0  # cursor position
        
        self.get_line(order)  # get the user entry
        command = self.read_command()  # read the first character
        
        #gui = Gui("Logic Simulator", path, names, devices, network,
                      #monitors)

        if command == "q":
            dlg = wx.MessageDialog(self,"Are you sure you want to exit?","Confirm exit",wx.CANCEL | wx.OK)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_CANCEL:
                print("The user cancelled")
            if result == wx.ID_OK:
                self.Close(True)
        if command == "h":
            self.help_command()
        elif command == "s":
            self.switch_command()
        elif command == "m":
            self.monitor_command()
        elif command == "z":
            self.zap_command()
        elif command == "r":
            self.run_command()
        elif command == "c":
            self.continue_command()
        else:
            print("Invalid command. Enter 'h' for help.")

        del self.line

    def get_line(self,order):
        """Print prompt for the user and update the user entry."""
        #self.cursor = 0
        #self.line = input("#: ")
        #while self.line == "":  # if the user enters a blank line
            #self.line = input("#: ")
        self.line = order

    def read_command(self):
        """Return the first non-whitespace character."""
        self.skip_spaces()
        return self.character
        #del self.character 

    def get_character(self):
        """Move the cursor forward by one character in the user entry."""
        if self.cursor < len(self.line):
            self.character = self.line[self.cursor]
            self.cursor += 1
        else:  # end of the line
            self.character = ""

    def skip_spaces(self):
        """Skip whitespace until a non-whitespace character is reached."""
        self.get_character()
        while self.character.isspace():
            self.get_character()

    def read_string(self):
        """Return the next alphanumeric string."""
        self.skip_spaces()
        name_string = ""
        if not self.character.isalpha():  # the string must start with a letter
            print("Error! Expected a name.")
            return None
        while self.character.isalnum():
            name_string = "".join([name_string, self.character])
            self.get_character()
        return name_string

    def read_name(self):
        """Return the name ID of the current string if valid.

        Return None if the current string is not a valid name string.
        """
        name_string = self.read_string()
        if name_string is None:
            return None
        else:
            name_id = self.names.query(name_string)
        if name_id is None:
            print("Error! Unknown name.")
        return name_id

    def read_signal_name(self):
        """Return the device and port IDs of the current signal name.

        Return None if either is invalid.
        """
        device_id = self.read_name()
        if device_id is None:
            return None
        elif self.character == ".":
            port_id = self.read_name()
            if port_id is None:
                return None
        else:
            port_id = None
        return [device_id, port_id]

    def read_number(self, lower_bound, upper_bound):
        """Return the current number.

        Return None if no number is provided or if it falls outside the valid
        range.
        """
        self.skip_spaces()
        number_string = ""
        if not self.character.isdigit():
            print("Error! Expected a number.")
            return None
        while self.character.isdigit():
            number_string = "".join([number_string, self.character])
            self.get_character()
        number = int(number_string)

        if upper_bound is not None:
            if number > upper_bound:
                print("Number out of range.")
                return None

        if lower_bound is not None:
            if number < lower_bound:
                print("Number out of range.")
                return None

        return number

    def switch_command(self):
        """Set the specified switch to the specified signal level."""
        switch_id = self.read_name()
        if switch_id is not None:
            switch_state = self.read_number(0, 1)
            if switch_state is not None:
                if self.devices.set_switch(switch_id, switch_state):
                    print("Successfully set switch.")
                else:
                    print("Error! Invalid switch.")

    def monitor_command(self):
        """Set the specified monitor."""
        monitor = self.read_signal_name()
        if monitor is not None:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                print("Successfully made monitor.")
            else:
                print("Error! Could not make monitor.")

    def zap_command(self):
        """Remove the specified monitor."""
        monitor = self.read_signal_name()
        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                print("Successfully zapped monitor")
            else:
                print("Error! Could not zap monitor.")

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                return False
        self.monitors.display_signals()
        return True

    def run_command(self):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        cycles = self.read_number(0, None)

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles

    def continue_command(self):
        """Continue a previously run simulation."""
        cycles = self.read_number(0, None)
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                print("Error! Nothing to continue. Run first.")
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                print(" ".join(["Continuing for", str(cycles), "cycles.",
                                "Total:", str(self.cycles_completed)]))
                
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

        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network
        self.locale = wx.Locale()

        self.cycles_completed = 0  # number of simulation cycles completed

        self.character = ""  # current character
        self.line = ""  # current string entered by the user
        self.cursor = 0  # cursor position
        
        wx.Locale.AddCatalogLookupPathPrefix('locale')
        if self.locale:
            assert sys.getrefcount(self.locale) <= 2
            del self.locale

        self.locale = wx.Locale(wx.LANGUAGE_CHINESE_SIMPLIFIED)
        if self.locale.IsOk():
            self.locale.AddCatalog("zh_CN")
        else:
            self.locale = None
        
        #get list of devices and their outputs if they have any
        listofoutputs = []
        for i in self.devices.devices_list:
            for output_id in i.outputs:
                if output_id == None:
                    listofoutputs.append(self.names.get_name_string(i.device_id))
                    if i.outputs[output_id] != 0:
                        print(self.names.get_name_string(i.outputs[output_id]))
                else:
                    deviceandoutput = self.names.get_name_string(i.device_id)+"."+self.names.get_name_string(output_id)
                    listofoutputs.append(deviceandoutput)

        listofinputs = []
        for i in self.devices.devices_list:
            for input_id in i.inputs:
                device = (self.names.get_name_string(i.device_id))
                inputs = self.names.get_name_string(input_id)
                deviceandinputs = device+"."+inputs
                listofinputs.append(deviceandinputs)

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
        self.canvas.run(10,True)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles:")
        font = wx.Font(10,wx.DECORATIVE, wx.NORMAL, wx.BOLD, True)
        self.text.SetFont(font)
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.text2 = wx.StaticText(self, wx.ID_ANY, "Text based control:")
        self.text2.SetFont(font)
        self.text_box_command = wx.TextCtrl(self, wx.ID_ANY, "",style=wx.TE_PROCESS_ENTER) 
        self.text_box_command.SetHint('Type function here')
        self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        self.clear_button = wx.Button(self, wx.ID_ANY, "Clear Text Box")
        self.text3 = wx.StaticText(self, wx.ID_ANY, "Switches:")
        self.text3.SetFont(font)
        self.text4 = wx.StaticText(self, wx.ID_ANY, "Monitors:")
        self.text4.SetFont(font)
        self.text5 = wx.StaticText(self, wx.ID_ANY, "Connections:")
        self.text5.SetFont(font)
        self.combo1 = wx.ComboBox(self, choices = listofoutputs, style = wx.CB_READONLY)
        self.combo2 = wx.ComboBox(self, choices = listofinputs, style = wx.CB_READONLY)
        self.text6 = wx.StaticText(self, wx.ID_ANY, "connect")
        self.break_connect_button = wx.Button(self, wx.ID_ANY, "Break Connection")
        self.connect_button = wx.Button(self, wx.ID_ANY, "Connect")
        self.text7 = wx.StaticText(self, wx.ID_ANY, "Command buttons:")
        self.text7.SetFont(font)
        
        # Bind events to widgets                #this assigns the functions interacting with the widgets will actually do
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.text_box_command.Bind(wx.EVT_TEXT_ENTER, self.command_interface)
        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear_button)
        self.combo1.Bind(wx.EVT_COMBOBOX,self.on_combo)
        self.combo2.Bind(wx.EVT_COMBOBOX,self.on_combo)
        self.break_connect_button.Bind(wx.EVT_BUTTON, self.on_break_connect_button)
        self.connect_button.Bind(wx.EVT_BUTTON, self.on_connect_button)
        
        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)     
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        bottom_sizer = wx.BoxSizer()
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        combo_sizer = wx.BoxSizer(wx.HORIZONTAL)
        combo_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
          
        main_sizer.Add(left_sizer, 0, wx.ALL, 5)                       
        main_sizer.Add(right_sizer, 5, wx.EXPAND|wx.ALL, 5) 
        right_sizer.Add(self.canvas, 10, wx.EXPAND | wx.ALL, 5)
        right_sizer.Add(bottom_sizer,5, wx.EXPAND | wx.ALL, 5)
        combo_sizer.Add(self.combo1,1,wx.ALL,1)
        combo_sizer.Add(self.text6, 1, wx.ALL, 1)
        combo_sizer.Add(self.combo2,1,wx.ALL,1)
        combo_sizer2.Add(self.break_connect_button) 
        combo_sizer2.Add(self.connect_button)                      
        
        left_sizer.Add(self.text, 1, wx.TOP, 1)
        left_sizer.Add(self.spin, 1, wx.ALL, 1)
        left_sizer.Add(self.text2, 1, wx.TOP, 5)
        left_sizer.Add(self.text_box_command, 1, wx.ALL, 1)
        left_sizer.Add(self.text3, 1, wx.TOP, 5)
        left_sizer.Add(scrolledpanel(self, names, devices, network, monitors))
        left_sizer.Add(self.text4, 1, wx.TOP, 5)
        left_sizer.Add(scrolledpanel2(self, names, devices, network, monitors))
        left_sizer.Add(self.text5, 1, wx.TOP, 5)
        left_sizer.Add(combo_sizer, 1, wx.ALL,1)
        left_sizer.Add(combo_sizer2, 1, wx.ALL,1)
        left_sizer.Add(self.text7, 1, wx.TOP, 5)
        left_sizer.Add(self.clear_button, 1, wx.ALL, 1)
        left_sizer.Add(self.run_button, 1, wx.ALL, 1)
        left_sizer.Add(self.continue_button, 1, wx.ALL, 1)
        bottom_sizer.Add(self.text_box,1, wx.EXPAND|wx.ALL, 5)          

        self.SetSizeHints(800, 800)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()                                               
        if Id == wx.ID_EXIT:
            dlg = wx.MessageDialog(self,"Are you sure you want to exit?","Confirm exit",wx.CANCEL | wx.OK)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_CANCEL:
                print("The user cancelled")
            if result == wx.ID_OK:
                self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Team 20\n2022",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_OPEN:
            self.on_open(True)
        if Id == wx.ID_HELP:
            self.text_box.WriteText(str(UserInterface.help_command(self)))
            self.text_box.WriteText("\n\n")

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)
        return(spin_value)

    def command_interface_order(self, event, order):
        """Read the command entered and call the corresponding function."""
        #print("Logic Simulator: interactive command line user interface.\n"
        #      "Enter 'h' for help.")
        #print(self.devices.find_devices(self.devices.SWITCH))
        #print(self.monitors.get_signal_names())
        # number of simulation cycles completed

        self.character = ""  # current character
        self.line = ""  # current string entered by the user
        self.cursor = 0  # cursor position

        self.get_line_order(order)  # get the user entry
        command = self.read_command()  # read the first character
        if command == "r":
            self.run_command()
            
        elif command == "c":
            self.continue_command()
            
        else:
            print("Invalid command. Enter 'h' for help.")
            

        del self.line

    def get_line_order(self, order):
        """Print prompt for the user and update the user entry."""
        self.line = order  

    def on_continue_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Continue button pressed." + str(self.on_spin(event))
        self.canvas.render(text)
        order = "c"+""+str(self.on_spin(event))
        self.command_interface_order(event, order)
        

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed." + str(self.on_spin(event))
        self.canvas.render(text)
        order = "r"+""+str(self.on_spin(event))
        self.command_interface_order(event, order)
        # self.canvas.run(int(str(self.on_spin(event))),True)

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
    
    def on_combo(self, event):
        "Handle the event the user chooses something from the drop down"
        on_combo_value = self.combo1.GetValue()

    def on_break_connect_button(self, event):
        on_combo_value = self.combo1.GetValue()
        on_combo_value2 = self.combo2.GetValue()
        print("break", " ", on_combo_value, " ", "and", " ", on_combo_value2)

        first_device = on_combo_value.split('.')[0]
        if len(on_combo_value.split('.')) == 1: 
            first_port = None
        else:
            first_port = on_combo_value.split('.')[1]
        second_device = on_combo_value2.split('.')[0]
        second_port = on_combo_value2.split('.')[1]

        first_device_id = self.names.query(first_device)
        if first_port != None:
            first_port_id = self.names.query(first_port)
        else:
            first_port_id = None
        second_device_id = self.names.query(second_device)
        second_port_id = self.names.query(second_port)

        self.network.break_connection(first_device_id, first_port_id, second_device_id, second_port_id)

        first_device1 = self.devices.get_device(first_device_id)
        second_device2 = self.devices.get_device(second_device_id)

        print(second_device2.inputs)
        print("break done")
        
    def on_connect_button(self, event):
        on_combo_value = self.combo1.GetValue()
        on_combo_value2 = self.combo2.GetValue()
        print("connect", " ", on_combo_value, " ", "and", " ", on_combo_value2)

        #grab ids of everything in the comboboxes 
        #first_device_id, first_port_id, second_device_id, second_port_id
        first_device = on_combo_value.split('.')[0]
        if len(on_combo_value.split('.')) == 1: 
            first_port = None
        else:
            first_port = on_combo_value.split('.')[1]
        second_device = on_combo_value2.split('.')[0]
        second_port = on_combo_value2.split('.')[1]

        first_device_id = self.names.query(first_device)
        if first_port != None:
            first_port_id = self.names.query(first_port)
        else:
            first_port_id = None
        second_device_id = self.names.query(second_device)
        second_port_id = self.names.query(second_port)

        print(first_device_id, first_port_id, second_device_id, second_port_id)
        
        self.network.make_connection(first_device_id, first_port_id, second_device_id, second_port_id)

        first_device1 = self.devices.get_device(first_device_id)
        second_device2 = self.devices.get_device(second_device_id)

        print(second_device2.inputs)
        print("connect done")

#--------userint functions:---------
    def command_interface(self, event):
        """Read the command entered and call the corresponding function."""
        #print("Logic Simulator: interactive command line user interface.\n"
        #      "Enter 'h' for help.")
        #print(self.devices.find_devices(self.devices.SWITCH))
        #print(self.monitors.get_signal_names())
        self.cycles_completed = 0  # number of simulation cycles completed

        self.character = ""  # current character
        self.line = ""  # current string entered by the user
        self.cursor = 0  # cursor position

        self.get_line()  # get the user entry
        command = self.read_command()  # read the first character
        if command == "q":
            dlg = wx.MessageDialog(self,"Are you sure you want to exit?","Confirm exit",wx.CANCEL | wx.OK)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_CANCEL:
                print("The user cancelled")
            if result == wx.ID_OK:
                self.Close(True)
        if command == "h":
            self.help_command()
            self.text_box_command.SetValue("")
        elif command == "s":
            self.switch_command()
            self.text_box_command.SetValue("")
        elif command == "m":
            self.monitor_command()
            self.text_box_command.SetValue("")
        elif command == "z":
            self.zap_command()
            self.text_box_command.SetValue("")
        elif command == "r":
            self.run_command()
            self.text_box_command.SetValue("")
        elif command == "c":
            self.continue_command()
            self.text_box_command.SetValue("")
        else:
            print("Invalid command. Enter 'h' for help.")
            self.text_box_command.SetValue("")

        del self.line

    def get_line(self):
        """Print prompt for the user and update the user entry."""
        #self.cursor = 0
        #self.line = input("#: ")
        #while self.line == "":  # if the user enters a blank line
            #self.line = input("#: ")
        self.line = self.text_box_command.GetValue()  
        while self.line == "": 
            pass

    def read_command(self):
        """Return the first non-whitespace character."""
        self.skip_spaces()
        return self.character
        #del self.character 

    def get_character(self):
        """Move the cursor forward by one character in the user entry."""
        if self.cursor < len(self.line):
            self.character = self.line[self.cursor]
            self.cursor += 1
        else:  # end of the line
            self.character = ""

    def skip_spaces(self):
        """Skip whitespace until a non-whitespace character is reached."""
        self.get_character()
        while self.character.isspace():
            self.get_character()

    def read_string(self):
        """Return the next alphanumeric string."""
        self.skip_spaces()
        name_string = ""
        if not self.character.isalpha():  # the string must start with a letter
            print("Error! Expected a name.")
            return None
        while self.character.isalnum():
            name_string = "".join([name_string, self.character])
            self.get_character()
        return name_string

    def read_name(self):
        """Return the name ID of the current string if valid.

        Return None if the current string is not a valid name string.
        """
        name_string = self.read_string()
        if name_string is None:
            return None
        else:
            name_id = self.names.query(name_string)
        if name_id is None:
            print("Error! Unknown name.")
        return name_id

    def read_signal_name(self):
        """Return the device and port IDs of the current signal name.

        Return None if either is invalid.
        """
        device_id = self.read_name()
        if device_id is None:
            return None
        elif self.character == ".":
            port_id = self.read_name()
            if port_id is None:
                return None
        else:
            port_id = None
        return [device_id, port_id]

    def read_number(self, lower_bound, upper_bound):
        """Return the current number.

        Return None if no number is provided or if it falls outside the valid
        range.
        """
        self.skip_spaces()
        number_string = ""
        if not self.character.isdigit():
            print("Error! Expected a number.")
            return None
        while self.character.isdigit():
            number_string = "".join([number_string, self.character])
            self.get_character()
        number = int(number_string)

        if upper_bound is not None:
            if number > upper_bound:
                print("Number out of range.")
                return None

        if lower_bound is not None:
            if number < lower_bound:
                print("Number out of range.")
                return None

        return number

    def help_command(self):
        """Print a list of valid commands."""
        print("User commands:")
        print("r N       - run the simulation for N cycles")
        print("c N       - continue the simulation for N cycles")
        print("s X N     - set switch X to N (0 or 1)")
        print("m X       - set a monitor on signal X")
        print("z X       - zap the monitor on signal X")
        print("h         - help (this command)")
        print("q         - quit the program")
        #return("User commands:\nr N       - run the simulation for N cycles\nc N       - continue the simulation for N cycles\ns X N     - set switch X to N (0 or 1)\nm X       - set a monitor on signal X\nz X       - zap the monitor on signal X\nh         - help (this command)\nq         - quit the program")

    def switch_command(self):
        """Set the specified switch to the specified signal level."""
        switch_id = self.read_name()
        if switch_id is not None:
            switch_state = self.read_number(0, 1)
            if switch_state is not None:
                if self.devices.set_switch(switch_id, switch_state):
                    print("Successfully set switch.")
                else:
                    print("Error! Invalid switch.")

    def monitor_command(self):
        """Set the specified monitor."""
        monitor = self.read_signal_name()
        if monitor is not None:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                print("Successfully made monitor.")
            else:
                print("Error! Could not make monitor.")

    def zap_command(self):
        """Remove the specified monitor."""
        monitor = self.read_signal_name()
        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                print("Successfully zapped monitor")
            else:
                print("Error! Could not zap monitor.")

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                return False
        self.monitors.display_signals()
        return True

    def run_command(self):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        cycles = self.read_number(0, None)

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            # if self.run_network(cycles):
            self.cycles_completed += cycles
            self.canvas.run(cycles, True)

    def continue_command(self):
        """Continue a previously run simulation."""
        cycles = self.read_number(0, None)
        
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                print("Error! Nothing to continue. Run first.")
            # elif self.run_network(cycles):
            else:
                self.cycles_completed += cycles
                print(" ".join(["Continuing for", str(cycles), "cycles.",
                                "Total:", str(self.cycles_completed)]))
                self.canvas.run(cycles)
        