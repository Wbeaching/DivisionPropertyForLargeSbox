#!/usr/bin/python
# -*- coding: UTF-8 -*-

import copy
import AES.AES_model
import time
import os
import AES.AES_specify


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


if __name__ == "__main__":

    cd = dict()

    cd["cipher_name"] = "AES"

    cd["cipher_size"] = 128

    cd["inequalities"] = AES.AES_specify.inequalities_EDPPT

    folder = cd["cipher_name"] + "_integral_distinguish"
    if not os.path.exists(folder):
        os.mkdir(folder)

    distinguish_find = True

    e_search_space = list()
    e_dict = dict()
    for ei in range(0, 4):
        for ej in range(0, 4):
            for ek in range(0, 8):
                e = [[[0 for ekk in range(0, 8)] for ejj in range(0, 4)] for eii in range(0, 4)]
                e[ei][ej][ek] = 1
                e_search_space.append(copy.deepcopy(e))
                e_dict[str(e)] = [ei, ej, ek]

    round_i = 4
    cd["total_round"] = round_i
    cd["record_file"] = folder + "////" + cd["cipher_name"] + "_record.txt"
    cd["time_record"] = folder + "////" + cd["cipher_name"] + "_time_record.txt"
    cd["solve_file"] = folder + "////" + cd["cipher_name"] + "_round{}.lp".format(round_i)
    t1 = time.time()
    for weight in range(1, 5):
        distinguish_find = False
        distinguish_count = 0

        cd["search_apace"] = folder + "////" + "search_weight{}.txt".format(weight)

        for b in get_b_search_space(weight):
            f = open(cd["search_apace"], "a")
            f.write(str(b) + "\n")
            f.close()

            cd["b"] = copy.deepcopy(b)
            balance_position = [[["?" for bpk in range(0, 8)] for bpj in range(0, 4)] for bpi in range(0, 4)]
            distinguish_find1 = False
            for e in e_search_space:
                cd["e"] = copy.deepcopy(e)
                AES.AES_model.model(cd)
                flag = AES.AES_model.model_solve(cd["solve_file"])
                if flag:
                    bll = e_dict[str(e)]
                    balance_position[bll[0]][bll[1]][bll[2]] = "0"
                    distinguish_find1 = True
            if distinguish_find1:
                distinguish_find = True
                distinguish_count += 1
                rf = open(cd["record_file"], "a")
                rf.write("*" * 20)
                rf.write("{}th  4round integral distinguish (weight = {}) based on division property"
                         " is found.\n".format(distinguish_count, weight))
                rf.write("when the values:\n")
                rf.write("b = {}\n".format(str(cd["b"])))
                rf.write("the balance position is:\n")
                for row in balance_position:
                    rf.write(str(row) + "\n")
                rf.close()
        if distinguish_find:
            break
    t2 = time.time()
    f = open(cd["time_record"], "w")
    f.write("this process cost time total {}".format(t2 - t1))
    f.close()
