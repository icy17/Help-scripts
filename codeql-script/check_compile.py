import sys
import os
import json
import csv
from os.path import join, getsize

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

def gen_search_code(path, target_api, filter_list):
    prefix = '''
    /**
 * @name searchapi
 * @description test if target is compiled
 * @kind problem
 * @problem.severity error
//  * @precision high
 * @id cpp/test-compile
 * @tags security
 */

import cpp

from FunctionCall fc, File f
where 
fc.getTarget().hasName("''' + target_api + '''") 
and fc.getFile() = f
'''
    after = '''
    select  fc, fc.getLocation().toString()
    '''
    filter_code = ''
    for filter in filter_list:
        filter_code = filter_code + 'and not f.getBaseName().toString() = "' + filter + '"\n'
    ql_code = prefix + '\n' + filter_code + after
    with open(path, 'w') as f:
        f.write(ql_code)

def get_data_json(in_path):
    out_list = list()
    with open(in_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip('\n')
            one = json.loads(line)
            out_list.append(one)
    return out_list
def read_csv(path):
    with open(path, 'r') as f:
        result = csv.reader(f)
        result = list(result)
    return len(result)

def get_file_size(filepath):

    res = 0
    # 判断输入是文件夹还是文件
    if os.path.isdir(filepath):
        # 如果是文件夹则统计文件夹下所有文件的大小
        for root, dirs, files in os.walk(filepath):
            res += sum([getsize(join(root, name)) for name in files])
    elif os.path.isfile(filepath):
        # 如果是文件则直接统计文件的大小
        res += os.path.getsize(filepath)
    # 格式化返回大小
    # bu = 1024
    # if res < bu:
    #     res = f'{bu}B'
    # elif bu <= res < bu**2:
    #     res = f'{round(res / bu, 3)}KB'
    # elif bu**2 <= res < bu**3:
    #     res = f'{round(res / bu**2, 3)}MB'
    # elif bu**3 <= res < bu**4:
    #     res = f'{round(res / bu**3, 3)}GB'
    # elif bu**4 <= res < bu**5:
    #     res = f'{round(res / bu**4, 3)}TB'
    return res

def if_big(database_path):
    print(database_path)
    res = get_file_size(database_path) / (1024*1024)
    print(str(res) + 'M')
    return res
    # if res > 100:
    #     return True
    # else:
    #     return False

def without_find(database, api_path):
    out = list()
    # i = 0
    with open(api_path, 'r') as f:
        api_list = f.readlines()
    
    for api_line in api_list:
        
        api_pair = list()
        api1 = api_line.split(': ')[0].strip('\n')
        api2 = api_line.split(': ')[1].strip('\n')
        api_pair = api2.split(',')
        for api in api_pair:
            api_dict = dict()
            api_dict['database'] = database
            api_dict['API1'] = api1.strip(' ')
            api_dict['API2'] = api.strip(' ')
            # api_dict['No'] = i
            # print(api1 + ' :' + api)
            out.append(api_dict)
            # i += 1
            # print(out)
    return out

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python3 ./check_compile.py database-dir findres_path out_path')
        exit(1)
    database_dir = sys.argv[1] + '/'
    findres_path = sys.argv[2]
    home_dir = '/root/'

    out_dir = sys.argv[3] + '/'
    ql_dir = home_dir + '/CodeQL/vscode-codeql-starter/codeql-custom-queries-cpp/'
    miss_path = out_dir + '/miss_info'
    # out_dir = sys.argv[4]
    # databases = ['Cinder-bfd0558']
    databases = list()
    databases = read_json(findres_path)
    # with open(findres_path, 'r') as f:
    #     databases = f.readlines()

    # database = 'coturn-3492644'
    # ql_path = '/home/icy/Desktop/CodeQL/'
    in_path = findres_path
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    i = 0
    all_num = len(databases)
    for database_json in databases:
        # database = database.strip('\n')
        # database_name = database.split('-')[0]
        i += 1
        
        print(f'Parse {str(i)}/{str(all_num)}')


        database = database_json['repo']
        database_path = database_dir + database
        print(database_path)
        if not os.path.exists(database_path):
            with open(miss_path, 'a') as f:
                f.write(json.dumps(database_json))
                f.write('\n')
            continue
        output_path = out_dir + '/searchres'
        check_api = database_json['api']
        # ql_out_path = ql_path + '/vscode-codeql-starter/codeql-custom-queries-cpp/' + 'tmp_search.ql'
        # api_path =  "/home/icy/Desktop/data/sqlite_top10/sqlite3_api"
        csv_out = out_dir + '/search-' + database + check_api + '_check.csv'
        # check_out = output_path + '/searchres/' + database
        
        filter_list = []
        # in_path = output_path + '/findres/' + database
        # log_path = output_path + '/searchres/log'

        
        # TODO:debug
        # with_find:
        # data = get_data_json(in_path)
        # without_find:
        # data = without_find(database, api_path)
        # for i in data:
        #     print(i)
        # exit(1)
        # end
        database_log = database_path + '/log/'
        if os.path.exists(database_log):
            rm_cmd = 'rm -rf ' + database_log
            print(rm_cmd)
            os.system(rm_cmd)
        size = if_big(database_path)
        if size > 500:
            big_flag = 'big_'
        else:
            big_flag = ''
        out_dict = database_json
        out_dict['big_flag'] = big_flag
        out_dict['size'] = size
        ql_out_path = ql_dir + '/tmp_search.ql'
        gen_search_code(ql_out_path, check_api, filter_list)
        search_cmd = 'codeql database analyze ' + database_path + ' --rerun --format=csv --output=' + csv_out + ' ' + ql_out_path
        os.system(search_cmd)
        tmp_list = list()
        with open(csv_out, 'r') as f:
            tmp_list = f.readlines()
        nums = len(tmp_list)
        
        files = os.listdir(database_log)
        hit_nums = 0
        for file_name in files:
            file_path = database_log + '/' + file_name 
            if file_name.find('database-analyze') != -1:
                content = ''
                with open(file_path, 'r') as f:
                    content = f.read()
                hit_nums = content.count('[SPAMMY] database interpret-results> Skipping location')
                print(hit_nums)
                break
                # end_index = content.rfind('since it is outside the source archive.')
                # find_search = content.find('Interpreted problem query "searchapi"')
        nums = max(hit_nums, nums)
        out_dict['nums'] = nums
        if nums != 0:
            with open(output_path, 'a') as f:
                f.write(json.dumps(out_dict))
                f.write('\n')
        os.remove(csv_out)
        # i += 1
        # if i == 10:
        #     exit(1)
        # break
        # for info in data:
        #     out_info = dict()
            
        #     out_info['database'] = database
        #     out_info['database_path'] = database_path
        #     # out_info['']
        #     if info['repo'] != database_name:
        #         continue
        #     api_list = info['api']
        #     for check_api in api_list:
        #     # check_api = info['API1']
        #         # info['bigflag'] = big_flag
        #         out_info['bigflag'] = big_flag
        #         out_info['size'] = size
        #         out_info['API1'] = check_api
        #         out_info['API2'] = get_api2(check_api, api_path)
        #         gen_search_code(ql_out_path, check_api, filter_list)
        #     # codeql database analyze /home/icy/Desktop/CodeQL//database/coturn-3492644 --rerun --format=csv --output=/home/icy/Desktop/CodeQL//output/coturn-3492644.csv --ram=1024 /home/icy/Desktop/CodeQL//vscode-codeql-starter/codeql-custom-queries-cpp/search_api.ql
        #         search_cmd = 'codeql database analyze ' + database_path + ' --rerun --format=csv --output=' + csv_out + ' --ram=1024 ' + ql_out_path
        #         os.system(search_cmd)
        #         if not os.path.exists(csv_out):
        #             print('no csv out search error!\n')
        #             with open(log_path, 'a') as f:
        #                 f.write('cant find ' + csv_out + '\n')
        #             continue
        #         if os.path.getsize(csv_out) != 0:
        #             print(check_api + ' exists!')
        #         else:
        #             print(check_api + ' not exists!')
        #             continue
        #         times = read_csv(csv_out)
        #         log_out = database + ' find api:' + check_api + ': ' + str(times) + '\n\n'
        #         with open(log_path, 'a') as f:
        #             f.write(log_out)
        #         with open(check_out, 'a') as f:
        #             f.write(json.dumps(out_info))
        #             f.write('\n')
        #         print(search_cmd)
        #         # if os.path.exists(csv_out):
        #         #     os.remove(csv_out)
        #     # break
        #     # remove csv out:
