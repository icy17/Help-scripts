import os
import sys
import subprocess
import json
import time

# return a dict list. dict: {name: file_name, path: full_path}
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
        print('Usage: python3 ./auto_apisan.py <in_software_dir> <out_dir>')
        exit(1)
    
    # TODO check if more?
    apisan_cmd = ['apisan check --checker=rvchk', 'apisan check --checker=cpair', 'apisan check --checker=args', 'apisan check --checker=intovfl', 'apisan check --checker=cond', 'apisan check --checker=fsb']
    
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    out_log = out_dir + '/apisan-log'
    faild_log = out_dir + '/apisan-faild-log'
    success_log = out_dir + '/apisan-success-log'
    software_path = in_dir + '/apisan-in'
    software_list = list()

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    with open(software_path, 'r') as f:
        tmp = f.read().strip('\n')
        software_list = tmp.split('\n')
    for software in software_list:
        out_dict = dict()
        out_dict['repo'] = software
        out_dict['status'] = 'begin'
        out_dict['faild_stage'] = ''
        software_dir = in_dir + '/' + software
        out_software_dir = out_dir + '/' + software
        if not os.path.exists(out_software_dir):
            os.mkdir(out_software_dir)
        
        os.chdir(software_dir)
        with open(out_log, 'a') as f:
            f.write('Parse' + software + '\n')
        for cmd in apisan_cmd:
            start = time.time()
            check_name = cmd.strip(' ').split('=')[-1]
            out_path = out_software_dir + '/' + check_name
            all_cmd = cmd + ' > ' + out_path
            out_dict['status'] = all_cmd
            with open(out_log, 'a') as f:
                f.write('Exec' + all_cmd + '\n')
            return_info = subprocess.Popen(all_cmd, shell=True, stderr=subprocess.PIPE)
            try:
                out, err = return_info.communicate(timeout=18000)
            except:

                with open(faild_log, 'a') as f:
                    out_dict['faild_stage'] = 'timeout'
                    f.write(json.dumps(out_dict))
                    f.write('\n')
                with open(out_log, 'a') as f:
                    f.write('Cost too much time. Break!\n\n')
                # os.remove(ql_path)
                continue
            end = time.time()
            info = err.decode("utf-8","ignore")
            if return_info.returncode != 0:
                with open(faild_log, 'a') as f:
                    out_dict['faild_stage'] = 'run wrong'
                    f.write(json.dumps(out_dict))
                    f.write('\n')
                with open(out_log, 'a') as f:
                    f.write('Error: ' + info + '\n\n')
                    continue
            
            else:
                out_dict['status'] = 'finish'
                with open(success_log, 'a') as f:
                    f.write(json.dumps(out_dict))
                    f.write('\n')
                with open(out_log, 'a') as f:
                    f.write('Success! Time: ' + str(end-start) + 's\n\n')
                

    