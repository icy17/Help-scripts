from genericpath import isfile
import os
import sys
from os.path import join, getsize
# import openpyxl
# from  openpyxl import  Workbook 
# from openpyxl  import load_workbook
import time
import json

def get_time():
    time_str = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()) + '\n'
    return time_str

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

def gen_ql_code(ql_dir, big_flag, database):
    ql_path = ql_dir + '/'
    ql_name = database['malloc_api'] + '-' + database['free_api'] + '.ql'
    ql_path = ql_dir + '/' + ql_name
    # ql_path2 = ql_dir + '/big_' + ql_name
    ql_prefix = ql_dir + '/prefix.ql'
    # backup_dir = ql_dir + '/oldbak/'
    if big_flag:
        ql_after = ql_dir + '/big_after.ql'
    else:
        ql_after = ql_dir + '/after.ql'

    # ql_after_big = ql_dir + '/big_after.ql'
    
    # ql_after = ql_dir + '/after.ql'
    # if os.path.isfile(ql_path):
        
    #     mv_cmd = 'mv ' + ql_path + ' ' + backup_dir
    #     os.system(mv_cmd)
    #     with open(log_file, 'a') as f:
    #         f.write('Execute MV:' + mv_cmd + '\n\n')
    # if os.path.isfile(ql_path2):
        
    #     mv_cmd = 'mv ' + ql_path2 + ' ' + backup_dir
    #     os.system(mv_cmd)
    #     with open(log_file, 'a') as f:
    #         f.write('Execute MV:' + mv_cmd + '\n\n')
    source_exp = int(database['malloc_index'])
    sink_exp = int(database['free_index'])
    sourceFC = database['malloc_api'].strip(' ')
    sinkFC = database['free_api'].strip(' ')
    ifflag = 'false'
    # filter_list_raw = database['filter']
    filter_list = list()
    # if filter_list_raw:
    #     filter_list = filter_list_raw.split(', ')
    if ifflag:
        flag = 'true'
    else:
        flag = 'false'
    print(ql_name)
    if source_exp == -1:
        change_sourcefc = '''
        Expr getSourceExpr(FunctionCall fc)
    {
    result = fc //sqlite3_open
    }
    '''
    else:
        change_sourcefc = '''
        Expr getSourceExpr(FunctionCall fc)
    {
    result = fc.getArgument(''' + str(source_exp) +''')
    }
    '''
    
    change_code = change_sourcefc + '''
    Expr getSinkExp(FunctionCall fc)
    {
    result = fc.getArgument(''' + str(sink_exp) +''') 
    }

    predicate isSourceFC(FunctionCall fc)
    {
    fc.getTarget().hasName("''' + sourceFC + '''")
    }

    predicate isSinkFC(FunctionCall fc)
    {
    fc.getTarget().hasName("''' + sinkFC + '''")
    }
    boolean ifTestFlag()
    {
    result = ''' + flag + '''
    }
     '''
    filter_code = ''
    # if filter_list_raw:
    #     for filter in filter_list:
    #         filter = filter.strip('\n')
    #         filter = filter.strip(' ')
    #         filter_code = filter_code + 'and not f.getBaseName().toString() = "' + filter + '"\n'
    final_code = filter_code + 'select malloc, malloc.getLocation().toString()\n'
    with open(ql_prefix, 'r') as f:
        prefix = f.read()
    with open(ql_after, 'r') as f:
        after = f.read()
    # with open(ql_after_big, 'r') as f:
    #     after_big = f.read()
    qlcode = prefix + change_code + after
    with open(ql_path, 'w') as f:
        f.write(qlcode + final_code)
    # with open(log_file, 'a') as f:
    #         f.write(get_time() + 'Create a QL code:' + ql_path + '\n\n')
    # with open(ql_path2, 'w') as f:
    #     f.write(prefix + change_code + after_big + final_code)
    # with open(log_file, 'a') as f:
    #         f.write(get_time() + 'Create a QL code:' + ql_path2 + '\n\n')
    return ql_path
    
def sort_by_size(database_list, database_dir):
    size_dict = dict()
    size_list = list()
    out_list = list()
    for data in database_list:
        database_path = database_dir +  '/all-database' + '/' + data['repo']
        size_res = get_file_size(database_path) / (1024*1024)
        size_dict[data['repo']] = size_res
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

if __name__ == '__main__':
    # in_list = 'list'
    # #in Ubuntu 18.04(vmware)
    # codeql_dir = '/home/icy/Desktop/CodeQL/'
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
    if len(sys.argv) != 5:
        print('wrong input arg')
        print('Usage: python3 ./auto_detect.py <codeql_dir> <findres> <output_dir> <database_dir>')
        exit(1)
    
    # codeql_dir = '/home/icy/Desktop/CodeQL/'
    # out_dir = codeql_dir + '/output/'
    # in_list = 'list'
    codeql_dir = sys.argv[1] + '/'
    out_dir = sys.argv[3] + '/'
    in_path = sys.argv[2]

    database_dir = sys.argv[4] + '/'
    ql_dir = codeql_dir + '/vscode-codeql-starter/codeql-custom-queries-cpp/'
    log_path = out_dir + '/detect_log'
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
    for database in data:
        # if database['Check'] == 1:
        #     continue
        database_name = database['repo']
        database_path = database_dir +  '/all-database' + '/' + database_name
        # database['path'] = database_path
        if database['size'] > 550:
            big_flag = True
        else:
            big_flag  = False
        # big_flag = False
        ql_path = gen_ql_code(ql_dir, big_flag, database)
        # ql_name = database['bigflag'] + database['API1'] + '-' + database['API2'] + '.ql'
        # ql_path = ql_dir + '/' + ql_name
        if not big_flag:
            out_csv_path = out_dir + database_name + database['malloc_api'] + '-' + database['free_api'] + '.csv '
        else:
            out_csv_path = out_dir + 'big_' + database_name + '-' + database['malloc_api'] + '-' + database['free_api'] + '.csv '

        
        # codeql_analyze = 'codeql database analyze ' + database_path + ' --rerun --format=csv --output=' + out_dir + database['bigflag'] + database_name + database['API1'] +'.csv --ram=2048 --threads=2 ' + ql_path
        codeql_analyze = 'codeql database analyze ' + database_path + ' --rerun --threads=4 --format=csv --output=' + out_csv_path + ql_path
        with open(log_path, 'a') as f:
            f.write(get_time() + 'Execute codeql analyze:\n' + codeql_analyze + '\n')
        start = time.time()
        os.system(codeql_analyze)
        end = time.time()
        with open(log_path, 'a') as f:
            f.write('Total time: ' + str(end-start) + 's\n\n')
        print(codeql_analyze)
        # exit(1)
        os.remove(ql_path)
        out_csv_list.append(out_csv_path)
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




