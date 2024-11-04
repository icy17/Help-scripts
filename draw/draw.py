import matplotlib.pyplot as plt


# plt.style.use('seaborn')
# 示例数据
# generation
# x = [0, 0.5, 1]
# y = [0.77193, 0.76316, 0.7193]
# # right code
x = [0, 0.5, 1]
y = [0.6, 0.575, 0.8]
# # violation code
# x = [0, 0.5, 1]
y = [0.6, 0.581, 0.554]
# # refinement
# x = [0, 0.5, 1]
y = [0.744, 0.716, 0.759]
# 创建折线图
# plt.figure(figsize=(8, 6))
plt.plot(x, y, marker='o', linestyle='-', color='b')

# 添加标题和标签
plt.xticks([0, 0.5, 1])
# plt.title('(a) Raw APSRs Generation')
plt.xlabel('Temperature', fontsize=24)
plt.ylabel('F1', fontsize=24)
plt.xticks(fontsize=20)  # 调整X轴刻度标签字体大小
plt.yticks(fontsize=20)  # 调整Y轴刻度标签字体大小
# plt.subplots_adjust(left=0.4, right=0.7, top=0.7, bottom=0.4)
# 显示图例
# plt.legend()
# max_y = max(y)
# max_x = x[y.index(max_y)]

# # 在图表上标记最高点
# plt.annotate(f'Max: {max_y} at {max_x}', 
#              xy=(max_x, max_y), 
#              xytext=(max_x+0.1, max_y-2),  # 调整标记的位置
#              arrowprops=dict(facecolor='black', shrink=0.05),
#              fontsize=12)
# 显示网格
plt.grid(True)
plt.tight_layout()
# 保存为矢量图（PDF 或 SVG）
plt.savefig('refinement.svg', format='svg', bbox_inches='tight')  # 保存为 PDF 格式
# plt.savefig('line_plot.svg')  # 保存为 SVG 格式

# 显示图表
plt.show()
