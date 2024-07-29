from pydriller import Repository, ModifiedFile
import json
import os
import sys
import subprocess
from cinspector.interfaces import CCode, CFile
from cinspector.analysis import CallGraph
from cinspector.nodes import CompoundStatementNode, DeclarationNode, IfStatementNode,Edit, AssignmentExpressionNode, IdentifierNode, InitDeclaratorNode, ParenthesizedExpressionNode, FunctionDefinitionNode

def get_standard_list():
    standard_API_path = '/root/data/API-list/standardC'
    out_list = list()
    with open(standard_API_path, 'r') as f:
        out_list = f.read().split('\n')
    return out_list

standard_list = get_standard_list()
# repo = '/root/PR-software/php-src/'
# print('wait for clone?')
# for commit in Repository(repo).traverse_commits():
#     print(commit.msg)
#     print(commit.hash)
#     print(commit.insertions)
#     print(commit.deletions)
#     for m in commit.modified_files:
#         print(type(m))
#         exit(1)
#         if len(m.methods) == 0 or m.filename.find('.c') == -1:
#             continue
#         print(
#             "Author {}".format(commit.author.name),
#             " modified {}".format(m.filename),
#             " with a change type of {}".format(m.change_type.name),
#             " and the complexity is {}".format(m.complexity)
#         )
#         print(m.methods)
#         print(m.diff_parsed)
#         print(m.filename)
#         print(m.new_path)
#         exit(1)

def get_all_file_path(in_dir):
    res = []
    out_list = list()
    for path in os.listdir(in_dir):
        # print(in_dir)
    # check if current path is a file
        orig_path = os.path.join(in_dir, path)
        # print(orig_path)
        # if not os.path.isfile(orig_path):
            # print('in')
        out_dict = dict()
        out_dict['name'] = path
        out_dict['path'] = orig_path
        res.append(out_dict)
    return res

# DEBUG
def if_msg_security(msg):
    key_msgs = ['leak', 'security', 'vuln', 'fix', 'null deref', 'overflow', 'by zero', 'issue', 'crash', 'fault', 'abort', 'memory', 'code exec', 'bypass', 'cve ', 'cwe ', 'uninitia']
    msg = msg.replace('-', ' ')
    msg = msg.replace('_', ' ')
    msg = msg.replace('.', ' ')
    msg = msg.replace(',', ' ')
    msg = msg.lower()
    hit_list = list()
    for key in key_msgs:
        if msg.find(key) != -1:
            hit_list.append(key)

    return hit_list

# def get_loc_by_index(index, code):
#     before_content = code[:index]

# 找到file_path对应的所有fc，以列表形式返回func名(get_API.py里写的)
def get_fc(code):
    out_list = list()
    # code = ''
    ast_type = 'call_expression'
    # with open(file_path, 'r') as f:
    #     code = f.read()
    cc = CCode(code)
    target_list = cc.get_by_type_name(ast_type)
    for target in target_list:
        # print(target)
        if not target.function or target.is_indirect():
            continue
        function_name = target.function.src
        if function_name in standard_list:
            continue
        # print(function_name)
        out_list.append(function_name)
    return out_list

# 获取一段代码中的所有函数，并返回元组列表，每个元组内有该函数开始行和结束行[(start_line, end_line)], line num从1开始
def get_func_list(code):
    func_line_list = list()
    func_list = list()
    cc = CCode(code)

    func_def_list = cc.get_by_type_name('function_definition')
    for func_def in func_def_list:
        start_byte = func_def.internal.start_byte
        end_byte = func_def.internal.end_byte
        before_content = code[: start_byte]
        function_content = code[start_byte: end_byte]
        function_line_nums = function_content.count('\n')
        before_line = before_content.count('\n')
        start_line = before_line + 1
        end_line = start_line + function_line_nums
        func_line_list.append((start_line, end_line))
        func_list.append(function_content)
    return func_line_list, func_list


# 最多的commit：只要有API就算API相关
# DEBUG
def if_commit_API0(m: ModifiedFile, fc_list, api_list):
    before_code = m.source_code_before
    after_code = m.source_code
    diff_info = m.diff_parsed
    match_api_list = list()
    for fc in fc_list:
        if fc in api_list:
            match_api_list.append(fc)
    return match_api_list
   
