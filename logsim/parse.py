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


from zmq import device


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
         self.NO_DOT,
         self.NO_CURLY_OPEN,
         self.NO_CURLY_CLOSE,
         self.NO_DEVICE,
         self.NO_NUM,
         self.NO_CONNECT_SYMBOL,
         self.INVALID_DEVICE_NAME,
         self.INVALID_DEVICE_TYPE,
         self.INVALID_PORT
         ] = self.names.unique_error_codes(15)

        self.error_dict = {
            # Sytanx error
            self.NO_SECTIONS: "Error: Expected a section before going further.",
            self.NO_DEVICE_SECTION: "Error: Expected a device section",
            self.NO_CONNECTION_SECTION: "Error: Expected a connection section",
            self.NO_MONITOR_SECTION: "Error: Expected a monitor section",
            self.NO_LINKING_VERB: "Error: Expected a linking verb",
            self.NO_SEMICOLON: "Error: Expected a ';'",
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
            network.DEVICE_ABSENT: "Error: No such a device",

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

        # used to return the device type for each name
        # self.names_list = []
        # self.device_type_list = []

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        if self.symbol.type == self.scanner.EOF:
            self.display_error(self.NO_SECTIONS)

        while self.symbol.type != self.scanner.EOF:
            self.symbol = self.scanner.get_symbol()

            if self.symbol.type == self.scanner.KEYWORD:
                # Device
                if self.symbol.id == self.scanner.DEVICE_ID:
                    self.device_section = True
                    self.parse_sections('DEVICE')

                # Connection
                elif self.symbol.id == self.scanner.CONNECTION_ID:
                    self.connection_section = True
                    self.parse_sections('CONNECTION')

                    # check whether we have the device section
                    # if self.device_section:
                    #     continue
                    # else:
                    #     self.display_error(self.NO_DEVICE_SECTION)
                    #     break

                # Monitor
                elif self.symbol.id == self.scanner.MONITOR_ID:
                    self.monitor_section = True
                    self.parse_sections('MONITOR')
                    # check whether we have the connection section
                    # if self.connection_section:
                    #     # self.symbol = self.scanner.get_symbol()
                    #     # print(self.symbol.type)
                    #     continue
                    # else:
                    #     self.display_error(self.NO_CONNECTION_SECTION)
                    # break

            else:
                if (not self.device_section or
                    not self.connection_section or
                        not self.monitor_section):
                    self.display_error(self.NO_SECTIONS)
                break
        # check whether we have the monitor section
            # if not self.monitor_section:
            #     self.display_error(self.NO_MONITOR_SECTION)
        print(f'\n total number of errors: {self.error_count}')

        if self.error_count == 0:

            return True

    def parse_sections(self, KEYWORD):
        """Parse each section."""
        # check the CURLY_OPEN
        self.symbol = self.scanner.get_symbol()

        while self.symbol.type is None:
            self.symbol =self.scanner.get_symbol()
        if self.symbol.type == self.scanner.CURLY_OPEN:
            self.symbol = self.scanner.get_symbol()
        else:
            self.display_error(self.NO_CURLY_OPEN)
        # parse the section and check the CURLY_CLOSE
        while self.symbol.type != self.scanner.CURLY_CLOSE:

            if KEYWORD == 'DEVICE':
                self.parse_device()

            elif KEYWORD == 'CONNECTION':
                self.parse_connection()

            elif KEYWORD == 'MONITOR':
                self.parse_monitor()

            elif self.symbol.type == self.scanner.EOF:
                self.display_error(self.NO_CURLY_CLOSE)
                break

    def parse_device(self):
        """Parse the device section."""
        # e.g. A,B are OR with 2 inputs
        # e.g. C is NAND with 2 inputs;
        # A
        # print(self.symbol.type)

        if self.symbol.type == self.scanner.NAME:
            device_info = []
            device_info.append(self.symbol.id)
            # self.names_list.append(self.symbol.id)
            # ,
            self.symbol = self.scanner.get_symbol()

            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.NAME:
                    device_info.append(self.symbol.id)
                    # self.names_list.append(self.symbol.id)
                    self.symbol = self.scanner.get_symbol()
                else:
                    self.display_error(self.INVALID_DEVICE_NAME)
                    break
        
            # pass
            #  is / are
            if (self.symbol.id == self.scanner.IS_ID or
                    self.symbol.id == self.scanner.ARE_ID):
                self.symbol = self.scanner.get_symbol()
                #  OR... Devices
            

                if self.symbol.type == self.scanner.NAME:
                    gate_type = (self.symbol.id in
                                    self.devices.gate_types)
                    device_type = (self.symbol.id in
                                    self.devices.device_types)
                    if gate_type or device_type:
                        device_kind = self.symbol.id

                        # ignore 'with'
                        if device_kind == self.devices.D_TYPE:
                            if self.error_count == 0:
                                for i in device_info:
                                    device_er = (
                                        self.devices.make_device(
                                            i,
                                            device_kind,
                                            device_property=None))
                                    if (device_er !=self.devices.NO_ERROR):
                                        self.display_error(device_er,skip=False)
                                        break
                            self.symbol = self.scanner.get_symbol()
                            type = self.symbol.type
                            if type != self.scanner.SEMICOLON:
                                self.display_error(self.NO_SEMICOLON)
                            
                            else:
                                self.symbol = self.scanner.get_symbol()

                        else:

                            self.symbol = self.scanner.get_symbol()

                            self.ignore_none()

                            # 2. Number
                            if self.symbol.type == self.scanner.NUMBER:
                                # print(self.devices.gate_types)
                                # print(device_kind)
                                # print(self.symbol.id)
                                # print(self.devices.OR)

                                if self.error_count == 0:
                                    for i in device_info:
                                        er = self.devices.make_device(
                                            i,
                                            device_kind,
                                            int(self.symbol.id)
                                                            )
                                        if er != self.devices.NO_ERROR:
                                            self.display_error(
                                                device_er, skip = False)
                                            break
                                # ignore 'input'

                                self.symbol = self.scanner.get_symbol()

                                # print(self.symbol.type)
                                self.ignore_none()
                                # print(self.symbol.type)
                                type = self.symbol.type
                                if type != self.scanner.SEMICOLON:
                                    self.display_error(
                                        self.NO_SEMICOLON)
                                # print(self.symbol.type)

                                else:
                                    self.symbol = self.scanner.get_symbol()
                            else:
                                self.display_error(self.NO_NUM)

                else:
                    self.display_error(self.INVALID_DEVICE_NAME)
            else:
                self.display_error(self.NO_LINKING_VERB)
        else:
            self.display_error(self.INVALID_DEVICE_NAME)

 

        

    def parse_connection(self):
        """Parse the connection file."""
        # e.g FF.q connect G.g1
        # self.symbol = self.scanner.get_symbol()
        # FF
        if self.symbol.type == self.scanner.NAME:
            first_device = self.devices.get_device(self.symbol.id)
            if first_device is None:
                self.display_error(self.INVALID_DEVICE_NAME)
                self.symbol = self.scanner.get_symbol()

            elif first_device.device_kind == self.devices.D_TYPE:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type != self.scanner.DOT:
                    self.display_error(self.NO_DOT)
                else:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.id not in self.devices.dtype_output_ids:
                        self.display_error(self.INVALID_PORT)

                    first_device_port = self.symbol.id
                    self.symbol = self.scanner.get_symbol()

            else:
                first_device_port = None
                self.symbol = self.scanner.get_symbol()
            #  CONNECT

            if self.symbol.id == self.scanner.CONNECT_ID:
                self.symbol = self.scanner.get_symbol()
                #  Device
                second_device = self.devices.get_device(self.symbol.id)            
                if second_device is None:
                    self.display_error(self.INVALID_DEVICE_NAME)

                else:
                    self.symbol = self.scanner.get_symbol()
                    # DOT
                    if self.symbol.type == self.scanner.DOT:
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.type == self.scanner.NAME:
                                second_device_port = self.symbol.id
                                self.symbol = self.scanner.get_symbol()

                                if self.symbol.type != self.scanner.SEMICOLON:
                                    self.display_error(self.NO_SEMICOLON)
                                    
                                else:
                                    if self.error_count == 0:
                                        error_type = self.network.make_connection(
                                            first_device.device_id,
                                            first_device_port,
                                            second_device.device_id,
                                            second_device_port)
                                        if error_type != self.network.NO_ERROR:
                                            self.display_error(error_type, skip = False)
                                    self.symbol = self.scanner.get_symbol()

                        else:
                            self.display_error(self.INVALID_PORT)
                    else:
                        self.display_error(self.NO_DOT)
                        
            else:
                self.display_error(self.NO_CONNECT_SYMBOL)

        else:
            self.display_error(self.INVALID_DEVICE_NAME)

    def parse_monitor(self):
        """Parse the monitor section."""

        # print(self.symbol.type)
        if self.symbol.type == self.scanner.CURLY_CLOSE:
            pass
        else:
            monitorPoint = self.signame(Monitor_mode=True)
            if monitorPoint is None:
                return
            monitorList = [monitorPoint]
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                # print(self.symbol.type)
                monitorPoint = self.signame(Monitor_mode=True)

                if monitorPoint is None:
                    return
                monitorList.append(monitorPoint)
            if self.symbol.type != self.scanner.SEMICOLON:
                self.display_error(self.NO_SEMICOLON)
            else:
                self.symbol = self.scanner.get_symbol()
            # self.symbol = self.scanner.get_symbol()

            if self.error_count == 0:
                for i in monitorList:
                    monitor_error_type = self.monitors.make_monitor(i[0], i[1])
                    if monitor_error_type != self.monitors.NO_ERROR:
                        self.display_error(monitor_error_type, skip = False)
        return True

    def ignore_none(self):
        """Ignore None output."""
        while True:
            if self.symbol.type is None:
                self.symbol = self.scanner.get_symbol()
            else:
                return True
    

    def signame(self, Monitor_mode=False):
        """Parse each individual signal name."""
        if self.symbol.type == self.scanner.NAME:
            device = self.symbol.id
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.DOT:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.NAME:
                    port = self.symbol.id
                    self.symbol = self.scanner.get_symbol()
                    if port in self.devices.dtype_output_ids:
                        return (device, port)
                    elif (
                            port in self.devices.dtype_input_ids or
                            self.names.get_name_string(port) in self.inputs
                         ):
                        if Monitor_mode:
                            return (device, None)
                        else:
                            return (device, port)
                    else:
                        self.display_error(self.INVALID_PORT, skip = False)
                        return (device, None)
                else:
                    self.display_error(self.INVALID_DEVICE_NAME)
                    return None
            return (device, None)
        else:
            self.display_error(self.INVALID_DEVICE_NAME,skip=False)
            return None
 
    def display_error(self, error_type,skip=True):
        """Display errors."""
        self.error_count += 1

        # error_position = self.scanner.lines[self.symbol.line_number]
        error_content = self.error_dict[error_type]
        symbol_pos = self.symbol.position
        print("" * symbol_pos + "^",
              '\033[1;31m' + error_content + '\033[0m')
        if not skip:
            return

        while self.symbol.type not in [
            self.scanner.SEMICOLON,
            self.scanner.CURLY_CLOSE,
            self.scanner.EOF,
        ]:
            self.symbol = self.scanner.get_symbol()
            print(1)

        if self.symbol.type == self.scanner.SEMICOLON:
            self.symbol = self.scanner.get_symbol()
