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
# e.g. get_value_from_json(list, 'pcap_freecode', 'func') will get json of pcap_freecode
def get_value_from_json(json_list, key_value, key_match):
    for item in json_list:
        key = item[key_match]
        if key == key_value:
            return item
    return None


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python ./gen_rule.py <in_json1> <in_json2> <out_json>')
        exit(1)
    in_path1 = sys.argv[1]
    in_path2 = sys.argv[2]
    out_path = sys.argv[3]
    in_list1 = read_json(in_path1)
    in_list2 = read_json(in_path2)

    target_libs = ['libevent', 'libzip', 'zlib', 'curl', 'libcurl']
    for item in in_list1:
        if item['lib'] not in target_libs:
            continue
        with open(out_path, 'a') as f:
            f.write(json.dumps(item))
            f.write('\n')
    for item in in_list2:
        
        api = item['api']
        if item['lib'] not in target_libs:
            continue
        out_dict = dict()    
        out_dict['api'] = api
        out_dict['lib'] = item['lib']
        rule_list = list()
        re = get_value_from_json(in_list1, api, 'api')
        print(re)
        if re == None:
            with open(out_path, 'a') as f:
                f.write(json.dumps(item))
                f.write('\n')
        else:
            rule_list2 = re['rule_list']
            for rules in item['rule_list']:
                to_type = rules['rule']
                to_index = rules['index']
                match_flag = False
                for rule_match in rule_list2:
                    type_in = rule_match['rule']
                    index_in = rule_match['index']
                    if type_in == to_type and to_index == index_in:
                        match_flag = True
                        break
                if match_flag == False:
                    rule_list.append(rules)
            out_dict['rule_list'] = rule_list
            if len(rule_list) != 0:
                with open(out_path, 'a') as f:
                    f.write(json.dumps(out_dict))
                    f.write('\n')
