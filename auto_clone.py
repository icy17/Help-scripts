import os
import sys
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

def get_repo_name(link):
    link = link.replace('.git', '')
    name = link.strip('/').split('/')[-1]
    return name

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("wrong input")
        print('Usage: python3 ./auto_clone.py <https_link_path> <out_dir>')
        exit(1)
    
    in_path = sys.argv[1]
    out_dir = sys.argv[2]
    out_log = out_dir + '/clone-log'
    faild_log = out_dir + '/clong-faild-log'
    
    in_list = read_json(in_path)
    os.chdir(out_dir)
    for item in in_list: 
        os.chdir(out_dir)
        repo_link = item['github link']
        commit_id = item['commit id']
        repo_name = get_repo_name(repo_link)
        cmd = 'git clone --recursive ' + repo_link
        with open(out_log, 'a') as f:
            f.write('Exec: ' + cmd + '\n')
        re = os.system(cmd)
        if not re:
            with open(out_log, 'a') as f:
                f.write('Success\n')
        else:
            item['faild_stage'] = 'clone'
            with open(faild_log, 'a') as f:
                f.write(item + '\n')
        
        os.chdir(out_dir + '/' + repo_name)
        cmd = 'git checkout ' + str(commit_id)
        with open(out_log, 'a') as f:
            f.write('Exec: ' + cmd + '\n')
        re = os.system(cmd)
        if not re:
            with open(out_log, 'a') as f:
                f.write('Success\n')
        else:
            item['faild_stage'] = 'checkout'
            with open(faild_log, 'a') as f:
                f.write(item + '\n')
        
        