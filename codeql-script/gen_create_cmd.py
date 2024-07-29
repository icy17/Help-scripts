import os
import subprocess
import sys

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

def gen_create_cmd(software):
    make_cmd = 'make'
    codeql_create_cmd = 'codeql database create --language=cpp --overwrite -c "' + make_cmd + '" /root/database/' + software 
    return codeql_create_cmd

    

if __name__ == '__main__':
    # codeql database create --language=cpp --overwrite -c "make" /home/icy/Desktop/CodeQL/database/tcpdump-fd2a4d9
    if len(sys.argv) != 2:
        print("Usage gen_create_cmd software")
    software = sys.argv[1]
    git_path = '/root/software/' + software

    commit_id = get_commit_id(git_path)
    
    print(commit_id)
    software_id = software + '-' + commit_id
    codeql_create_cmd = gen_create_cmd(software_id)

    print(codeql_create_cmd)

    # test_cmd = 'ls'
    # subprocess.getstatusoutput(test_cmd, shell = True)


    