# 中等的commit：当前函数与API相关
# DEBUG
def if_commit_API1(m: ModifiedFile, noapi_list, fc_list):
    match_list = list()
    before_code = m.source_code_before
    after_code = m.source_code
    diff_info = m.diff_parsed
    func_line_list, func_list = get_func_list(after_code)
    tmp_list = list()
    
    for item in diff_info['added']:
        loc = item[0]
        line = item[1]
        i = -1
        for func in func_line_list:
            i += 1
            start_line = func[0]
            end_line = func[1]
            if loc >= start_line and loc <= end_line:
                tmp_list.extend(get_fc(func_list[i]))
                break
    for fc in tmp_list:
        if fc not in noapi_list:
            match_list.append(fc)  
    return match_list  

# 少的commit：上下文XX行内有API
# DEBUG
def if_commit_API2(m: ModifiedFile, noapi_list, fc_list):
    window_size = 10
    before_code = m.source_code_before
    after_code = m.source_code
    diff_info = m.diff_parsed
    match_api_list = list()
    after_lines = after_code.split('\n')
    tmp_list = list()
    line_list = list()
    for item in diff_info['added']:
        loc = item[0]
        # line = item[1]
        begin_line = loc - 10
        end_line = loc + 10
        if loc < 10:
            begin_line = 0
        if loc > len(after_lines) - 11:
            end_line = len(after_lines) - 1
        k = begin_line
        while 1:
            if k > end_line:
                break
            line_list.append(k)
            # line_hit = after_lines[k]
            # print(line_hit)
            k += 1
            # tmp_list.extend(line_hit)
    line_list = list(set(line_list))
    line_list.sort()
    content = ''
    for loc in line_list:
        content += after_lines[loc]
        content += '\n'
    
    tmp_list = get_fc(content)
    for fc in tmp_list:
        if fc not in noapi_list:
            match_api_list.append(fc)  
    return match_api_list    

# 最少的commit：只有修改行有API
# DEBUG
def if_commit_API3(m: ModifiedFile, noapi_list, fc_list):
    before_code = m.source_code_before
    after_code = m.source_code
    diff_info = m.diff_parsed
    match_api_list = list()
    tmp_list = list()
    if len(diff_info['added']) != 0:
        for item in diff_info['added']:
            loc = item[0]
            line = item[1]
            fcs = get_fc(line)
            tmp_list.extend(fcs)
    if len(diff_info['deleted']) != 0:
        for item in diff_info['deleted']:
            loc = item[0]
            line = item[1]
            fcs = get_fc(line)
            tmp_list.extend(fcs)    
    for fc in tmp_list:
        if fc not in noapi_list:
            match_api_list.append(fc)  
    return match_api_list  

# TODO
# 写入json并保存有用的commit(多个file保存多个dict):{repo, func, file_path, commit_msg, commit_id, api_level, msg_match, msg_level, orig_filename}
# 除了json，保存该file commit diff信息到commit_path
def write_log(out_dir, repo, orig_filename, commit_path, commit_msg, file_content, commit_id, api_level, msg_match_list, api_match, max_lines):
    out_dict = dict()
    out_log = out_dir + '/0AAAAlog'
    
    out_dict['commit_id'] = commit_id 
    out_dict['commit_path'] = out_dir + '/' + commit_path
    out_dict['repo'] = repo
    out_dict['filename'] = orig_filename
    out_dict['commit_msg'] = commit_msg
    out_dict['api_level'] = api_level
    out_dict['keyword_list'] = msg_match_list
    out_dict['api_match'] = api_match
    out_dict['changed_lines'] = max_lines
    if msg_match_list == ['fix']:
        out_dict['keyword_level'] = 'fix'
    else:
        out_dict['keyword_level'] = 'others'
    
    # print(out_dict)
    with open(out_log, 'a') as f:
        f.write(json.dumps(out_dict))
        f.write('\n')
    with open(out_dir + '/' + commit_path, 'w') as f:
        f.write(file_content)
        
        
