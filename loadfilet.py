from names import Names
from scanner import Scanner
new_names = Names()
test_scan = Scanner(r"Z:\Documents\GF2_Software\logsim\Definition_Ex1.txt", new_names, False)

for i in range(300):

        val = test_scan.get_symbol()

        print(f"type = {val.type}")
        print(f"id = {val.id}")
        print(f"line = {val.line_number}")
        print(f"pos = {val.position}")