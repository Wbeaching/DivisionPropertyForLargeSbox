#!/usr/bin/python
# -*- coding: UTF-8 -*-

import copy
import AES.AES_model
import time
import os
import AES.AES_specify

if __name__ == "__main__":

    cd = dict()

    cd["cipher_name"] = "AES"

    cd["cipher_size"] = 128

    cd["inequalities"] = AES.AES_specify.inequalities_EDPPT

    folder = cd["cipher_name"] + "_max_round"
    if not os.path.exists(folder):
        os.mkdir(folder)

    distinguish_find = True

    search_space = list()

    for bi in range(0, 4):
        for bj in range(0, 4):
            for bk in range(0, 8):
                b = [[[1 for bkk in range(0, 8)] for bjj in range(0, 4)] for bii in range(0, 4)]
                b[bi][bj][bk] = 0
                for ei in range(0, 4):
                    for ej in range(0, 4):
                        for ek in range(0, 8):
                            e = [[[0 for ekk in range(0, 8)] for ejj in range(0, 4)] for eii in range(0, 4)]
                            e[ei][ej][ek] = 1
                            search_space.append(copy.deepcopy([copy.deepcopy(b), copy.deepcopy(e)]))

    round_i = 0
    cd["record_file"] = folder + "////" + cd["cipher_name"] + "_record.txt"
    cd["time_record"] = folder + "////" + cd["cipher_name"] + "_time_record.txt"
    total_search = len(search_space)
    ttt1 = time.time()
    while distinguish_find:
        distinguish_find = False
        round_i += 1
        cd["solve_file"] = folder + "////" + cd["cipher_name"] + "_round{}.lp".format(round_i)
        t1 = time.time()
        search_count = 0
        cd["total_round"] = round_i
        for ss in search_space:
            cd["b"] = copy.deepcopy(ss[0])
            cd["e"] = copy.deepcopy(ss[1])

            t11 = time.time()
            search_count += 1
            AES.AES_model.model(cd)
            flag = AES.AES_model.model_solve(cd["solve_file"])
            t22 = time.time()
            print(t22 - t11)
            if flag:
                rf = open(cd["record_file"], "a")
                rf.write("*" * 20)
                rf.write("{} round integral distinguish based on division property is found.\n".format(round_i))
                rf.write("when the values:\n")
                rf.write("b = {}\n".format(str(cd["b"])))
                rf.write("e = {}\n".format(str(cd["e"])))
                rf.close()
                distinguish_find = True
                break
            else:
                print("testing: round = {}, search_count = {}, total_search = {}".format(round_i, search_count, total_search))
        t2 = time.time()
        tf = open(cd["time_record"], "a")
        if distinguish_find:
            tf.write("After " + str(t2 - t1) + "time, we found {} rounds integral distinguish.\n\n".format(round_i))
        else:
            tf.write("After " + str(t2 - ttt1) + "time, we show no {} round integral distinguish.\n\n".format(round_i))
        tf.close()
