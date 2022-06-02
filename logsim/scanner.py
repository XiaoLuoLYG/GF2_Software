import sys
from names import Names
import os
"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None
        self.line_number = None
        self.position = None

class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names, string=False):

        """Open specified file and initialise reserved words and IDs."""
        """
        Open files
        For test purpose, introduce another input: string.
        If true, instead open file, used created string as input.
        """
        if string:
            self.read_as_string = True
            self.input_file = path   # input string
            self.character_count = 0
        else:
            self.read_as_string = False
            try:
                self.input_file = open(path, "r")   # input file
                self.lines = self.input_file.readlines()
                self.input_file.seek(0)
            except FileNotFoundError:
                raise FileNotFoundError(
                    "Error: File doesn't exist in current directory")
                sys.exit()

        # Resevered words and IDs
        self.names = names
        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.DOT,
                                 self.LINECOMMENT, self.KEYWORD, self.NUMBER,
                                 self.CURLY_OPEN, self.CURLY_CLOSE, self.NAME,
                                 self.EOF, self.BULKCOMMENT] = range(11)

        # keyword that cannot be ignored
        self.keywords_list = ["Device", "device",  "Connection",
                              "Monitor", "is", "are", "input",
                               "connect"]

        [self.DEVICE_ID, self.DEVICE_LOWER_ID,
         self.CONNECTION_ID, self.MONITOR_ID, self.IS_ID, self.ARE_ID,
         self.INPUT_ID, 
         self.CONNECT_ID] = self.names.lookup(self.keywords_list)

        # ignore
        self.ignore = ["gate", "gates", "a", "an","with",
                       "some", "initially", "inputs", "connected", "cycles","simulation"]

        self.ending_symbols = [self.SEMICOLON, self.CURLY_CLOSE, self.EOF]

        # initialise
        self.current_character = " "
        self.word_number = 0
        self.current_line_number = 0
        self.current_position = 0

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces()  # current character now not whitespace
        symbol.line_number = self.current_line_number
        symbol.position = self.current_position

        if self.current_character.isalpha():  # name
            name_string_list = self.get_name()
            self.name_string = name_string_list[0]
            if self.name_string in self.ignore:
                symbol.type = None
            elif self.name_string in self.keywords_list:
                symbol.type = self.KEYWORD
                symbol.id = self.names.query(self.name_string)
            else:
                symbol.type = self.NAME
                # symbol.id = self.names.query(self.name_string)
                [symbol.id] = self.names.lookup([self.name_string])

            print(self.name_string, end=' ')

        elif self.current_character.isdigit():  # number
            symbol.id = self.get_number()[0]
            # [symbol.id] = self.names.lookup([number_get])
            symbol.type = self.NUMBER
            print(symbol.id, end=' ')

        elif self.current_character == ",":
            symbol.type = self.COMMA
            print(",", end=' ')
            self.advance()

        elif self.current_character == "{":
            symbol.type = self.CURLY_OPEN
            self.advance()
            print("{", end=' ')

        elif self.current_character == "}":
            symbol.type = self.CURLY_CLOSE
            self.advance()
            print("}", end=' ')

        elif self.current_character == ";":
            symbol.type = self.SEMICOLON
            self.advance()
            print(";", end=' ')

        elif self.current_character == ".":
            symbol.type = self.DOT
            self.advance()
            print(".", end=' ')
        # etc for other punctuation

        elif self.current_character == "#":  # single line comment
            x = 0
            symbol.type = self.LINECOMMENT
            while x < 1:
                self.advance()
                # ignore until end of line
                while self.current_character != "\n":
                    self.advance()
                x += 1
        # bulk comment, expect another (//blabla//)
        elif self.current_character == "/":
            symbol.type = self.BULKCOMMENT
            self.advance()
            # start bulk comment, start ignoring
            if self.current_character == "/":
                consec_slashes = 0
                # ignore until two consecutive slashes
                while consec_slashes < 2:
                    if self.current_character == "/":
                        consec_slashes += 1
                        symbol.type = self.BULKCOMMENT
                        # self.advance()
                    elif self.current_character == "":
                        raise SyntaxError("eof while still in a bulk comment")
                        break
                    else:
                        consec_slashes = 0
                self.advance()
            '''else:
                raise SyntaxError("Unexpected symbol,
                expected '//' at beginning of bulk comment")'''

        elif self.current_character == "":  # end of file
            symbol.type = self.EOF

        else:  # not a valid character
            raise SyntaxError("Error: Invalid character encounter")

        self.word_number += 1
        return symbol

    def advance(self):
        """reads one further character into the document"""
        if self.read_as_string:  # test string input
            try:
                self.current_character = self.input_file[self.character_count]
            except IndexError:
                self.current_character = ""
                return self.current_character
            self.character_count += 1
        else:
            self.current_character = self.input_file.read(1)  # file input

        self.current_position += 1

        if self.current_character == "\n":
            self.current_line_number += 1
            self.current_position = -1

        return self.current_character

    def get_name(self):
        """Seek the next name string in input_file.

        Return the name string(or None)and the next non-alphanumeric character.
        """
        name = self.current_character

        while True:
            self.current_character = self.advance()
            if self.current_character.isalnum():
                name = name + self.current_character
            else:
                return [name, self.current_character]

    def get_number(self):
        """Seek the next number in input_file.

        Return the number (or None) and the next non-numeric character.
        """
        num = self.current_character
        while True:
            self.current_character = self.advance()
            if self.current_character.isdigit():
                num = num+self.current_character
            else:
                return [num, self.current_character]

    def skip_spaces(self):
        """"advances until the character is no longer a space"""

        while self.current_character.isspace():
            self.current_character = self.advance()
