import json
import sys

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
    print('This script counts the frequency of each API occurrence in the findres file and outputs it in descending order')
    print('Usage: python3 ./cal_API_num.py <in_findres> <out_num_file>')
    if len(sys.argv) != 3:
        print('Wrong Input\nUsage: python3 ./cal_API_num.py <in_findres> <out_num_file>')
        exit(1)
    
    
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    in_list = read_json(in_path)
    api_dict = dict()
    lib_dict = dict()
    for item in in_list:
        api_name = item['api']
        lib = item['lib']

        lib_dict[api_name] = lib
        if api_name not in api_dict.keys():
            api_dict[api_name] = item['hit_nums']
        else:
            api_dict[api_name]  += item['hit_nums']
    out_list =list()
    for api in api_dict.keys():
        out_dict = dict()
        out_dict['api'] = api
        out_dict['lib'] = lib_dict[api]
        out_dict['num'] = api_dict[api]
        out_list.append(out_dict)
    out_list.sort(key=lambda k: (k.get('num', 0)), reverse=True)
    for line in out_list:
        with open(out_path, 'a') as f:
            f.write(json.dumps(line))
            f.write('\n')