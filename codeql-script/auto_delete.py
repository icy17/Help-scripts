import os
import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('python3 ./auto-delete.py <res_dir>')
        exit(1)
    in_dir = sys.argv[1] + '/'
    log_path = in_dir + 'delete_log'
    files = os.listdir(in_dir)
    os.chdir(in_dir)
    for file in files:
        if file.find('.csv') != -1:
            if os.path.getsize(file) == 0:
                print('Remove out file: ' + file)
                os.remove(file)
                with open(log_path, 'a') as f:
                    f.write(f'No wrong result! Delete out csv file: {file}\n')
