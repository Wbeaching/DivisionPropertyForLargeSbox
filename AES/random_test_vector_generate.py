#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = "HugeChaos"


import random
import copy


def weight_select1(l1, l2, l3, len1):
    if len(l3) == len1:
        l2.append(l3)
        return l2
    elif len(l1) == 0:
        return l2
    else:
        l2p = []
        for i in range(0, len(l1)):
            l3.append(l1[i])
            l2q = weight_select1(copy.deepcopy(l1[(i+1):]), copy.deepcopy(l2), copy.deepcopy(l3), len1)
            l2p += copy.deepcopy(l2q)
            l3.remove(l1[i])
        return l2p


'''
def weight_select(len1):
    l11 = [i for i in range(0, 16)]
    l22 = []
    l33 = []
    l222 = weight_select1(l11, l22, l33, len1)
    return l222
'''


def weight_select(len1):
    l11 = [0, 5, 10, 15]
    l12 = []
    l13 = []
    l14 = weight_select1(l11, l12, l13, len1)

    l21 = [1, 6, 11, 12]
    l22 = []
    l23 = []
    l24 = weight_select1(l21, l22, l23, len1)

    l31 = [2, 7, 8, 13]
    l32 = []
    l33 = []
    l34 = weight_select1(l31, l32, l33, len1)

    l41 = [3, 4, 9, 14]
    l42 = []
    l43 = []
    l44 = weight_select1(l41, l42, l43, len1)

    return l14 + l24 + l34 + l44


def get_b_search_space(len1):
    vec = weight_select(len1)
    b_search_space = list()
    for vec1 in vec:
        b = [[[0 for bkk in range(0, 8)] for bjj in range(0, 4)] for bii in range(0, 4)]
        for vec11 in vec1:
            for k in range(0, 8):
                b[vec11//4][vec11 % 4][k] = 1
        b_search_space.append(copy.deepcopy(b))
    return b_search_space


def generate_random_test_vector0(bound):
    search_space = list()
    count = 0
    total_b_space = get_b_search_space(1) + get_b_search_space(2) + get_b_search_space(3) + get_b_search_space(4)
    total_b_space_len = len(total_b_space)
    while count < bound:
        weight = random.randint(0, total_b_space_len - 1)
        b = copy.deepcopy(total_b_space[weight])

        e = [[[0 for ekk in range(0, 8)] for ejj in range(0, 4)] for eii in range(0, 4)]
        ei = random.randint(0, 3)
        ej = random.randint(0, 3)
        ek = random.randint(0, 7)
        e[ei][ej][ek] = 1
        sp = copy.deepcopy([copy.deepcopy(b), copy.deepcopy(e)])
        if sp not in search_space:
            search_space.append(sp)
            count += 1
    f = open("test_vector.py", "w")
    f.write("#!/usr/bin/python\n# -*- coding: UTF-8 -*-\n\n")
    f.write("tv0 = [")
    for i in range(0, bound):
        f.write(str(search_space[i]))
        if i != bound - 1:
            f.write(",\n")
    f.write("]")
    f.close()


def generate_random_test_vector1(bound):
    search_space = list()
    count = 0
    while count < bound:
        b = [[[1 for bkk in range(0, 8)] for bjj in range(0, 4)] for bii in range(0, 4)]
        e = [[[0 for ekk in range(0, 8)] for ejj in range(0, 4)] for eii in range(0, 4)]

        bi = random.randint(0, 3)
        bj = random.randint(0, 3)
        bk = random.randint(0, 7)
        b[bi][bj][bk] = 0

        ei = random.randint(0, 3)
        ej = random.randint(0, 3)
        ek = random.randint(0, 7)
        e[ei][ej][ek] = 1
        sp = copy.deepcopy([copy.deepcopy(b), copy.deepcopy(e)])
        if sp not in search_space:
            search_space.append(sp)
            count += 1
    f = open("test_vector.py", "a")
    f.write("\n\n\ntv1 = [")
    for i in range(0, bound):
        f.write(str(search_space[i]))
        if i != bound - 1:
            f.write(",\n")
    f.write("]")
    f.close()


generate_random_test_vector0(512)
generate_random_test_vector1(512)
