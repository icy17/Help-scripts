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
    new_all_findres = '/root/output/detect-702-all/searchres'
    old_findres = '//root/output/detect-major-must-hit/searchres'
    out_findres = '//root/output/detect-702-all/searchres-filter'

    old_json = read_json(old_findres)
    new_json = read_json(new_all_findres)

    hit_list = list()
    for item in old_json:
        hit_str = item['api'] + item['repo']
        if hit_str in hit_list:
            continue

        else:
            hit_list.append(hit_str)

    for item in new_json:
        hit_str = item['api'] + item['repo']
        if hit_str in hit_list:
            continue

        else:
            with open(out_findres, 'a') as f:
                f.write(json.dumps(item))
                f.write('\n')