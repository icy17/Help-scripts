import os
import sys
import subprocess

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Wrong input!\n Usage: python3 ./parse_bc.py <in_project_dir> <flag>')
        exit(1)
    in_dir = sys.argv[1]
    # gen_bc和gen_dir两种，bc是根据indir生成bc_list,如果输入的是zip则会先解压再生成list。 dir是把indir下的所有bc打包成bc_dir.zip
    parse_flag = sys.argv[2]
    find_cmd = 'find -name "*.bc"'
    
    tmp_in_dir = in_dir
    if in_dir.find('.zip') != -1:
        unzip_cmd = 'unzip ' + in_dir + ' -d ' + in_dir.strip('bc_dir.zip')
        print(unzip_cmd)
        # exit(1)
        os.system(unzip_cmd)
        in_dir = in_dir.strip('.zip')
    os.chdir(in_dir)
    out_bc_file = in_dir + '/bc_list'
    out_bc_dir = in_dir + '/bc_dir'
    return_info = subprocess.Popen(find_cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        out, err = return_info.communicate(timeout=300)
    except:
        print('timeout')
        exit(1)
    res_flag = return_info.returncode
    info = out.decode().strip('\n')
    print(info)
    bc_list = info.split('\n')
    if parse_flag == 'gen_bc':
        for bc in bc_list:
            with open(out_bc_file, 'a') as f:
                f.write(in_dir + '/' + bc + '\n')
    if parse_flag == 'gen_dir':
        if  os.path.exists(out_bc_dir):
            os.system('rm -rf ' + out_bc_dir)
        os.mkdir(out_bc_dir)
            
        for bc in bc_list:
            cp_cmd = 'cp ' + bc + ' ' + out_bc_dir + '/'
            print(cp_cmd)
            # exit(1)
            os.system(cp_cmd)
        zip_cmd = 'zip -r ./bc_dir.zip ./bc_dir'
        print(zip_cmd)
        os.system(zip_cmd)
    