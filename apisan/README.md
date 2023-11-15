APISAN使用步骤： 
    apisan build ./configure
    apisan build make
    apisan check --db=[db] --checker=[checker]

auto_apisan.py: 自动化使用APISAN检查in_software_dir下的软件，即自动化第三步，需要要求软件已经完成APISAN的前两步
    Usage: python3 ./auto_apisan.py <in_software_dir> <out_dir>
        in_software_dir下包含apisan-in文件，该文件包含所有待检查的软件名称以及所有已经编译好的软件