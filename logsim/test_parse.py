"""Test the parse module"""

import pytest

from names import Names
from devices import Devices
from scanner import Scanner
from network import Network
from monitors import Monitors
from parse import Parser

def start_up(path):
    names = Names()
    scanner = Scanner(path, names, False)
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    parse = Parser(names,devices,network,monitors,scanner)
    return parse

# @pytest.fixture
# def parse():
#     return start_up("Definition_file.txt")


@pytest.mark.parametrize(
    "file, expected_output",
    [
        (
            "Definition_Ex1.txt",
            True,
        ),
        (
            "Definition_Ex2.txt",
            True,
        ),
    ],
)

def test_parse_network(file, expected_output):
    parse = start_up(file)
    assert parse.parse_network() == expected_output





@pytest.mark.parametrize(
    "file, expected_output",
    [
        ( "Definition_Ex1.txt", True, ),
        ( "Definition_Ex4.txt", False, ),
    ],
)

def test_parse_network_part(file,expected_output):
    parse = start_up(file)
    parse.parse_network()
    output = parse.device_section and parse.connection_section and parse.monitor_section
    assert output == expected_output
    
@pytest.mark.parametrize("input, error_count",
                         [("Device{A,B are with 2 inputs;} Connection{}", 0),
                          ])