from cinspector.interfaces import CCode
from cinspector.analysis import CallGraph
from cinspector.nodes import CompoundStatementNode, DeclarationNode, IfStatementNode



if __name__ == '__main__':
    in_path = '/home/jhliu/repos/libpcap/gencode.c'
    content = ''
    with open(in_path, 'r') as f:
        content = f.read()
    # print(content)
    cc = CCode(content.strip('\n'))
    # print(cc.node.print_tree())
    funcs = cc.get_by_type_name('function_definition')
    # func = funcs[0]
    # # print(func.name)
    # # print(func.parameters)
    # # print(func.value)
    for func in funcs:
        if str(func.name) == 'pcap_freecode':
            print(func)
            print(func.print_tree())
    #     cc1 = CCode(str(func.value))
    #     if str(func.name).find('K') != -1:
    #         print(func)
    #         print(cc1.get_by_type_name('call_expression'))
    #         exit(1)
    # print(type(funcs[0]))
    # for func in funcs:
    #     name = str(func.name)
    #     print(name)
    #     print(type(name))
    #     if name == 'pcap_close':
    #         print(func)
    #         calls = func.children_by_type_name('call_expression')
    #         print(calls)
    #         for call in calls:
    #             if call.is_indirect():
    #                 print(call)
    #                 continue
    #         break
    # print(funcs[0].name)
    # print(funcs)