from names import Names
from scanner import Scanner
new_names = Names()
test_scan = Scanner(r"C:\Users\10513\OneDrive\Documents\Cam\IIA\GF2 git\GF2_Software\Definition_file.txt", new_names, False)

for i in range(300):

    val = test_scan.get_symbol()
    if val != None:
        print(f"type = {val.type}")
        print(f"id = {val.id}")
        print(f"line = {val.line_number}")
        print(f"pos = {val.position}")