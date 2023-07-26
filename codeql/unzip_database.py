import os
import sys
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

# codeql database unbundle --target=/home/jhliu/database-all/ /home/jhliu/database-zip/radare2-674617ed81.zip
if __name__ == '__main__':
    print('this script will unzip all the databases and their source code in <in_dir> and put database in <out_dir>, source code in <out_dir/source_code> dir')
    print('Usage: python3 ./unzip_database.py <in_dir> <out_dir>')
    if len(sys.argv) != 3:
        print('Wrong Input unzip_database.py <in_dir> <out_dir>. Example: python3 ./unzip_database.py /home/jhliu/databases-zip/ /home/jhliu/database-all/')
        exit(1)
    database_dir = sys.argv[1] + '/'
    out_dir = sys.argv[2] + '/'
    out_code_dir = out_dir + '/source_code/'
    home_dir = '/home/jhliu'
    tmp_log = home_dir + '/tmp_unzip_log'
    
    files = get_all_file_path(database_dir)
    
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    if not os.path.exists(out_code_dir):
        os.mkdir(out_code_dir)
    
    
    with open(tmp_log, 'w') as f:
        f.write('Begin Unzip...\n')
    fail_list = list()
    
    for file in files:
        print(file)
        time_start = time.time()
        file_name = file['name']
        file_path = file['path']
        
        unbundle_cmd = 'codeql database unbundle --target=' + out_dir + ' ' + file_path

        with open(tmp_log, 'a') as f:
            f.write('\n\nUnbundle ' + file_name + '\nCmd: ' + unbundle_cmd + '\n')
        print(unbundle_cmd)
        
        re = os.system(unbundle_cmd)
        if re != 0:
            fail_list.append(file)
            print('Unbundle Faild')
            with open(tmp_log, 'a') as f:
                f.write('Unbundle Faild\n')
            continue
        
        # unzip source code:
        unzip_in = out_dir + file_name.strip('.zip') + '/src.zip'
        
        source_code_path = out_code_dir + '/' + file_name.strip('.zip')
        unzip_cmd = 'unzip ' + unzip_in + ' -d ' + source_code_path
        with open(tmp_log, 'a') as f:
            f.write('Unzip ' + file_name + '\nCmd: ' + unzip_cmd + '\n')
        print(unzip_cmd)
        
        re = os.system(unzip_cmd)
        
        time_end = time.time()
        time_cost = time_end - time_start
        with open(tmp_log, 'a') as f:
            f.write('Bundle re: ' + str(re) + '\n')
            f.write('Time: ' + str(time_cost) + '\n')
        print(re)
        if re != 0:
            fail_list.append(file)
            print('Unzip Faild')
            with open(tmp_log, 'a') as f:
                f.write('Unzip Faild\n')
        
    print('Fail list: ')
    for file in fail_list:
        print(file['name'])