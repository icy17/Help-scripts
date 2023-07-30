import subprocess
import sys
import json
import os



def gen_search_cmd(database):
    # codeql database analyze /home/icy/Desktop/CodeQL/database/tcpdump-fd2a4d9 --rerun --format=csv --output=./output/tcpdump-fd2a4d9.csv --ram=1024 ./vscode-codeql-starter/codeql-custom-queries-cpp/pcap_compile-pcap_freecode.ql
    codeql_search = 'codeql database analyze ' + codeql_dir + '/database/' + database + ' --rerun --format=csv --output=' + codeql_dir + '/output/' + database + '.csv --ram=1024 ' + codeql_dir + '/vscode-codeql-starter/codeql-custom-queries-cpp/search_api.ql'
    return codeql_search

def get_commit_id(path):
    cd_cmd = 'cd ' + path
    git_cmd = cd_cmd + '&& git rev-parse --short HEAD'
    output = subprocess.getstatusoutput(git_cmd)
    commit_id = 0
    if output[0] == 0:
        commit_id = output[1]
    else:
        print('get commit id faild')
        exit(1)
    return commit_id

def output_info(in_dict):
    output = list()
    database = in_dict['database']
    api_list = in_dict['api_info']
    for apis in api_list:
        api1 = list(apis.keys())[0]
        api2s = apis[api1]
        for api2 in api2s:
            api2 = api2.strip('\n')
            api2 = api2.strip(' ')
            one_dict = dict()
            one_dict['database'] = database
            one_dict['API1'] = api1
            one_dict['API2'] = api2
            output.append(one_dict)
    return output

def filter_file(hit_list):
    out_list = list()
    for file in hit_list:
        filename = file.split('/')[-1]
        if filename not in filter_list:
            out_list.append(file)
    return out_list

def gen_create_cmd(software, source_path):
    make_cmd = 'make -j 4'
    codeql_create_cmd = 'codeql database create --language=cpp' + ' --source-root ' + source_path +' --overwrite -c "' + make_cmd + '" ' + codeql_dir + '/database/' + software 
    return codeql_create_cmd

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

def clone(out_dir, repo):
    
    res = True
    os.chdir(out_dir)
    clone_cmd = 'git clone --recursive --depth 1 git@github.com:' + repo + '.git'
    # clone_cmd = 'git clone --recursive git@github.com:' + repo + '.git'
    # with open(log_path, 'a') as f:
    #     f.write(clone_cmd + '\n')
    print(clone_cmd)
    result = os.system(clone_cmd)
    if result != 0:
        # with open(log_path, 'a') as f:
        #     f.write('clone repo:' + repo + 'error!\n')
        res = False
    # else:
    #     with open(log_path, 'a') as f:
    #         f.write("clone succuss\n")
    return res

def get_list_from_dir(in_dir):
    
    res = []
    out_list = list()
    for path in os.listdir(in_dir):
    # check if current path is a file
        orig_path = path
        if os.path.isfile(os.path.join(in_dir, path)):
            res.append(orig_path)
    for api in res:
        lib = api
        api = os.path.join(in_dir, api)
        with open(api, 'r') as f:
           tmp =  f.read().strip('\n')
           lines = tmp.split('\n')
           for line in lines:
               out_dict = dict()
               out_dict['api'] = line
               out_dict['lib'] = lib
               out_list.append(out_dict)
    return out_list


# api_malloc, api_free, malloc_index, free_index
def get_api_list(in_path, lib):
    out_list = list()
    with open(in_path, 'r') as f:
        tmp_list = json.load(f)
    # api_list = read_json(in_path)
    for line in tmp_list:
        # if line['lib'] == lib:
        out_list.append(line)
    return out_list

