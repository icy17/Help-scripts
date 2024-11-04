import os
import json
import copy

before_list = list()
loop_flag = False

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

def write_out(path, out_dict):
    with open(path, 'a') as f:
        f.write(json.dumps(out_dict))
        f.write('\n')
        
if __name__ == '__main__':
    project_name = 'libpcap'
    in_dir = '/home/jhliu/output/' + project_name + '-funcs/'
    in_path = in_dir + '0call_graph.json'
    api_path = '/home/jhliu/data/CheckFunction/' + project_name + '_API'
    out_path = in_dir + '0parse_order.json'

    in_list = read_json(in_path)
    api_list = list()
    with open(api_path, 'r') as f:
        tmp = f.read()
        api_list = tmp.strip('\n').split('\n')
    all_num = 0
    before_list = list()
    for line in in_list:
        func = line['func']
        nums = line['analyse_func_num']
        if line['no_fc_num'] != 0 or line['indirect_num'] != 0:
            continue
        if func in api_list:
            if nums < 25 and nums > 0:
                call_graph = line['call_graph']
                for callee in call_graph:
                    if callee not in before_list:
                        before_list.append(callee)
                        all_num += 1
                if len(call_graph) == 0:
                    callee = func
                    if callee not in before_list:
                        before_list.append(callee)
                        all_num += 1
                line['all_num'] = all_num
                write_out(out_path, line)
                if all_num > 200:
                    break
            
