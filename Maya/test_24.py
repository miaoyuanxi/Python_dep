#coding=utf-8
# 2018/10/11-15:31-2018


# encoding=utf-8
# 用你熟悉的程序语言实现 算24 的算法
# 已知4个整数，数字范围在1-13之间，求计算方法（限加减乘除，可带括号），可以计算出24
import itertools
import copy
a = int(input("请输入第1个数字:"))
b = int(input("请输入第2个数字:"))
c = int(input("请输入第3个数字:"))
d = int(input("请输入第4个数字:"))
inputList = [a, b, c, d]
listAll = []  # 用来存储这个列表数字的排列组合 [[],[],[],[]......]
listSignIndex = []  # 用来存储输出的运算符号顺序下表 0,1,2,3 对应 + - * /
listSign = []  # 用来存储输出的运算符号 + - * /
listSet = list(itertools.permutations(inputList, 4))  # 无序排列组合
for i in listSet:
    listAll.append(list(i))  # 用list()把元组转换成列表
# 把运算符号的下表转换成对应的符号
def changeIndexToSign():
    for i in listSignIndex:
        if i == 0:
            listSign.append("+")
        elif i == 1:
            listSign.append("-")
        elif i == 2:
            listSign.append("*")
        elif i == 3:
            listSign.append("/")
last = []
def start():
    global last
    while 1:
        for list1 in listAll:
            val = list1[0]
            last = copy.deepcopy(list1)
            for i in range(4):
                if i == 0:
                    val += list1[1]
                elif i == 1:
                    val -= list1[1]
                elif i == 2:
                    val *= list1[1]
                elif i == 3:
                    val /= list1[1]
                val2 = val  # 保存当前的val值 即list1[0] list1[1]运算的值
                for j in range(4):
                    if j == 0:
                        val += list1[2]
                    elif j == 1:
                        val -= list1[2]
                    elif j == 2:
                        val *= list1[2]
                    elif j == 3:
                        val /= list1[2]
                    val1 = val  # 保存当前的val值 即list1[0] list1[1] list[2]运算的值
                    for k in range(4):
                        if k == 0:
                            val += list1[3]
                        elif k == 1:
                            val -= list1[3]
                        elif k == 2:
                            val *= list1[3]
                        elif k == 3:
                            val /= list1[3]
                        if val == 24:
                            listSignIndex.append(i)
                            listSignIndex.append(j)
                            listSignIndex.append(k)
                            changeIndexToSign()
                            return
                        else:
                            val = val1  # 如果这次循环不行，就把那么把val还置为list1[0] list1[1] list[2]运算的值
                    val = val2  # 如果第3值运算完了没有结束，那么把val还置为list1[0] list1[1]运算的值
                val = list1[0]  # 如果第3，第4 值运算完了没有结束，那么把val还置为list1[0]值
start()
listSign.append("");
lastStr = "(("
for i in range(4):
    if i == 1 or i == 2:
        lastStr += str(last[i]) + ")" + listSign[i]
    else:
        lastStr += str(last[i]) + listSign[i]
print(lastStr)