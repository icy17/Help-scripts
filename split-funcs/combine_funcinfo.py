import json
import os
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


if __name__ == '__main__':
    project_name = 'libpcap'
    main_dir = '/home/jhliu/output/' + project_name + '-funcs'
    func_info1 = main_dir + '/0func_info.json'
    func_info2 = main_dir + '-cflow/0func_info.json'
    out_path = main_dir + '/0func_info_all.json'
    
    all_dict = dict()
    all_list = list()
    main_list = read_json(func_info1)
    for line in main_list:
        func_name = line['func']
        orig_path = line['orig_path']
        key_name = func_name + '-' + orig_path
        line['method'] = 'treesitter'
        all_list.append(line)
        # with open(out_path, 'a') as f:
        #     f.write(json.dumps(line))
        #     f.write('\n')
        all_dict[key_name] = 'treesitter'
    cflow_list = read_json(func_info2)
    for line in cflow_list:
        func_name = line['func']
        orig_path = line['orig_path']
        key_name = func_name + '-' + orig_path
        if key_name not in all_dict.keys():
            line['method'] = 'cflow'
            line['indirect_fc'] = list()
            line['type'] = 'function'
            line['indirect_num'] = 0
            all_list.append(line)
            # with open(out_path, 'a') as f:
            #     f.write(json.dumps(line))
            #     f.write('\n')
    all_list.sort(key=lambda k: (k.get('other_num', 0)), reverse=False)
    for item in all_list:
        with open(out_path, 'a') as f:
            f.write(json.dumps(item))
            f.write('\n')