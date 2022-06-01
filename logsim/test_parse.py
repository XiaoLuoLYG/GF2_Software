from tkinter.tix import Tree
from tracemalloc import start
import pytest

from names import Names
from devices import Devices
from scanner import Scanner
from network import Network
from monitors import Monitors
from parse import Parser

def start_up(path):
    names = Names()
    scanner = Scanner(path, names, True)
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    parse = Parser(names,devices,network,monitors,scanner)
    return parse

@pytest.fixture
def parser():
    return start_up()
    
@pytest.mark.parametrize("input, output",
                        [("Device{} Connection{} ", False),
                         ("Device{} Connection{} Monitor", True)
                        
                        ]
    
)

def test_parse_netwrok(input,output):
    indicate = False
    parse = new_parse(input)
    parse.parse_network()
    if (new_parse.device_section == True and
            new_parse.connection_section == True and
                new_parse.monitor_section == True):
        indicate = True
    assert indicate == output