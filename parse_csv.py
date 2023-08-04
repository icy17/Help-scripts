import csv
import sys
import json
# from  openpyxl import  Workbook 
# from openpyxl  import load_workbook
# import openpyxl

def get_data_excel(in_path):
    wb= openpyxl.load_workbook(in_path)
# 第二步选取表单
    sheet = wb.active
# 按行获取数据转换成列表
    rows_data = list(sheet.rows)
# 获取表单的表头信息(第一行)，也就是列表的第一个元素
    titles = [title.value for title in rows_data.pop(0)]
    # print(titles)

# 整个表格最终转换出来的字典数据列表
    all_row_dict = []
    # 遍历出除了第一行的其他行
    for a_row in rows_data:
        the_row_data = [cell.value for cell in a_row]
        # 将表头和该条数据内容，打包成一个字典
        row_dict = dict(zip(titles, the_row_data))
        # print(row_dict)
        all_row_dict.append(row_dict)
    return all_row_dict

def get_data_csv(in_path):
    out_list = list()
    with open(in_path, 'r') as file_csv:
        # fieldnames = ("field1","field2")
        reader = csv.DictReader(file_csv)
        for info in reader:
            # print(info)
            out_list.append(info)

    return out_list

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('python3 ./parse_csv.py in_path')
        exit(1)
    in_path = sys.argv[1]
    out_path = in_path.split('.')[0]
    # in_path = '/home/jhliu/data/GT-no-keyword.csv'
    # out_path = '/home/jhliu//data/GT-no-keyword'
    json_list = get_data_csv(in_path)
    # print(json_list)
    for info in json_list:
        # print(info)
        with open(out_path, 'a') as f:
            f.write(json.dumps(info))
            f.write('\n')