if __name__ == '__main__':
    # exit(1)
    # repo_list = ['']
    if len(sys.argv) != 3:
        print('Wrong Input!\nUsage: python ./parse_commit.py <repo-dir> <noapi_dir> <out_dir>')
        exit(1)
    repo_dir = sys.argv[1]
    noapi_dir = sys.argv[2]
    out_dir = sys.argv[2]
    # read API-list
    parse_repo = ['nginx', 'curl', 'goaccess', 'libuv', 'openwrt', 'nnn']
    
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    # out_dir0 = out_dir + '/API0'
    out_dir1 = out_dir + '/API1'
    out_dir2 = out_dir + '/API2'
    out_dir3 = out_dir + '/API3'
    # if not os.path.exists(out_dir0):
    #     os.mkdir(out_dir0)
    if not os.path.exists(out_dir1):
        os.mkdir(out_dir1)
    if not os.path.exists(out_dir2):
        os.mkdir(out_dir2)
    if not os.path.exists(out_dir3):
        os.mkdir(out_dir3)
    repo_list = get_all_file_path(repo_dir)

    
    
    for repo_dict in repo_list:
        repo = repo_dict['path']
        repo_name = repo_dict['name']
        if len(parse_repo) != 0:
            if repo_name not in parse_repo:
                continue
        noapi_list = list()
        noapi_path = noapi_dir + '/' + repo_name + '-apilist'
        with open(noapi_path, 'r') as f:
            noapi_list = f.read().split('\n')
        print(repo_name)
        commit_nums = len(list(Repository(repo).traverse_commits()))
        commit_i = 0
        # 获取commit
        for commit in Repository(repo).traverse_commits():
            commit_i += 1
            commit_id = commit.hash
            # DEBUG
            # if commit_id != '0b3d0c82a7fd24331350142ef59aed00ac6538ad':
            #     continue
            commit_msg = commit.msg
            print(commit_id)
            print(repo_name + ' parsed ' + str(commit_i) + ' / ' + str(commit_nums))
            api_level = -1
            # 针对每个commit进行过滤：
            hit_list = if_msg_security(commit_msg)
            if len(hit_list) != 0:
                # 确定是安全相关的commit
                for m in commit.modified_files:
                    
                    after_source_code = m.source_code
                    file_name = m.filename
                    diff_info = m.diff
                    max_lines = max(m.deleted_lines, m.added_lines)
                    # DEBUG:
                    # if file_name != 'ao_sun.c':
                    #     continue
                    # DEBUG:
                    # if m.deleted_lines + m.added_lines > 20:
                    #     continue
                    
                    # 只过滤C/C++语言文件
                    if not file_name.endswith('.c') and not file_name.endswith('.cpp') and not file_name.endswith('.h'):
                        continue
                    commit_file = commit_id[:8] + '-' + file_name.split('.')[0]
                    # 如果commit没修改文件内容就跳过
                    if after_source_code == None:
                        continue
                    # print(file_name)
                    # print('wait for get_fc')
                    fc_list = get_fc(after_source_code)
                    # print(fc_list)
                    # 如果没有任何函数调用直接跳过
                    if len(fc_list) == 0:
                        continue
                    # match_list = if_commit_API0(m, fc_list, api_list)
                    # if len(match_list) == 0:
                    #     continue
                    # api_level = 0
                    # tmp_list = match_list
                    # print(tmp_list)
                    # exit(1)
                    match_list = if_commit_API1(m, noapi_list, fc_list)
                    if len(match_list) == 0:
                        # (out_dir, repo, orig_filename, commit_path, commit_msg, file_content, commit_id, api_level, msg_match_list, api_match, max_lines)
                        # write_log(out_dir0, repo_name, file_name, commit_file, commit_msg, diff_info, commit_id, api_level, hit_list, match_list, max_lines)
                        continue
                    api_level = 1
                    tmp_list = match_list
                    match_list = if_commit_API2(m, noapi_list, fc_list)
                    if len(match_list) == 0:
                        write_log(out_dir1, repo_name, file_name, commit_file, commit_msg, diff_info, commit_id, api_level, hit_list, match_list, max_lines)
                        continue
                    api_level = 2
                    tmp_list = match_list
                    match_list = if_commit_API3(m, noapi_list, fc_list)
                    if len(match_list) == 0:
                        write_log(out_dir2, repo_name, file_name, commit_file, commit_msg, diff_info, commit_id, api_level, hit_list, match_list, max_lines)
                        continue
                    else:
                        api_level = 3
                        write_log(out_dir3, repo_name, file_name, commit_file, commit_msg, diff_info, commit_id, api_level, hit_list, match_list, max_lines)
                