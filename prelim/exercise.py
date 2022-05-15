#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""
import sys
import os

def open_file(path):
    """Open and return the file specified by path."""
    try:
        fo = open(path,'r')
    except:
        print("Error:IOError")
        sys.exit()
    else:
        print('\nFile open successfully')
        return fo

def get_next_character(input_file):
    """Read and return the next character in input_file."""
    pos = input_file.tell()
    if pos == 0:
        next_c = input_file.read(1)
    elif pos != 0:
        input_file.seek(0,1)
        next_c = input_file.read(1)

    return next_c

def get_next_non_whitespace_character(input_file):
    """Read and return the next character in input_file."""
    next_nwc = get_next_character(input_file)
    while next_nwc.isspace():
        next_nwc = get_next_character(input_file)
    return next_nwc
    """Seek and return the next non-whitespace character in input_file."""


def get_next_number(input_file):
    """Seek the next number in input_file.

    Return the number (or None) and the next non-numeric character.
    """
    digit_str = ''
    while True:
        next_d = get_next_character(input_file)
        if not next_d.isdigit():
            if next_d == '':#EOF
                digit_str = None
                break
            else:
                continue
        else:
            while next_d.isdigit():
                digit_str += next_d
                next_d = get_next_character(input_file)
                if not next_d.isdigit():
                    digit_str = int(digit_str)
                    break
            break
    return [digit_str,next_d]

def get_next_name(input_file):
    """Seek the next name string in input_file.

    Return the name string (or None) and the next non-alphanumeric character.
    """


def main():
    """Preliminary exercises for Part IIA Project GF2."""

    # Check command line arguments
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print("Error! One command line argument is required.")
        sys.exit()

    else:
        arguments = sys.argv[1]
        if os.path.exists(arguments):
            file_path = os.path.abspath(arguments)
            print("\nNow opening file {fp}".format(fp=file_path))
            fo = open_file(file_path)
        # Print the path provided and try to open the file for reading

            print("\nNow reading file...")
            while True:
                next_c =get_next_character(fo)
                print(next_c,end='')
                if not next_c:
                    break
        # Print out all the characters in the file, until the end of file
            
            print("\nNow skipping spaces...")
            fo.seek(0,0) #reset
            while True:
                next_nwc = get_next_non_whitespace_character(fo)
                print(next_nwc,end='')
                if not next_nwc:
                    break
        # Print out all the characters in the file, without spaces
            print("\n")
            print("\nNow reading numbers...")
            counter = 0 #for EOF
            fo.seek(0,0) #reset
            while True:
                next_digit = get_next_number(fo)
                if next_digit[0] != None: #containing digits
                    counter += 1
                    print(next_digit[0])
                elif not next_digit[0]:
                    if counter == 0: #not containing digit
                        print(next_digit[0])
                        break
                    else:
                        break
            
        # Print out all the numbers in the file
        else:
            print("Error! File not existed")
            sys.exit()
        







        print("\nNow reading names...")
        # Print out all the names in the file

        print("\nNow censoring bad names...")
        # Print out only the good names in the file
        # name = MyNames()
        # bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
        #                 name.lookup("Ghastly"), name.lookup("Awful")]

if __name__ == "__main__":
    main()
