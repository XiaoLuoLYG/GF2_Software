"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


# from zmq import device
# from logsim.scanner import Scanner


class Parser:
    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.symbol = self.scanner.get_symbol()
        # error
        [self.NO_SECTIONS,
         self.NO_DEVICE_SECTION,
         self.NO_CONNECTION_SECTION,
         self.NO_MONITOR_SECTION,
         self.NO_LINKING_VERB,
         self.NO_SEMICOLON,
         self.NO_COMMA,
         self.NO_DOT,
         self.NO_CURLY_OPEN,
         self.NO_CURLY_CLOSE,
         self.NO_DEVICE,
         self.NO_NUM,
         self.NO_CONNECT_SYMBOL,
         self.INVALID_DEVICE_NAME,
         self.INVALID_DEVICE_TYPE,
         self.INVALID_PORT
         ] = self.names.unique_error_codes(16)

        self.error_dict = {
            # Sytanx error
            self.NO_SECTIONS: "Error: Expected a section.",
            self.NO_DEVICE_SECTION: "Error: Expected a device section",
            self.NO_CONNECTION_SECTION: "Error: Expected a connection section",
            self.NO_MONITOR_SECTION: "Error: Expected a monitor sectoin",
            self.NO_LINKING_VERB: "Error: Expected a linking verb",
            self.NO_SEMICOLON: "Error: Expected a ':'",
            self.NO_COMMA: "Error: Expected a ','",
            self.NO_DOT: "Error: Expected a '.'",
            self.NO_CURLY_OPEN: "Error: Expected a '{'",
            self.NO_CURLY_CLOSE: "Error: Expected a '}'",
            self.NO_DEVICE: "Error: Expected a device",
            self.NO_NUM: "Error: Expected a number",
            self.NO_CONNECT_SYMBOL: "Error: Expected a connect symbol",
            self.INVALID_DEVICE_NAME: "Error: Invalid device name",
            self.INVALID_DEVICE_TYPE: "Error: No such a device",
            self.INVALID_PORT: "Error: Invalid port",

            # Semantic errors
            network.INPUT_TO_INPUT: "Error: Both ports are inputs",
            network.OUTPUT_TO_OUTPUT: "Error: Both ports are outputs",
            network.INPUT_CONNECTED: "Error: Input is already in a connection",
            network.PORT_ABSENT: "Error: Second port is not a valid port",
            network.DEVICE_ABSENT: "Error: NO such a device",

            devices.INVALID_QUALIFIER: "Error: Invalid qualifier",
            devices.NO_QUALIFIER: "Error: No qualifier",
            devices.BAD_DEVICE: "Error: bad device",
            devices.QUALIFIER_PRESENT: "Error: Qualifier present",
            devices.DEVICE_PRESENT: "Error: Device present",
            monitors.NOT_OUTPUT: "Error: Not output",
            monitors.MONITOR_PRESENT: "Error: Monitor present",
            # devices.network.DEVICE_ABSENT: "Error: No such a device"
        }
        self.error_count = 0

        # # Used to check whether any sections are missed
        self.device_section = False
        self.connection_section = False
        self.monitor_section = False

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        while self.symbol.type != self.scanner.EOF:
            self.symbol = self.scanner.get_symbol()

            if self.symbol.type == self.scanner.KEYWORD:
                # Device
                if self.symbol.id == self.scanner.DEVICE_ID:
                    self.device_section = True
                    self.parse_sections('DEVICE')

                # Connection
                if self.symbol.id == self.scanner.CONNECTION_ID:
                    self.connection_section = True
                    self.parse_sections('CONNECTION')

                    # check whether we have the device section
                    if self.device_section:
                        continue
                    else:
                        self.display_error(self.NO_DEVICE_SECTION)
                        break

                # Monitor
                if self.symbol.id == self.scanner.MONITOR_ID:
                    self.monitor_section = True
                    self.parse_sections('MONITOR')
                    # check whether we have the connection section
                    if self.connection_section:
                        continue
                    else:
                        self.display_error(self.NO_CONNECTION_SECTION)
                        break

            else:
                self.display_error(self.NO_SECTIONS)
        # check whether we have the monitor section
        if not self.monitor_section:
            self.display_error(self.NO_MONITOR_SECTION)

        return True

    def parse_sections(self, KEYWORD):
        """Parse each section, including the device, the connection and the monitor."""
        # check the CURLY_OPEN
        while True:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.CURLY_OPEN:
                break

            elif self.symbol.type is None:
                continue

            else:
                self.display_error(self.NO_CURLY_OPEN)
                break
        # parse the section and check the CURLY_CLOSE
        while self.symbol.type != self.scanner.CURLY_CLOSE:

            if KEYWORD == 'DEVICE':
                self.parse_device()

            elif KEYWORD == 'CONNECTION':
                self.parse_connecction()

            elif KEYWORD == 'MONITOR':
                self.parse_monitor()

            elif self.symbol.type == self.scanner.EOF:
                self.display_error(self.NO_CURLY_CLOSE)
                break

    def parse_device(self):
        """Parse the device section."""
        # e.g A,B are OR with 2 inputs
        self.symbol = self.scanner.get_symbol()
        device_info = []
        if self.symbol.type == self.scanner.NAME:
            device_info.append(self.symbol.id)
            self.symbol = self.scanner.get_symbol()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type != self.scanner.NAME:
                    self.display_error(self.INVALID_DEVICE_NAME)
                    break
                else:
                    device_info.append(self.symbol.id)
                    self.symbol = self.scanner.get_symbol()
            #  is / are
            if self.symbol.type == self.scanner.KEYWORD:
                if (self.symbol.id == self.scanner.IS_ID or
                        self.symbol.id == self.scanner.ARE_ID):
                    self.symbol = self.scanner.get_symbol()
                    #  OR... Devices
                    if self.symbol.type == self.scanner.NAME:
                        if (self.symbol.id in self.devices.gate_types or
                                self.symbol.id in self.devices.device_types):
                            device_type = self.symbol.id

                            # ignore 'with'
                            
                            self.symbol = self.scanner.get_symbol()
                        
                            self.ignore_none()

                            # 2. Number
                            if self.symbol.type == self.scanner.NUMBER:
                                if self.error_count == 0:
                                    print(device_type)
                                    for i in device_info:
                                        device_er = self.devices.make_device(
                                            i,
                                            device_type,
                                            self.symbol.id)
                                        if device_er != self.devices.NO_ERROR:
                                            self.display_error(
                                                device_er)
                                            break
                                # ignore 'input'
                                self.symbol = self.scanner.get_symbol()

                                self.ignore_none()

                                if self.symbol.type == self.scanner.SEMICOLON:
                                    self.symbol = self.scanner.get_symbol()

                                else:
                                    self.display_error(self.NO_SEMICOLON)

                            else:
                                self.display_error(self.NO_NUM)

                        else:
                            self.display_error(self.NO_DEVICE)

                    else:
                        self.display_error(self.INVALID_DEVICE_NAME)

                else:
                    self.display_error(self.NO_LINKING_VERB)
        else:
            self.display_error(self.INVALID_DEVICE_NAME)

    def parse_connecction(self):
        """Parse the connection file."""
        # e.g FF.q connect G.g1
        self.symbol = self.scanner.get_symbol()
        # FF
        if self.symbol.type == self.scanner.NAME:
            self.symbol = self.scanner.get_symbol()
            first_device = self.devices.get_device(self.symbol.id)

            # if first_device is None:
            #     self.display_error(self.NO_DEVICE)

            if first_device is None:
                self.display_error(self.NO_DEVICE)

            elif first_device.device_kind == self.devices.D_TYPE:
                self.symbol = self.scanner.get_symbol()
                # DOT
                if self.symbol.type != self.sanner.DOT:
                    self.display_error(self.NO_DOT)

                # PORT
                self.symbol = self.scanner.get_symbol()

                if self.symbol.id not in self.devices.dtype_output_ids:
                    self.display_error(self.INVALID_PORT)

                first_device_port_id = self.symbol.id

            else:
                first_device_port_id = None

            #  CONNECT
            self.symbol = self.scanner.get_symbol()
            if self.symbol.id == self.scanner.CONNECT_ID:
                self.symbol = self.scanner.get_symbol()

            else:
                self.display_error(self.NO_CONNECT_SYMBOL)

            #  Device
            self.symbol = self.scanner.get_symbol()
            second_device = self.devices.get_device(self.symbol.id)

            # if second_device is None:
            #     self.display_error(self.NO_DEVICE)

            self.symbol = self.scanner.get_symbol()
            # DOT
            if self.symbol.type != self.scanner.DOT:
                self.display_error(self.NO_DOT)
            # Port
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.NAME:
                self.display_error(self.INVALID_DEVICE_NAME)

            second_device_port_id = self.symbol.id

            self.symbol = self.scanner.get_symbol()

            if self.symbol.type != self.scanner.SEMICOLON:
                self.display_error(self.NO_SEMICOLON)

            self.symbol = self.scanner.get_symbol()

            if self.error_count == 0:
                error_type = self.network.make_connection(
                    first_device.device_id,
                    first_device_port_id,
                    second_device.device_id,
                    second_device_port_id)
                if error_type != self.network.NO_ERROR:
                    self.display_error(error_type)

        else:
            self.display_error(self.INVALID_DEVICE_NAME)

    def parse_monitor(self):
        """Parse the monitor section."""
        monitor_info = []
        while self.symbol.type != self.scanner.CURLY_CLOSE:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.NAME:
                if (
                    self.symbol.id in self.devices.gate_types or
                        self.symbol.id in self.devices.device_types):
                    monitor_info.append(self.symbol.id)
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.symbol.COMMA:
                        self.symbol = self.scanner.get_symbol()
                    else:
                        self.display_error(self.NO_COMMA)
                else:
                    self.display_error(self.NO_DEVICE)
                    break
            else:
                self.display_error(self.INVALID_DEVICE_NAME)

        if self.error_count == 0:
            for i in monitor_info:
                monitor_error_type = self.monitors.make_monitor(i, None)
                if monitor_error_type != self.monitors.NO_ERROR:
                    self.display_error(monitor_error_type)

    def ignore_none(self):
        """Ignore None output."""
        while True:
            if self.symbol.type is None:
                self.symbol = self.scanner.get_symbol()
            else:
                break

    def display_error(self, error_type):
        """Display errors."""
        self.error_count += 1
        # error_position = 1
        error_position = self.scanner.lines[self.symbol.line_number]
        error_content = self.error_dict[error_type]
        symbol_pos = self.symbol.position
        print(error_position, "" * symbol_pos + "^", error_content)
