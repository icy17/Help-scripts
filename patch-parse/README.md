get_non_API.py: 自动从软件源码中确定该软件自定义的函数有哪些
    原理：找到所有在软件源码中定义的函数
    漏报：由于软件可能包含某些库的实现源码（比如sqlite3.c），因此部分库使用API时也可能可以找到对应的函数实现
    误报：standard API可能不全，可能tree-sitter无法分析部分文件，导致函数提取失败
    Usage：python3 ./get_API.py <repo_dir> <out_dir>
        在out_dir生成repo_name-apilist文件，比如curl-apilist
    Example: python3 ./get_API.py ~/repos/curl/ ~/output/patch_parse/
parse_commit.py: 自动处理软件的commit，从中筛出所有安全相关的函数相关的commit
    Usage: python ./parse_commit.py <repo-dir> <noapi_dir> <out_dir>
        noapi_dir: 保存所有自定义函数list的dir，该dir是get_non_API.py的out_dir
        repo_dir: 保存所有repo的dir，会便利dir下的所有repo并处理commit
        out_dir: 会生成API0, API1, API2, API3四个文件夹，每个文件夹下都会放对应的commit（修改了多个file会拆成多个文件）