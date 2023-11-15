import csv
import json
import os.path
import sys

def gen_csv(in_list, out_csv):
    in_content = list()
    with open(in_list, 'r') as f:
        in_content = f.readlines()
    list_info = list()
    for data in in_content:
        data = data.strip('\n')
        json_data = json.loads(data)
        # new_dict = dict()
        # new_dict['function'] = json_data['Function']
        # new_dict['lib'] = json_data['Lib']
        # if 'Parsed_Rule' not in json_data.keys():
        #     new_dict['final_rule'] = []
        #     new_dict['final_rule_num'] = 0
        # else:
        #     new_dict['final_rule'] = json_data['Parsed_Rule']
        #     new_dict['final_rule_num'] = len(json_data['Parsed_Rule'])
        for key in json_data.keys():
            if type(json_data[key]) == str:
                json_data[key] = json_data[key].replace('\n', '\t')
        # del json_data['Right_Code']
        # json_data['apiname'] = json_data['apiname'].strip('\n')
        list_info.append(json_data)
    header = list(list_info[0].keys())
    with open(out_csv, 'a', newline='') as f:
        writer = csv.DictWriter(f,fieldnames=header) # 提前预览列名，当下面代码写入数据时，会将其一一对应。
        writer.writeheader()  # 写入列名
        writer.writerows(list_info) # 写入数据

if __name__ == '__main__':
    in_path = sys.argv[1]
    # in_list = '/root/data/api-data/gt-expr-107/icy17BioM-ELECTRA-Large-SQuAD2-finetune/orig-all_result'
    # in_list = '/root/api_pair/data/keyword-result/'
    # libs = ['libxml2', 'libzip', 'zlib']
    libs = ['all']
    # libs = ['ldap', 'libpcap', 'libmysql', 'zlib', 'ffmpeg', 'libexpat', 'libzip', 'libxml2', 'libdbus']
    # libs = ['ldap','ffmpeg', 'libexpat', 'libpcap', 'libxml2']
    # libs = ['glib', 'libzip', 'zlib', 'libmysql', 'openssl']
    for lib in libs:
        # in_path = in_list + lib
        # in_path = in_list + lib + '-qa-parsepara-skip'
        # in_path = in_list + lib + '-qa'
        # header = ['']
        # if not os.path.exists(in_path):
        #     continue
        gen_csv(in_path, in_path+ '.csv')