import json
import os
import copy
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
def get_all_functioncall(cflow_re):
    re =  cflow_re[1:]
    call_list = list()
    # print(cflow_re)
    for line in re:
        line = line.strip()
        if line.find('()') == -1:
            continue
        func_begin = line.find('-')
        if func_begin == -1:
            continue
        fcname = line[func_begin + 1: line.find('()')]
        call_list.append(fcname)
    call_list = list(set(call_list))
    return call_list

# def 

if __name__ == '__main__':
    prog_out_dir = '/home/jhliu/output/libpcap-funcs-cflow/'
    in_path = prog_out_dir + '0name_list'
    out_path = prog_out_dir + '0func_info.json'
    standard_path = '/home/jhliu/data/CheckFunction/standardC'
    prog_path = prog_out_dir + '0func_list'
    
    # read
    in_list = list()
    standard_list = list()
    prog_list = list()
    in_list = read_json(in_path)
    # with open(in_path, 'r') as f:
    #     in_list = f.readlines()
    with open(standard_path, 'r') as f:
        tmp = f.read().strip('\n')
        standard_list = tmp.split('\n')
    with open(prog_path, 'r') as f:
        tmp = f.read().strip('\n')
        prog_list = tmp.split('\n')
    print(len(standard_list))
    print(len(prog_list))
    # end
    all_list = list()
    i = 0
    for item in in_list:
        i += 1
        # item = item.strip('\n')
        # print(item)
        print(f'{str(i)} / {str(len(in_list))}')
        file_path = item['path']
        # print(file_path)
        func_name = item['func_name']
        file_content = ''
        out_dict = dict()
        out_dict['path'] = file_path
        out_dict['func'] = func_name
        out_dict['type'] = 'function'
        out_dict['standard_num'] = 0
        out_dict['other_num'] = 0
        out_dict['standard_fc'] = list()
        out_dict['other_fc'] = list()
        out_dict['orig_path'] = item['orig_path']
        # with open(file_path, 'r') as f:
        #     file_content = f.read()
        # print(file_content)
        # name_index = file_content.find(func_name)
        # func_index = file_content.find('{', name_index)
        # func_content = file_content[func_index: ]
        # print(func_content)
        # fc_dict = get_all_functioncall(func_content)
        # # fc有可能是standard，也有可能是列表的第三方，也有可能不在列表里（第三方/标准库）
        # if func_name == 'swri_audio_convert_alloc':
        #     break
        
        # cflow
        cflow_cmd = 'cflow -T --omit-arguments --omit-symbol-names ' + '-m ' + func_name + ' -o /home/jhliu/tmp/cflow ' + '"' + file_path + '"'
        # print(cflow_cmd)
        os.system(cflow_cmd)
        cflow_re = ''
        with open('/home/jhliu/tmp/cflow', 'r', errors='ignore') as f:
            cflow_re = f.readlines()
        # print(cflow_re)
        
        # os.remove('/home/jhliu/tmp/cflow')
        if len(cflow_re) > 1:
            fc_list = get_all_functioncall(cflow_re)
            # print(fc_list)
            # exit(1)
            for fc in fc_list:
                if fc in standard_list:
                    out_dict['standard_fc'].append(fc)
                    out_dict['standard_num'] += 1
                else:
                    out_dict['other_fc'].append(fc)
                    out_dict['other_num'] += 1
        all_list.append(out_dict)
        # print(all_list)
        
        # print(all_list)
        # with open(out_path, 'a') as f:
        #     f.write(json.dumps(out_dict))
        #     f.write('\n')
        # print(cflow_re)
        # print(fc_list)
            
        # if i == 10:
    all_list.sort(key=lambda k: (k.get('other_num', 0)), reverse=False)
    for item in all_list:
        with open(out_path, 'a') as f:
            f.write(json.dumps(item))
            f.write('\n')

