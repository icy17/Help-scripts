import os
import json
def read_json(in_path):
    # in_list = list()
    out_list = list()
    with open(in_path, 'r') as f:
        tmp_list = f.readlines()
    for line in tmp_list:
        line = line.strip('\n')
        line_json = json.loads(line)
        out_list.append(line_json)
    return out_list


def get_all_file_path(in_dir):
    out_list = list()
    for root, dirs, files in os.walk(in_dir):
        for file in files:
            last_str = file.strip('.').split('.')[-1]
            if (last_str[0] != 'c' and last_str[0] != 'h') or last_str == 'conf' or last_str == 'cnf':
                continue
            out_list.append(root + '/' + file)
        # out_list.extend(files)
    return out_list

def get_func_name(func):
    index1 = func.find('{')
    if index1 <= 0:
        return ''
    tmp = func[index1-1]
    while tmp == ' ' or tmp == '\n':
        index1 -= 1
        if index1 <= 0:
            return ''
        tmp = func[index1]
    if tmp != ')':
        return ''
    tmp_func = func[0: index1+1]
    index2 = tmp_func.rfind('(')
    if index2 <= 0:
        return ''
    tmp = tmp_func[index2-1]
    while tmp == ' ' or tmp == '\n':
        index2 -= 1
        if index2 <= 0:
            return ''
        tmp = func[index2]
    final_str = tmp_func[0: index2 + 1].strip('\n').strip(' ').replace('\n', ' ')
    name_index = final_str.rfind(' ')
    final_name = final_str[name_index: index2].strip('\n').strip(' ').strip('(').strip('*')
    if final_name.find('(') != -1 or final_name.find(')') != -1 or final_name.find('/') != -1:
        return ''
    return final_name

    


    # return ''

# 返回值是start+这个prog分出来的函数数量
def split_func(prog, out_prefix, start):
    
    num = 0
    
    last_prog = prog
    index = prog.find('{')
    if index == -1:
        return start
    # func_list = list()
    index_list = list()
    while index != -1:
        first_index = index
        index1 = first_index
        first_times = 0
        last_times = 1
        first_index += 1
        # print('find \{\}')
        while last_times != 0 and first_index != -1:
            first_index += 1
            next_1 = last_prog.find('{', first_index)
            # print('find \{:' + str(next_1))
            # print(last_prog[nex])
            next_2 = last_prog.find('}', first_index)
            # print('find \}:' + str(next_2))
            # if next_2 == -1:
            #     index_dict[first_index] = -1
            #     break
            if next_2 < next_1:
                last_times -= 1
            else:
                # print(last_prog[next_1: next_2 + 1])
                plus_times = last_prog.count('{', next_1, next_2)
                # print("pluse times:" + str(plus_times))
                last_times = last_times + plus_times -1
            first_index = next_2
            # print('first_index:' + str(first_index))
        index2 = first_index
        index_list.append(index2)
        index = last_prog.find('{', index2, -1)
    index_beg = 0
    for key in index_list:
       
        tmp_prog = prog[index_beg : key + 1]
        index_beg = key + 1
        
        # print('\n\none func')
        print(tmp_prog)
        func_name = get_func_name(tmp_prog)
        if func_name == '':
            continue
        num += 1
        # print(type(out_prefix))
        # print(type(func_name))
        print(func_name)
        out_path = out_prefix + '-' + str(start + num) + '-' + func_name
        with open(out_path, 'a') as f:
            f.write(tmp_prog)
            f.write('\n')
        
        with open(func_name_path, 'a') as f:
            f.write(func_name + ': ' + out_path + '\n')
        # exit(1)
    return num

if __name__ == '__main__':
    project_dir = '/home/jhliu/repos/libpcap'
    out_dir = '/home/jhliu/output/' + project_dir.split('/')[-1] + '-funcs-cflow/'
    func_name_path = out_dir + '0name_list'
    parse_path = out_dir + '0func_list'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    files = get_all_file_path(project_dir)
    # print(files)
    index_start = 0
    # func_list = list()
    # line_list = list()
    fcname_list = list()
    for file_path in files:
        file_name = file_path.split('/')[-1]
        # if file_name != 'swresample.c':
        #     continue
        cflow_cmd = 'cflow -T --omit-arguments --omit-symbol-names -o /home/jhliu/tmp/cflow ' + '"' + file_path + '"'
        prog = ''
        print(cflow_cmd)
        os.system(cflow_cmd)
        cflow_re = ''
        lines = list()
        prog_lines = list()
        func_list = list()
        
        if not os.path.exists('/home/jhliu/tmp/cflow'):
            continue
        with open(file_path, 'r',errors='ignore') as f:
            tmp = f.read().strip('\n')
            prog_lines = tmp.split('\n')
        
        with open('/home/jhliu/tmp/cflow', 'r') as f:
            cflow_re = f.read()
            lines = cflow_re.split('\n')
        for line in lines:
            if line.find(') at ') == -1:
                continue
            
            index1 = line.find(file_name + ':')
            if index1 == -1:
                continue
            index_name = line.find('-')
            index_name_end = line.find('()')
            func_name = line[index_name + 1: index_name_end]
            end_index = line.find('>')
            line_num_str = line[index1 + len(file_name) + 1: end_index]
            # print(line_num_str)
            # print(type(line[index1 + len(file_name) + 1:].strip('>')))
            line_num = int(line_num_str)
            out_dict = dict()
            out_dict['func_name'] = func_name
            out_dict['line'] = line_num
            out_dict['orig_path'] = file_path
            out_dict['type'] = 'function'
            # out_dict['path'] = file_path
            # print(out_dict)
            if func_name == 'main':
                continue
            func_list.append(out_dict)
            # exit(1)
            # TODO: debug 确定每个name都是对的
        if len(func_list) == 0:
            continue
        # func_list = list(set(func_list))
        func_list.sort(key=lambda k: (k.get('line', 0)), reverse=False)
        # print(func_list)
        next_index = 1
        for func in func_list:
            
            
            out_path = out_dir + file_name + '-' + str(func['line']) + '-' + func['func_name']
            func['path'] = out_path
            # if out_path in fcname_list:
            #     print(out_path)
            #     continue
            # else:
            #     print(out_path)
            #     fcname_list.append(out_path)
            
            # list_index = func_list.index(func)
            if next_index < len(func_list):
                line_next = func_list[next_index]['line']
                next_index += 1
                # line_next = func_list[list_index + 1]['line']
                # if func['func_name'] == 'free_temp':
                #     print(func_list[list_index + 1])
                #     print(line_next)
                if line_next == func['line']:
                    continue
                with open(func_name_path, 'a') as f:
                    f.write(json.dumps(func))
                    f.write('\n')
                
                for i in range(func['line'] - 1, line_next - 1):
                    with open(out_path, 'a') as f:
                        f.write(prog_lines[i] + '\n')
            else:
                with open(func_name_path, 'a') as f:
                    f.write(json.dumps(func))
                    f.write('\n')
                for i in range(func['line'] - 1, len(prog_lines)):
                    with open(out_path, 'a') as f:
                        f.write(prog_lines[i] + '\n')

        # exit(1)

    # parse re
    in_list = list()
    out_list = list()
    
    in_list = read_json(func_name_path)
    for line in in_list:
        func_name = line['func_name']
        out_list.append(func_name)
    out_list = list(set(out_list))
    for item in out_list:
        with open(parse_path, 'a') as f:
            f.write(item + '\n')