env:LJH_CodeQL
    export CC=clang-17
    export CXX=clang++-17
    export CFLAGS="-save-temps -fno-inline -O2 -g"
    export CXXFLAGS="-save-temps -fno-inline -O2 -g"
    export CPPFLAGS="-save-temps -fno-inline -O2 -g"


parse_bc.py: 用于自动化收集in_project_dir下的bc文件并打包 / 将打包好的bc.zip解压并生成bc_list用于IPPO检测
    Usage: python3 ./parse_bc.py <in_project_dir> <flag>
        in_project_dir: 可以是编译好的project，也可以是.zip文件，该文件是parse_bc.py的gen_dir命令生成的
        flag: gen_bc和gen_dir两个选项：
            gen_bc: 将打包好的bc.zip解压后 / 直接给in_project_dir对应的软件生成bc_list用于IPPO检测
            gen_dir: 收集所有的bc文件后将它们打包成一个bc_dir.zip，用于移植到其他机器检测
        