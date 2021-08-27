import os

_type=input('input format to find: ')
for root, dirs, files in os.walk(input('input your dir(ex.:/Users/aleksandrglotov/Desktop): ')):
    for file in files:
        if file.endswith(f".{_type}"):
            path_file = os.path.join(root, file)
            print(path_file)

