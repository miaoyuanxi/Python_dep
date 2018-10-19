#coding=utf-8
# 2018/10/11-15:33-2018

# encoding=utf-8
a = int(input("请输入第1个数字:"))
b = int(input("请输入第2个数字:"))
c = int(input("请输入第3个数字:"))
d = int(input("请输入第4个数字:"))
list1 = [a, b, c, d]
list2 = []
list3 = []
symbols = ["+", "-", "*", "/"]
class FindException(Exception):
    pass
try:
    for i in range(4):
        one = list1[i]
        list2 = list1[0:i] + list1[i + 1:]
        for j in range(3):
            two = list2[j]
            list3 = list2[0:j] + list2[j + 1:]
            for k in range(2):
                three = list3[k]
                four = (list3[0:k] + list3[k + 1:])[0]
                for s1 in symbols:
                    for s2 in symbols:
                        for s3 in symbols:
                            express = "((one {0} two) {1} three) {2} four".format(s1, s2, s3)
                            if eval(express) == 24:
                                print("(({0} {1} {2}) {3} {4}) {5} {6} = 24".format(one, s1, two, s2, three, s3, four))
                                raise FindException
    print("无法算出")
except FindException:
    pass