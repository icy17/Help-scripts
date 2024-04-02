import sys
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
# TODO
def gen_rule_list(key_name):
    rule_type = ''
    rule_list = list()
    print(key_name)
    if item[key_name] == '':
        return None
    if key_name == 'NULL-index':
        rule_type = 'parameter-check'
    elif key_name == 'uninitialized-index':
        rule_type = 'uninitialize'
    elif key_name == 'must not be freed':
        rule_type = 'dangle-use'
    # elif key_name == 'must not be used':
    #     rule_type = 'uaf'
    elif key_name == 'must be freed':
        rule_type = 'malloc-missing-free'
    # elif key_name == 'Nbeforecall':
    #     rule_type = 'check_Nbefore'
    elif key_name == 'beforecall':
        rule_type = 'check_before'
        rule_dict = dict()
        rule_dict['rule'] = rule_type
        rule_dict['index'] = item[key_name]
        rule_list.append(rule_dict)
        return rule_list
    elif key_name == 'relation':
        # {"rule": "relation", "index": {"target": "0", "influence": "1"}}
        rule_type = 'relation'
        rule_dict = dict()
        rule_dict['rule'] = rule_type
        rule_dict['index'] = dict()
        rule_dict['index']['target'] = ''
        rule_dict['index']['influence'] = ''
        rule_list.append(rule_dict)
        return rule_list
    else:
        return None
    index_list = item[key_name].split(',')
    for index_t in index_list:
        rule_dict = dict()
        rule_dict['rule'] = rule_type
        # print(index_t.strip(' '))
        # print(key_name)
        # print(rule_type)
        index_t = int(index_t.strip(' '))
        rule_dict['index'] = index_t
        
        rule_list.append(rule_dict)
    return rule_list

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python ./gen_rule.py <in_json> <out_json>')
        exit(1)
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    in_list = read_json(in_path)
    target_libs = ['libevent', 'libzip', 'zlib', 'curl', 'libcurl']
    for item in in_list:
        out_dict = dict()
        rule_list = list()
        out_dict['api'] = item['Function']
        out_dict['lib'] = item['Lib']
        print(item)
        if item['Lib'] not in target_libs:
            continue
        for key in item.keys():
            if key == 'Function' or key == 'Lib':
                continue
            re = gen_rule_list(key)
            if re == None:
                continue
            rule_list.extend(re)
        if len(rule_list) == 0:
            continue
        out_dict['rule_list'] = rule_list
        with open(out_path, 'a') as f:
            f.write(json.dumps(out_dict))
            f.write('\n')
    