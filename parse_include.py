# import os
import sys
from cinspector.interfaces import CCode

def get_declarator(code):
    cc = CCode(code)
    out_list = list()
    declas = cc.get_by_type_name('function_declarator')
    for decla in declas:
        name = decla.declarator.src
        out_list.append(name)
    macros = cc.get_by_type_name('preproc_function_def')
    for macro in macros:
        function_name = macro.name.src
        out_list.append(function_name)
    return out_list

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python3 ./parse_include.py <in_include_file.h> <out_path>')
        exit(1)
    file_path = sys.argv[1]
    out_path = sys.argv[2]
    code = ''
    with open(file_path, 'r') as f:
        code = f.read() 
    find_list = get_declarator(code)
    find_list = list(set(find_list))
    for api in find_list:
        with open(out_path, 'a') as f:
            f.write(api + '\n')
    
    
