import os
import json
import sys
import subprocess
from cinspector.interfaces import CCode, CFile
from cinspector.analysis import CallGraph
from cinspector.nodes import CompoundStatementNode, DeclarationNode, IfStatementNode,Edit, AssignmentExpressionNode, IdentifierNode, InitDeclaratorNode, ParenthesizedExpressionNode, FunctionDefinitionNode


# 获取所有的standard API名，这些API是已经准备好的，在固定位置，如果没有的话会报错退出
def get_standart_list():
    standard_API_path = '/root/data/API-list/standardC'
    out_list = list()
    with open(standard_API_path, 'r') as f:
        out_list = f.read().split('\n')
    return out_list

# 在in_dir目录下寻找所有后缀为suffix的文件并以列表形式返回,suffix_list示例：['.c', '.cpp']
def get_file_by_suffix(in_dir, suffix_list):
    out_list = list()
    os.chdir(in_dir)
    print(in_dir)
    # find /home/icy/Desktop/data/top10/openssl -regex ".*\.cpp\|.*\.c\|.*\.h" | xargs grep -ri "SSL_" -l >> ../openssl_find
    find_prefix = 'find . -regex "'
    find_cmd = find_prefix
    for suffix in suffix_list:
        find_cmd = find_cmd + '.*\\' + suffix + '\\|'
    find_cmd = find_cmd.strip('\\|') + '"'
    # find_cmd = 'find . -regex ' + '".*\\.cpp\\|.*\\.c\\|.*\\.h\\|.*\\.cxx\\|.*\\.cc\\|.*\\.C\\|.*\\.c++" | xargs grep -ri "' + find_api + '"'
    print(find_cmd)
    output = subprocess.getstatusoutput(find_cmd)
    # print(output)
    if output[0] != 0 and output[0] != 123:
        print(find_cmd)
        print("find cmd faild")
        exit(1)
    if output[1] != '':
        out_list = output[1].split('\n')
    # print(out_list)
    # exit(1)
    return out_list

# DEBUG
# 找到file_path对应的所有有函数定义的函数，以列表形式返回func名
def get_def_func(file_path):
    out_list = list()
    code = ''
    ast_type = 'function_definition'
    with open(file_path, 'r') as f:
        code = f.read()
    cc = CCode(code)
    # print(file_path)
    # print(code)
    target_list = cc.get_by_type_name(ast_type)
    for target in target_list:
        # print(target)
        if not target.name:
            continue
        function_name = target.name.src
        out_list.append(function_name)
        # exit(1)
    return out_list

# 找到file_path对应的所有有函数定义的函数，以列表形式返回func名
def get_def_macro(file_path):
    out_list = list()
    code = ''
    ast_type = 'preproc_def'
    ast_type2 = 'preproc_function_def'
    with open(file_path, 'r') as f:
        code = f.read()
    cc = CCode(code)
    # print(file_path)
    # print(code)
    target_list = cc.get_by_type_name(ast_type)
    for target in target_list:
        # print(target)
        function_name = target.name.src
        out_list.append(function_name)
        # exit(1)
    target_list = cc.get_by_type_name(ast_type2)
    for target in target_list:
        # print(target)
        function_name = target.name.src
        out_list.append(function_name)
    return out_list

# DEBUG
# 找到file_path对应的所有fc，以列表形式返回func名
def get_fc(file_path):
    out_list = list()
    code = ''
    ast_type = 'call_expression'
    with open(file_path, 'r') as f:
        code = f.read()
    cc = CCode(code)
    target_list = cc.get_by_type_name(ast_type)
    for target in target_list:
        # print(target)
        if not target.function or target.is_indirect():
            continue
        function_name = target.function.src
        # print(function_name)
        out_list.append(function_name)
    return out_list

# 获取一个repo里所有可能的API
# 这个过滤可能导致部分API被滤掉（如果该API在函数内有定义，比如sqlite3
if __name__ == '__main__':
    if len(sys.argv) != 3:
        # python3 ./get_API.py ~/repos/FFmpeg/ ~/output/patch_parse/
        print('Wrong Input!\nUsage: python3 ./get_API.py <repo_dir> <out_dir>')
        exit(1)
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    repo_name = in_dir.strip('/').split('/')[-1]
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    log_json = out_dir + '/API-info'
    # 存放一个file里的所有API
    file_api_json = out_dir + '/file-API'
    api_path = out_dir + '/' + repo_name + '-apilist'
    standard_API = get_standart_list()
    
    
    # 获取所有.c .cpp文件（filec）
    filec_list = get_file_by_suffix(in_dir, ['.c', '.cpp', '.h'])
    # 获取所有.c .cpp,.h文件（filehc）
    filehc_list = get_file_by_suffix(in_dir, ['.c', '.cpp', '.h'])
    # 获取所有 有函数定义的函数（func-def）def_func_list: [{func: '', declaration: ''}]
    def_func_list = list()
    all_num = len(filec_list)
    i = 0
    for filec in filec_list:
        # print(filec)
        i += 1
        print('Parse first step: ' + str(i) + ' / ' + str(all_num))
        tmp_list = get_def_func(filec)
        def_func_list.extend(tmp_list)
        tmp_list2 = get_def_macro(filec)
        # print(tmp_list2)
        
        def_func_list.extend(tmp_list2)
    # exit(1)
    # 获取所有函数调用（fc）[{func: '', declaration: ''}]
    fc_list = list()
    all_num = len(filehc_list)
    i = 0
    for filehc in filehc_list:
        print(filehc)
        i += 1
        print('Parse second step: ' + str(i) + ' / ' + str(all_num))
        tmp_list = get_fc(filehc)
        fc_list.extend(tmp_list)
        
    # 对每个fc，找是否有对应的func-def，如果1.没有2.不是标准库函数，说明该func可能为API
    file_api_list = list()
    print('wait for match...')
    for func in fc_list:
        if func in def_func_list:
            # 该函数是用户自定义
            continue
        else:
            # 判断该函数是否是标准库函数
            if func in standard_API:
                continue
            else:
                # 该func很可能是API，保存下来{func, repo, declaration}, 另保存一个API-list，只有APIname
                # new_dict = dict()
                # new_dict['func'] = func
                # new_dict['repo']= in_dir.split('/')[-1]
                # new_dict['declaration'] = declaration
                file_api_list.append(func)
                # with open(log_json, 'a') as f:
                #     f.write(json.dumps(new_dict))
                #     f.write('\n')
                # with open(api_path, 'a') as f:
                #     f.write(func + '\n')
    file_api_list = list(set(file_api_list))
    for api in file_api_list:
        with open(api_path, 'a') as f:
            f.write(api + '\n')
        
