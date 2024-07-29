from genericpath import isfile
import os
import sys
from os.path import join, getsize
import subprocess
# import openpyxl
# from  openpyxl import  Workbook 
# from openpyxl  import load_workbook
import time
import json

def get_time():
    time_str = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()) + '\n'
    return time_str

def get_file_content(in_path):
    tmp_content = ''
    with open(in_path) as f:
        tmp_content = f.read()
    return tmp_content

def get_data_json(in_path):
    out_list = list()
    with open(in_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip('\n')
            one = json.loads(line)
            out_list.append(one)
    return out_list

# def get_data_excel(in_path):
#     wb= openpyxl.load_workbook(in_path)
# # 第二步选取表单
#     sheet = wb.active
# # 按行获取数据转换成列表
#     rows_data = list(sheet.rows)
# # 获取表单的表头信息(第一行)，也就是列表的第一个元素
#     titles = [title.value for title in rows_data.pop(0)]
#     # print(titles)

# # 整个表格最终转换出来的字典数据列表
#     all_row_dict = []
#     # 遍历出除了第一行的其他行
#     for a_row in rows_data:
#         the_row_data = [cell.value for cell in a_row]
#         # 将表头和该条数据内容，打包成一个字典
#         row_dict = dict(zip(titles, the_row_data))
#         # print(row_dict)
#         all_row_dict.append(row_dict)
#     return all_row_dict

def get_file_size(filepath):

    res = 0
    if not os.path.exists(filepath):
        print(filepath + ' not exists!')
        # print('\n')
        exit(1)
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
    if res > 500:
        return True
    else:
        return False

# ql_code: orig parameter-value-check.ql
# target_api: api used
# target_index: api parameter index.
def gen_parameter_check_ql(ql_code, target_api, target_index):
    target_api_str = 'fc.getTarget().hasName("' + target_api + '")'
    target_index_str = 'result = fc.getArgument(' + str(target_index) + ')'
    ql_code = ql_code.replace('fc.getTarget().hasName("SSL_CTX_set_options")', target_api_str)
    ql_code = ql_code.replace('result = fc.getArgument(0) ', target_index_str)
    return ql_code

def gen_missing_free_ql(ql_code, target_api, target_index, free_list):
    ql_code = ql_code.replace('Target_Malloc', target_api)
    ql_code = ql_code.replace('Target_INDEX', str(target_index))
    free_str = 'fc.getTarget().hasName("free")'
    for free_api in free_list:
        free_api = free_api['api']
        free_str = free_str + '\nor fc.getTarget().hasName("' + free_api + '")'

    ql_code = ql_code.replace('fc.getTarget().hasName("free")', free_str)
    return ql_code

def gen_missing_malloc_ql(ql_code, target_api, target_index, malloc_dict_list):
    ql_code = ql_code.replace('Target_Free', target_api)
    ql_code = ql_code.replace('Target_INDEX', str(target_index))
    malloc_str = '(fc.getTarget().hasName("malloc_with_parameter") and e = fc)'
    malloc_str2 = 'fc.getTarget().hasName("malloc")'
    for malloc_item in malloc_dict_list:
        malloc_api = malloc_item['api']
        malloc_index = malloc_item['index']
        
        malloc_str = malloc_str + '\n or (fc.getTarget().hasName("' + malloc_api + '") and e = fc.getArgument(' + str(malloc_index) + '))'
        malloc_str2 = malloc_str2 + '\n or fc.getTarget().hasName("' + malloc_api + '")'
    ql_code = ql_code.replace('(fc.getTarget().hasName("malloc_with_parameter") and e = fc)', malloc_str)
    ql_code = ql_code.replace('fc.getTarget().hasName("malloc")', malloc_str2)
    ql_code = ql_code.replace('malloc_with_parameter', 'malloc')
    return ql_code

def gen_double_free_ql(ql_code, target_api, target_index, malloc_dict_list):
    ql_code = ql_code.replace('Target_Free', target_api)
    ql_code = ql_code.replace('Target_INDEX', str(target_index))
    malloc_str = '(fc.getTarget().hasName("malloc_with_parameter") and e = fc)'
    malloc_str2 = 'fc.getTarget().hasName("malloc")'
    for malloc_item in malloc_dict_list:
        malloc_api = malloc_item['api']
        malloc_index = malloc_item['index']
        
        malloc_str = malloc_str + '\n or (fc.getTarget().hasName("' + malloc_api + '") and e = fc.getArgument(' + str(malloc_index) + '))'
        malloc_str2 = malloc_str2 + '\n or fc.getTarget().hasName("' + malloc_api + '")'
    ql_code = ql_code.replace('(fc.getTarget().hasName("malloc_with_parameter") and e = fc)', malloc_str)
    ql_code = ql_code.replace('fc.getTarget().hasName("malloc")', malloc_str2)
    ql_code = ql_code.replace('malloc_with_parameter', 'malloc')
    return ql_code

def gen_uaf_ql(ql_code, target_api, target_index, malloc_dict_list, free_list):
    ql_code = ql_code.replace('Target_API', target_api)
    ql_code = ql_code.replace('Target_INDEX', str(target_index))
    malloc_str = '(fc.getTarget().hasName("malloc_parameter") and e = fc)'
    malloc_str2 = 'fc.getTarget().hasName("malloc")'
    for malloc_item in malloc_dict_list:
        malloc_api = malloc_item['api']
        malloc_index = malloc_item['index']
        
        malloc_str = malloc_str + '\n or (fc.getTarget().hasName("' + malloc_api + '") and e = fc.getArgument(' + str(malloc_index) + '))'
        malloc_str2 = malloc_str2 + '\n or fc.getTarget().hasName("' + malloc_api + '")'
    ql_code = ql_code.replace('(fc.getTarget().hasName("malloc_parameter") and e = fc)', malloc_str)
    ql_code = ql_code.replace('fc.getTarget().hasName("malloc")', malloc_str2)
    ql_code = ql_code.replace('malloc_parameter', 'malloc')
    
    free_str = 'fc.getTarget().hasName("free")'
    for free_api in free_list:
        free_api = free_api['api']
        free_str = free_str + '\n or fc.getTarget().hasName("' + free_api + '")'
    ql_code = ql_code.replace('fc.getTarget().hasName("free")', free_str)
    return ql_code


def gen_uninitialize_ql(ql_code, target_api, target_index, initialize_dict_list):

    ql_code = ql_code.replace('Target_API', target_api)
    ql_code = ql_code.replace('Target_INDEX', str(target_index))
    malloc_str = '(fc.getTarget().hasName("initialize_expr") and e = fc.getAnArgument())'
    malloc_str2 = 'fc.getTarget().hasName("initialize")'
    for malloc_item in initialize_dict_list:
        malloc_api = malloc_item['api']
        # malloc_index = malloc_item['index']
        
        malloc_str = malloc_str + '\n or (fc.getTarget().hasName("' + malloc_api + '") and e = e = fc.getAnArgument())'
        malloc_str2 = malloc_str2 + '\n or fc.getTarget().hasName("' + malloc_api + '")'
    ql_code = ql_code.replace('(fc.getTarget().hasName("initialize_expr") and e = fc.getArgument(0))', malloc_str)
    ql_code = ql_code.replace('fc.getTarget().hasName("initialize")', malloc_str2)
    return ql_code

def sort_by_size(database_list, database_dir):
    size_dict = dict()
    size_list = list()
    out_list = list()
    for data in database_list:
        # database_path = database_dir +  '/all-database' + '/' + data['repo']
        # size_res = get_file_size(database_path) / (1024*1024)
        size_dict[data['repo']] = data['size']
        # size_dict['size'] = size_res
        # size_list.append(size_dict)
    for key in size_dict.keys():
        tmp_dict = dict()
        tmp_dict['repo'] = key
        tmp_dict['size'] = size_dict[key]
        size_list.append(tmp_dict)
    size_list.sort(key=lambda k: (k.get('size', 0)))
    print(size_list)
    # exit(1)
    for size_item in size_list:
        repo = size_item['repo']
        for data in database_list:
            if data['repo'] == repo:
                data['size'] = size_item['size']
                out_list.append(data)
    for item in out_list:
        print(item['repo'] + ' size: ' + str(item['size']))
    # exit(1)
    return out_list

def gen_ql_code(rule_dict, free_dict, malloc_dict, init_dict, ql_dict, api, lib):
    rule = rule_dict['rule']
    index = rule_dict['index']
    # if rule != 'malloc-missing-free' and rule != 'free-missing-malloc':
    #     return ''
    
    if rule == 'parameter-check':
        ql_code = gen_parameter_check_ql(ql_dict['parameter-check'], api, index)
    elif rule == 'malloc-missing-free':
        ql_code = gen_missing_free_ql(ql_dict['malloc-missing-free'], api, index, free_dict[lib])
        # ql_code = ''
        # # TODO gt 不检测这两种
    elif rule == 'free-missing-malloc':
        
        ql_code = gen_missing_malloc_ql(ql_dict['free-missing-malloc'], api, index, malloc_dict[lib])
        # ql_code = ''
        # # TODO gt 不检测这两种
    elif rule == 'uninitialize':
        ql_code = gen_uninitialize_ql(ql_dict['uninitialize'], api, index, init_dict[lib])
    elif rule == 'uaf':
        ql_code = gen_uaf_ql(ql_dict['uaf'], api, index, malloc_dict[lib], free_dict[lib])
    elif rule == 'double-free':
        ql_code = gen_double_free_ql(ql_dict['double-free'], api, index, malloc_dict[lib])
    else:
        ql_code = ''
    return ql_code

if __name__ == '__main__':
    print('Usage: python3 ./auto_detect.py <in_dir> <output_dir> <database_dir>\n in_dir should contain: searchres, free_API, malloc_API, initialize_API, api_rule and ql_template/xxx.ql')
    # in_list = 'list'
    # #in Ubuntu 18.04(vmware)
    # ql_dir = '/home/jhliu/Desktop/CodeQL/vscode-codeql-starter/codeql-custom-queries-cpp/'
    # database_dir = codeql_dir + '/database/'
    # ql_dir = codeql_dir + '/vscode-codeql-starter/codeql-custom-queries-cpp/'
    # out_dir = codeql_dir + '/output/gtout/'
    # log_path = out_dir + 'log'
    # in_path = out_dir + in_list

    # # in windows
    # # codeql_dir = '/home/icy/Desktop/CodeQL/'
    # database_dir = 'E:/win-database/'
    # ql_dir = 'D:/CGit/vscode-codeql-starter/codeql-custom-queries-cpp/'
    # out_dir = 'D:/CGit/output/gtout/'
    # log_path = out_dir + 'log'
    # in_path = out_dir + in_list

     #in UOS (vmware)
    if len(sys.argv) != 4:
        print('wrong input arg')
        print('Usage: python3 ./auto_detect.py <in_dir> <output_dir> <database_dir>')
        exit(1)
    
    # codeql_dir = '/home/icy/Desktop/CodeQL/'
    # out_dir = codeql_dir + '/output/'
    # in_list = 'list'
    # codeql_dir = sys.argv[1] + '/'
    out_dir = sys.argv[2] + '/'
    in_dir = sys.argv[1]
    
    database_dir = sys.argv[3] + '/'
    
    in_path = in_dir + '/searchres'
    # [{api, index, lib}]
    free_path = in_dir + 'free_API'
    # [api, index, lib]
    malloc_path = in_dir + '/malloc_API'
    # [api, index, lib]
    initialize_path = in_dir + '/initialize_API'
    # [api, rule_list({'parameter-check': 1}), lib]
    api_rule_path = in_dir + '/api_rule'
    
    ql_template_dir = in_dir + '/ql_template'
    parameter_check_ql = ql_template_dir + '/parameter-value-check.ql'
    malloc_missing_free_ql = ql_template_dir + '/malloc-missing-free.ql'
    free_missing_malloc_ql = ql_template_dir + '/free-missing-malloc.ql'
    uninitialize_ql = ql_template_dir + '/uninitialize.ql'
    double_free_ql = ql_template_dir + '/double-free.ql'
    uaf_ql = ql_template_dir + '/use-after-free.ql'
    ql_dir = '/root/CodeQL/vscode-codeql-starter/codeql-custom-queries-cpp/'
    log_path = out_dir + '/detect_log'
    fail_log = out_dir + '/faild_log'
    
    # get input
    ql_dict = dict()
    ql_dict['malloc-missing-free'] = get_file_content(malloc_missing_free_ql)
    ql_dict['parameter-check'] = get_file_content(parameter_check_ql)
    ql_dict['free-missing-malloc'] = get_file_content(free_missing_malloc_ql)
    ql_dict['uninitialize'] = get_file_content(uninitialize_ql)
    ql_dict['uaf'] = get_file_content(uaf_ql)
    ql_dict['double-free'] = get_file_content(double_free_ql)
    
    free_list = get_data_json(free_path)
    malloc_list = get_data_json(malloc_path)
    init_list = get_data_json(initialize_path)
    api_rule_list = get_data_json(api_rule_path)
    
    target_libs = ['openssl', 'libpcap', 'sqlite3', 'libxml2']
    # api_rule_dict['lib']['api']是rule_list
    api_rule_dict = dict()
    # malloc_dict['lib']是api dict list
    malloc_dict = dict()
    free_dict = dict()
    init_dict = dict()
    
    all_dict = dict()
    
    for lib in target_libs:
        malloc_dict[lib] = list()
        free_dict[lib] = list()
        init_dict[lib] = list()
        api_rule_dict[lib] = dict()
    
    for item in api_rule_list:
        lib = item['lib']
        api = item['api']
        rule_list = item['rule_list']

        if lib not in api_rule_dict.keys():
            api_rule_dict[lib] = dict()
            api_rule_dict[lib][api] = rule_list
        else:
            api_rule_dict[lib][api] = rule_list
    for item in malloc_list:
        lib = item['lib']
        api = item['api']
        index = item['index']
        in_dict = dict()
        in_dict['api'] = api
        in_dict['index'] = index
        if lib not in malloc_dict.keys():
            malloc_dict[lib] = list()
            
            malloc_dict[lib].append(in_dict)
        else:
            malloc_dict[lib].append(in_dict)
    
    for item in free_list:
        lib = item['lib']
        api = item['api']
        index = item['index']
        in_dict = dict()
        in_dict['api'] = api
        in_dict['index'] = index
        if lib not in free_dict.keys():
            free_dict[lib] = list()
            
            free_dict[lib].append(in_dict)
        else:
            free_dict[lib].append(in_dict)
            
    for item in init_list:
        lib = item['lib']
        api = item['api']
        # index = item['index']
        in_dict = dict()
        in_dict['api'] = api
        # in_dict['index'] = index
        if lib not in init_dict.keys():
            init_dict[lib] = list()
            
            init_dict[lib].append(in_dict)
        else:
            init_dict[lib].append(in_dict)
    print(free_dict)
    print(malloc_dict)
    print(init_dict)
    print(api_rule_dict)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    # in_path = in_list
    # codeql database analyze ./database/libspatialite-5fb62fc-small --rerun --format=csv --output=./output/libspatialite-5fb62fc-small.csv --ram=2048 ./vscode-codeql-starter/codeql-custom-queries-cpp/search_api.ql
    data = get_data_json(in_path)
    data = sort_by_size(data, database_dir)
    
    # for data_json in data:
    #     print(data_json)
    # excel_path = './test.xlsx'


    # data = get_data_excel(excel_path)
    # # print(data)
    # os.chdir('D:/CGit/codeql')
    out_csv_list = list()
    # cal all-query nums:
    all_nums = 0
    for database in data:
        database_name = database['repo']
        
        database_path = database_dir +  '/' + database_name
        
        if not os.path.exists(database_path):
            continue
        
        api = database['api']
        # if api != 'DH_free':
        #     continue
        lib = database['lib']
        if lib not in api_rule_dict.keys():
            continue
        if api not in api_rule_dict[lib].keys():
            continue
        rules = api_rule_dict[lib][api]
        all_nums += len(rules)
    i = 0
    for database in data:
        # if database['Check'] == 1:
        #     continue
        database_name = database['repo']
        # if database_name != 'openssl-bc5d9cc871':
        #     continue
        database_path = database_dir +  '/' + database_name
        
        if not os.path.exists(database_path):
            out_dict = dict()
            out_dict = database
            out_dict['rule'] = ''
            out_dict['reason'] = 'no-database'
            with open(fail_log + '-database', 'a') as f:
                f.write(json.dumps(out_dict))
                f.write('\n')
            continue
        
        api = database['api']
        # if api != 'NCONF_free':
        #     continue
        lib = database['lib']
        if lib not in api_rule_dict.keys():
            out_dict = dict()
            out_dict = database
            out_dict['rule'] = ''
            out_dict['reason'] = 'no-rule'
            with open(fail_log + '-rule', 'a') as f:
                f.write(json.dumps(out_dict))
                f.write('\n')
            continue
        if api not in api_rule_dict[lib].keys():
            out_dict = dict()
            out_dict = database
            out_dict['rule'] = ''
            out_dict['reason'] = 'no-rule'
            with open(fail_log + '-rule', 'a') as f:
                f.write(json.dumps(out_dict))
                f.write('\n')
            continue
        rules = api_rule_dict[lib][api]
        for rule in rules:
            i += 1
            print(f'{str(i)}/{str(all_nums)}')
            ql_code = gen_ql_code(rule, free_dict, malloc_dict, init_dict, ql_dict, api, lib)
            if ql_code == '':
                out_dict = dict()
                out_dict = database
                out_dict['rule'] = rule
                out_dict['reason'] = 'no-ql-code'
                with open(fail_log + '-ql-code', 'a') as f:
                    f.write(json.dumps(out_dict))
                    f.write('\n')
                continue
            ql_path = ql_dir + '/tmp.ql'
            with open(ql_path, 'w') as f:
                f.write(ql_code + '\n')
            # exit(1)
        # database['path'] = database_path
        # if database['size'] > 550:
        #     big_flag = True
        # else:
        #     big_flag  = False
        # big_flag = False
        # ql_path = gen_ql_code(ql_dir, big_flag, database)
        # ql_name = database['bigflag'] + database['API1'] + '-' + database['API2'] + '.ql'
        # ql_path = ql_dir + '/' + ql_names
        # if not big_flag:
            out_csv_path = out_dir +  '/' + database_name + '-' + database['api'] + '-' + rule['rule'] + str(rule['index']) + '.csv '
        # else:
        #     out_csv_path = out_dir + 'big_' + database_name + '-' + database['malloc_api'] + '-' + database['free_api'] + '.csv '

        
        # codeql_analyze = 'codeql database analyze ' + database_path + ' --rerun --format=csv --output=' + out_dir + database['bigflag'] + database_name + database['API1'] +'.csv --ram=2048 --threads=2 ' + ql_path
            codeql_analyze = 'codeql database analyze ' + database_path + ' --rerun --threads=4 --format=csv --output=' + out_csv_path + ql_path
            with open(log_path, 'a') as f:
                f.write(get_time() + 'Execute codeql analyze:\n' + codeql_analyze + '\n')
            start = time.time()
            database_log = database_path + '/log/'
            os.system('rm -rf ' + database_log)
            # change to subprocess set timeout TODO
            return_info = subprocess.Popen(codeql_analyze, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                out, err = return_info.communicate()
            except:
                out_dict = dict()
                out_dict = database
                out_dict['rule'] = rule
                out_dict['reason'] = 'timeout'
                with open(fail_log, 'a') as f:
                    f.write(json.dumps(out_dict))
                    f.write('\n')
                with open(log_path, 'a') as f:
                    f.write('Cost too much time. Break!\n\n')
                # os.remove(ql_path)
                continue
            info = out.decode("utf-8","ignore") + '\n' + err.decode("utf-8","ignore")
            print(info)
            end = time.time()
            if return_info.returncode != 0:
                # exit(1)
                out_dict = dict()
                out_dict = database
                out_dict['rule'] = rule
                out_dict['reason'] = info
                with open(fail_log, 'a') as f:
                    f.write(json.dumps(out_dict))
                    f.write('\n')
                with open(log_path, 'a') as f:
                    f.write(out_dict['reason'] + '\n\n')
                # os.remove(ql_path)
                continue
            
            with open(log_path, 'a') as f:
                f.write('Total time: ' + str(end-start) + 's\n\n')
            print(codeql_analyze)
            if not os.path.exists(database_log):
                    continue
            files = os.listdir(database_log)
            for file_name in files:
                print(file_name)
                if file_name.find('database-analyze') == -1:
                    continue
                dlog_path = database_log + file_name
                content = ''
                with open(dlog_path, 'r') as f:
                    content = f.read()
                str_index = content.find('[SPAMMY] database interpret-results> Skipping location')
                end_index = content.rfind('since it is outside the source archive.')
                find_search = content.find('Interpreted problem query "searchapi"')
                if find_search != -1:
                    continue
                path_index = content.find('Interpreted problem query')
                path_line = content[path_index:-1].split('\n')[0]
                api_info = path_line.split('/')[-1].replace('.ql.', '')
                out_path = out_csv_path.strip('.csv') + 'skip'
            if str_index != -1:
                name_index = ''
                
                test = content[str_index: end_index + len('since it is outside the source archive.') + 1]
                with open(out_path, 'a') as f:
                    f.write(test +'\n')
            # os.remove(ql_path)
            # exit(1)
            
            # out_csv_list.append(out_csv_path)
    # time.sleep(60)
    # for out_csv_path in out_csv_list:
    #     # if not os.path.exists(out_csv_path):
    #     #     continue
    #     if os.path.exists(out_csv_path):
    #         if os.path.getsize(out_csv_path) != 0:
    #             print('Remove out file: ' + out_csv_path)
    #             os.remove(out_csv_path)
    #             with open(log_path, 'a') as f:
    #                 f.write(f'No wrong result! Delete out csv file: {out_csv_path}\n')
        # break




