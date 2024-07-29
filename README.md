# 代码说明
## codeql-script/: 用于自动化CodeQL检测中的某些步骤
    zip_database.py
    unzip_database.py
    auto_find.py
    check_compile.py
    auto_detect.py
    auto_delete.py
    combine_csv.py
## apisan/: 用于自动化使用APISAN检查多个软件
    auto_apisan.py
## LLVM-help/: 用于自动化完成LLVM分析中的某些步骤
    parse_bc.py: 收集编译好的软件中的bc文件并生成bc_list然后打包
## ql-code/: CodeQL使用的检测代码，这里有一些对特定类型问题的检测ql
## ql-testcase/: 为了debug ql代码用的一些C语言简单的示例代码
## patch-parse/: 处理软件的patch信息的代码
    get_API.py
    parse_commit.py
## 其他代码：不好分类但常用的
    auto_clone.py: 用于根据https_link_path自动化clone软件到out_dir，并自动checkout到指定commit
        Usage: python3 ./auto_clone.py <https_link_path> <out_dir>
        https_link_path： json文件， 可用read_json读入， 每行是一个json，包含github link和commit id两个键。
    cal_API_num.py: Counts the frequency of each API occurrence in the findres file and outputs it in descending order
        Usage: python3 ./cal_API_num.py <in_findres> <out_num_file>
    gen_csv.py: 从json文件生成csv文件
        Usage: python3 ./gen_csv.py in_path
    parse_csv.py: 从csv生成json文件
        Usage: python3 ./parse_csv.py in_path
    parse_include.py: 从.h文件中得到该文件描述的API列表
        Usage: python3 ./parse_include.py <in_include_file.h> <out_path>
        