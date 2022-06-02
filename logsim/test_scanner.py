
import pytest
from names import Names
from scanner import Scanner
# from main_project.error import SyntaxError, SemanticError, ValueError, UnclassedError

'''Test the scanner module'

list of functions to test:
get_symbol
error
'''


@pytest.fixture
def new_names():
    names = Names()
    return names


@pytest.fixture
def new_symbol():
    symbol = Symbol()
    return symbol


@pytest.fixture
def new_scanner():
    data = ("   device7, 12 has ")
    other_names = Names()
    scan = Scanner(data, other_names, True)
    return scan


@pytest.fixture
def no_spaces():
    return ["d", "e", "v", "i", "c", "e", "7", ",", "1", "2", "h", "a", "s"]



def test_new_scanned_item_functionality(new_names):
    """Test that a file not found error works"""
    with pytest.raises(FileNotFoundError):
        Scanner("fakefile.txt", new_names, False)


def test_skip_spaces(new_scanner, new_names, expected_out="d"):
    """Test the self.skip_spaces() functionality of the scanner class"""
    new_scanner.skip_spaces()
    assert new_scanner.current_character == expected_out


def test_advance(new_scanner, no_spaces):
    """Test the self.advance() functionality of the scanner class"""
    i = 0
    while i <= len(no_spaces)-1:
        expected = no_spaces[i]
        new_scanner.skip_spaces()
        assert new_scanner.current_character == expected
        new_scanner.advance()
        i += 1


def test_get_name_and_num(new_scanner, new_names):
    """check that the get_name function gives out a valid name and the next character,
    check that the name is an alphanumerical string"""
    new_scanner.skip_spaces()
    name = new_scanner.get_name()
    assert name[0] == "device7"
    assert name[1] == ","
    assert name[0].isalnum()
    new_scanner.advance()
    new_scanner.advance()
    number = new_scanner.get_number()
    assert number[0] == "12"
    assert number[1] == " "


@pytest.mark.parametrize("data, expected_output_type, expected_output_id", 
                         [("Device",4, 0), ("NAND", 8, 9), ("device", 4, 1),
                           ("A12J", 8, 9), (";", 1, None), ("12", 5, None)])
def test_get_symbol(new_names, data, expected_output_type, expected_output_id):
    """Test that names, numbers, symbols and keywords are all
    initialised and stored in the right sections"""
    test_scan = Scanner(data, new_names, True)
    val = test_scan.get_symbol()
    print(val.id)
    assert val.type == expected_output_type
    assert val.id == expected_output_id


def test_dot_recognition(new_names):
    """Tests the recognition of an arrow symbol """
    test_scan = Scanner(".", new_names, True)
    val = test_scan.get_symbol()
    assert val.type == 2


def test_get_symbol_ignore():
    empty_names = Names()
    """check that the words in the scanner.ignore list are not appended to the name class"""
    test_strings = ('gates', 'gate', 'initially', '  initially', "cycles")
    before = len(empty_names.names)
    for word in test_strings:
        test_scan = Scanner(word, empty_names, True)
        # this will make symbols for all 10 defined symbols, but none for the ignored strings inputed
        val = test_scan.get_symbol()
        assert val.type is None
    after_num = len(empty_names.names)
    assert before + 9 == after_num
    assert empty_names.names == ["Device", "device", "Connection", "Monitor", "is", "are", "input", 
        "simulation", "connect"]


def test_wordcount(new_names):
    """test to see whether the names in the input string are added
    correctly and that the wordcount is counting well too"""
    Scanner("", new_names, True)
    before = []
    after = []
    before.append(len(new_names.names))
    before.append(0)
    test_scan = Scanner("A1 connect A2.I4", new_names, True)
    i = 0
    while i <= 4:
        test_scan.get_symbol()
        i += 1
    after.append(len(new_names.names))
    after.append(test_scan.word_number)
    print(after)
    print(before)
    assert after[0] == before[0] + 3 #name list length (no keywords or dot etc.)
    assert after[1] == before[1] + 5 #word number


def test_non_valid_symbol(new_names):
    """Test that the non valid characters and names raise the approrpiate errors"""
    with pytest.raises(SyntaxError):
        Scanner(" +", new_names, True).get_symbol()  # + is not a valid symbol
        #Scanner(" 4fjd", new_names, True).get_symbol() #non alphanumeric


@pytest.mark.parametrize("inputs, outputs", [("#hello \nh", "\n"),
                                             ("//hello \n world //h", "h")])
def test_comments(inputs, outputs, new_names):
    """Testing that the scanner skips over the two error types correctly"""
    new_scan = Scanner(inputs, new_names, True)
    new_scan.get_symbol()
    out = new_scan.current_character
    assert out == outputs

