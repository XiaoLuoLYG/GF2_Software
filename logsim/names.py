"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""


class Names:

    """Map variable names and string names to unique integers.

    This class deals with storing grammatical keywords and user-defined words,
    and their corresponding name IDs, which are internal indexing integers. It
    provides functions for looking up either the name ID or the name string.
    It also keeps track of the number of error codes defined by other classes,
    and allocates new, unique error codes on demand.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    unique_error_codes(self, num_error_codes): Returns a list of unique integer
                                               error codes.

    query(self, name_string): Returns the corresponding name ID for the
                        name string. Returns None if the string is not present.

    lookup(self, name_string_list): Returns a list of name IDs for each
                        name string. Adds a name if not already present.

    get_name_string(self, name_id): Returns the corresponding name string for
                        the name ID. Returns None if the ID is not present.
    """

    def __init__(self):
        """Initialise names list."""
        self.error_code_count = 0  # how many error codes have been declared
        self.names = [] # initialize name list

    def unique_error_codes(self, num_error_codes):
        """Return a list of unique integer error codes."""
        if not isinstance(num_error_codes, int):
            raise TypeError("Expected num_error_codes to be an integer.")
        self.error_code_count += num_error_codes
        return range(self.error_code_count - num_error_codes,
                     self.error_code_count)

    def query(self, name_string):
        """Return the corresponding name ID for name_string.

        If the name string is not present in the names list, return None.
        """
        #input error handling
        if type(name_string) != str:
            print('Convert non-string input into string')
            name_string = str(name_string)
            #name error handling 
            if not name_string.isalnum():
                raise SyntaxError("name_string is not alphanumeric")
            if name_string.isdigit():
                raise SyntaxError("name_string is a digit, must be alphanumber string")
            #Return name id or None
            if name_string in self.names:
                id = self.names.index(name_string)
                return id
            else:
                return None
            
        else:
            #name error handling 
            if not name_string.isalnum():
                raise SyntaxError("name_string is not alphanumeric")
            if name_string.isdigit():
                raise SyntaxError("name_string is a digit, must be alphanumber string")
            #Return name id or None
            if name_string in self.names:
                id = self.names.index(name_string)
                return id
            else:
                return None
            

    def lookup(self, name_string_list):
        """Return a list of name IDs for each name string in name_string_list.

        If the name string is not present in the names list, add it.
        """
        #Input error handling
        if not isinstance(name_string_list, str):
            raise TypeError("Expected name_string to be a string.")
        if type(name_string_list) != list:
            raise TypeError("Expected list input.")

        ids=[]
        for name_string in name_string_list:
            #Not present, add it
            if name_string not in self.names:
                self.names.append(name_string)
                id = self.names.index(name_string)
            else:
                id = self.names.index(name_string)
            ids.append(id)
        return id




    def get_name_string(self, name_id):
        """Return the corresponding name string for name_id.

        If the name_id is not an index in the names list, return None.
        """
        if name_id < 0:
            raise ValueError("name_id should be larger than zero")

        try:
            return self.names[name_id]
        except IndexError: #out of range
            return None