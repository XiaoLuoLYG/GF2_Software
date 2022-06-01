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

@pytest.mark.parametrize(
    
)