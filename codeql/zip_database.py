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
        if not os.path.isfile(orig_path):
            # print('in')
            out_dict = dict()
            out_dict['name'] = path
            out_dict['path'] = orig_path
            res.append(out_dict)
    return res
    
# codeql database bundle --output=/home/jhliu/database-zip/fluent-bit-2c7b7fabc.zip /home/jhliu/databases/fluent-bit-2c7b7fabc
if __name__ == '__main__':
    print('this script will bundle all the databases in <in_dir> and output the .zip file of database in <out_dir>.')
    print('Usage: python3 ./zip_database.py <in_dir> <out_dir>')
    if len(sys.argv) != 3:
        print('Wrong Input zip_database.py <in_dir> <out_dir>. Example: python3 ./zip_database.py /home/jhliu/databases/ /home/jhliu/database-zip')
        exit(1)
    database_dir = sys.argv[1] + '/'
    out_dir = sys.argv[2] + '/'
    home_dir = '/home/jhliu'
    tmp_log = home_dir + '/tmp_bundle_log'
    
    files = get_all_file_path(database_dir)
    # print(files)
    
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    
    with open(tmp_log, 'w') as f:
        f.write('Begin Bundle...\n')
    fail_list = list()
    
    for file in files:
        print(file)
        time_start = time.time()
        file_name = file['name']
        file_path = file['path']
        
        bundle_cmd = 'codeql database bundle --output=' + out_dir + file_name + '.zip ' + file_path
        
        with open(tmp_log, 'a') as f:
            f.write('\n\nBundle ' + file_name + '\nCmd: ' + bundle_cmd + '\n')
        print(bundle_cmd)
        
        re = os.system(bundle_cmd)
        time_end = time.time()
        time_cost = time_end - time_start
        with open(tmp_log, 'a') as f:
            f.write('Bundle re: ' + str(re) + '\n')
            f.write('Time: ' + str(time_cost) + '\n')
        print(re)
        if re != 0:
            fail_list.append(file)
        
    print('Fail list: ')
    for file in fail_list:
        print(file['name'])
        

