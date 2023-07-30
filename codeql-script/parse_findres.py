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

if __name__ == '__main__':
    in_name = '/home/jhliu/data/Detect-data/name.json'
    in_findres = '/home/jhliu/data/Detect-data/findres'
    out_findres = in_findres + '-parsed'
    
    
    findres_list = read_json(in_findres)
    name_list = read_json(in_name)
    print(len(findres_list))
    print(len(name_list))
    name_dict = dict()

    for item in name_list:
        name_dict[item['software']] = item['repo-name']
    
    hit_list = list()
    for item in findres_list:
        if item['repo'] not in name_dict.keys():
            print(item['repo'])
            print('not in key!')
            exit(1)
        item['repo'] = name_dict[item['repo']]
        hit_name = item['repo'] + item['api']
        if hit_name in hit_list:
            continue
        else:
            hit_list.append(hit_name)
        with open(out_findres, 'a') as f:
            f.write(json.dumps(item))
            f.write('\n')