# repo list 手动产生，repo dir（outdir）手动产生
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:python3 ./auto_find.py api_dir out_dir repo_list_path')
        exit(1)
    else:
        repo_list_dir = '/' + sys.argv[3]
        # repo_path = sys.argv[4]
        # software_name = sys.argv[2]
        api_dir = sys.argv[1] + '/'
        out_dir = sys.argv[2] + '/'
    # database_path = ''
        # software = 'Craft'
    # dir = '/home/icy/Desktop/data/sqlite3_top20/'
    # codeql_dir = '/root/CodeQL/'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    output_path = out_dir + '/findres'
    filter_list = []
    api_path = api_dir + '/'
    libs = ['openssl', 'libpcap', 'libxml2', 'sqlite3']
    # libs = ['libpcap']
    # libs = ['ffmpeg', 'ldap', 'libpcap','libexpat','libmysql','libgnutls', 'libevent', 'zlib','libzip', 'libdbus']
    # if not os.path.exists(output_dir):
    #     os.mkdir(output_dir)
    repo_list = list()
    
    # for lib in libs:
        
    #     repo_path = out_dir + repo_list_dir + lib
    #     if not os.path.exists(repo_path):
    #         continue
    #     with open(repo_path, 'r') as f:
    #         tmp_list = f.readlines()
    #     repo_list.extend(tmp_list)
    # # repo_list = [repo_path]
    repo_path = repo_list_dir
    with open(repo_path, 'r') as f:
            repo_list = f.readlines()
    for i in range(len(repo_list)):
        repo_list[i] = repo_list[i].strip('\n')
    repo_list = list(set(repo_list))
    print(repo_list)
    # print(repo_list)
    
    api_list = get_list_from_dir(api_path)
    print(api_list)
    # exit(1)
    # api_list = read_json(api_path)
    out_list = list()
    for repo in repo_list:
        repo = repo.strip('\n')
        tmp_dir = out_dir + '/' + repo
        repo_name = repo.strip().split('/')[-1]
        # if os.path.exists(tmp_dir):
        #     os.remove(tmp_dir)
        #     os.mkdir(tmp_dir)
        # else:
        #     os.mkdir(tmp_dir)
        # if not clone(tmp_dir, repo):
        #     print(f'clone {repo} error')
        #     continue
        # out_path = output_dir + '/' + repo.replace('/', '-')
        
        out_dict = dict()
        out_dict['repo'] = repo_name
        # out_dict['lib'] = lib
        find_api_list = list()
        api_dict = dict()
        for api_json in api_list:
            
            find_api = api_json['api']
            
            # free_api = api_json['free_api']
            # malloc_index = api_json['malloc_index']
            # free_index = api_json['free_index']
            lib = api_json['lib']
            if lib not in libs:
                continue
            info_dict = dict()
            info_dict['lib'] = lib
            info_dict = api_json
            info_dict['repo'] = repo_name
            # out_dict['api'] = find_api
            # out_dict['lib'] = lib
            file_list = list()
            os.chdir(tmp_dir)
            find_cmd = 'find ' + tmp_dir + ' -regex ".*\\.cpp\\|.*\\.c\\|.*\\.h\\|.*\\.cxx\\|.*\\.cc\\|.*\\.C\\|.*\\.c++" | xargs grep -ri "' + find_api + '"'
            print(find_cmd)
            output = subprocess.getstatusoutput(find_cmd)
            print(output)
            if output[0] != 0 and output[0] != 123:
                print(find_cmd)
                print("find cmd faild")
                exit(1)
            if output[1] != '':
                find_list = output[1].split('\n')
                info_dict['hit_nums'] = len(find_list)
                for find_api in find_list:
                    # index = find_list.index(find_api)
                    file = find_api.split(':')[0].strip()
                    file_list.append(file)
            else:
                info_dict['hit_nums'] = 0
            # free num
            # find_cmd = 'find ' + tmp_dir + ' -regex ".*\\.cpp\\|.*\\.c\\|.*\\.h\\|.*\\.cxx\\|.*\\.cc\\|.*\\.C\\|.*\\.c++" | xargs grep -ri "' + free_api + '"'
            # print(find_cmd)
            # output = subprocess.getstatusoutput(find_cmd)
            # print(output)
            # if output[0] != 0 and output[0] != 123:
            #     print(find_cmd)
            #     print("find cmd faild")
            #     exit(1)
            # if output[1] != '':
            #     find_list = output[1].split('\n')
            #     info_dict['free_nums'] = len(find_list)
            #     for find_api in find_list:
            #         # index = find_list.index(find_api)
            #         file = find_api.split(':')[0].strip()
            #         file_list.append(file)
            # else:
            #     info_dict['free_nums'] = 0
            find_list = list(set(file_list))
            # for find_api in find_list:
            #     # index = find_list.index(find_api)
            #     file = find_api.split(':')[0].strip()
            #     file_list.append(file)
            # find_list = list(set(file_list))
            # find_list = filter_file(find_list)
            if len(find_list) != 0:
                info_dict['file'] = find_list
                with open(output_path, 'a') as f:
                    f.write(json.dumps(info_dict))
                    f.write('\n')
                find_api_list.append(find_api)
            # if repo_name == 'gpac-41d952f' and find_api == 'sws_getContext':
            #     exit(1)
            # if find_api == 'event_new' and repo_name.find('seafile') != -1:
            #     exit(1)
                # api_list_hit.append(api_dict)
            # api_dict['file_name'] = find_list
            # out_dict['api_info'] = api_list_hit
        # find_api_list = list(set(find_api_list))
        # if len(find_api_list) != 0:
        #     # api_dict[find_api]
        #     with open(output_path, 'a') as f:
        #         f.write(json.dumps(info_dict))
        #         f.write('\n')
        #     out_dict['api'] = find_api_list
        #     out_list.append(out_dict)
    # for item in out_list:
    #     with open(output_path, 'a') as f:
    #         f.write(json.dumps(item))
    #         f.write('\n')
            
    # before::
    # filter_list = ['sqlite3.c']
    # software = software_name
    

    # path = dir + software
    # api_path = dir + '/sqlite3_api'
    # out_path = dir + software + '-findout'
    # commit_id = get_commit_id(path)
    # software_id = software + '-' + commit_id
    # codeql_create_cmd = gen_create_cmd(software_id, path)
    # codeql_search_cmd = gen_search_cmd(software_id)

    # print(codeql_create_cmd)
    # find /home/icy/Desktop/data/codeql/libzip -regex ".*\.cpp\|.*\.c\|.*\.h" | xargs grep -ri "zip_source_filep_create" -l >> /home/icy/Desktop/data/codeql/libzip_find
    # if len(sys.argv) != 3:
    #     print("wrong")
    #     exit(1)
    
    # api_list = get_api_list(api_path)
    # # with open(api_path, 'r') as f:
    # #     api_list = f.readlines()
    # out_list = list()
    # out_dict = dict()
    # out_dict['software'] = software
    # out_dict['database'] = software_id
    # api_list_hit = list()
    # for api_line in api_list:
    #     api_dict = dict()
    #     api_pair = list()
    #     api1 = api_line.split(': ')[0]
    #     api2 = api_line.split(': ')[1]
    #     api_pair = api2.split(',')
    #     # for i in api_pair:
    #     #     i = i.strip('\n')
    #     #     i = i.strip(' ')
    #     api = api1
    #     api = api.strip('\n')
    #     api_dict[api] = api_pair
    #     find_cmd = 'find ' + path + ' -regex ".*\\.cpp\\|.*\\.c|.*\\.h" | xargs grep -ril ' + api
    #     output = subprocess.getstatusoutput(find_cmd)
    #     # print(output)
    #     if output[0] != 0 and output[0] != 123:
    #         print("find cmd faild")
    #         exit(1)
    #     if output[0] == 123:
    #         continue
    #     find_list = output[1].split('\n')
    #     find_list = filter_file(find_list)
    #     if len(find_list) != 0:
    #         api_list_hit.append(api_dict)
    #     api_dict['file_name'] = find_list
    # out_dict['api_info'] = api_list_hit
    # print(out_dict)
    # print(codeql_create_cmd)
    # print(codeql_search_cmd)
    # test = output_info(out_dict)
    # out_file = output_path + software_id
    # # print(out_file)
    # with open(out_file, 'a') as f:
    #     for i in test:
    #         j = json.dumps(i)
    #         f.write(j)
    #         f.write('\n')
    # print(test)

        # for i in find_list:
        #     print(i)

