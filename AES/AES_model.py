#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = "HugeChaos"

from gurobipy import *
import AES.AES_specify
import copy
import os


def sbox(var1, var2, ine):
    statement = ""
    for row in ine:
        temp = []
        for u in range(0, 8):
            temp.append(str(row[u]) + " " + var1[7 - u])
        for v in range(0, 8):
            temp.append(str(row[v + 8]) + " " + var2[7 - v])
        temp1 = " + ".join(temp)
        temp1 = temp1.replace("+ -", "- ")
        s = str(-row[16])
        s = s.replace("--", "")
        temp1 += " >= " + s + "\n"
        statement += temp1
    return statement


def sbox_layer(var1, var2, ine):
    statement = ""
    for i in range(0, 4):
        for j in range(0, 4):
            statement += sbox(var1[i][j], var2[i][j], ine)
    return statement


def get_mds_auxiliary_var(head):
    auxiliary_var = []
    mat = AES.AES_specify.MDS
    for r in range(0, len(mat)):
        for c in range(0, len(mat[0])):
            if mat[r][c] != 0:
                auxiliary_var.append("{}_{}_{}".format(head, r, c))
    return auxiliary_var


def mc(var1, var2, auxiliary_var_head):
    statement = ""
    auxiliary_var = get_mds_auxiliary_var(auxiliary_var_head)
    mat = AES.AES_specify.MDS
    for j in range(0, len(mat[0])):
        temp = []
        for i in range(0, len(mat)):
            if mat[i][j] == 1:
                temp.append("{}_{}_{}".format(auxiliary_var_head, i, j))
        t = " + ".join(temp)
        statement += "{} - {} = 0\n".format(t, var1[j])
    for i in range(0, len(mat)):
        temp = []
        for j in range(0, len(mat[0])):
            if mat[i][j] == 1:
                temp.append("{}_{}_{}".format(auxiliary_var_head, i, j))
        t = " + ".join(temp)
        statement += "{} - {} = 0\n".format(t, var2[i])
    return statement, auxiliary_var


def mc_layer(var1, var2, auxiliary_var_head):
    statement = ""
    auxiliary_var = []
    for col in range(0, len(var1[0])):
        v1 = []
        v2 = []
        for row in range(0, len(var1)):
            v1 += copy.deepcopy(var1[row][col])
            v2 += copy.deepcopy(var2[row][col])
        statement1, auxiliary_var1 = mc(copy.deepcopy(v1), copy.deepcopy(v2), "{}_{}".format(auxiliary_var_head, col))
        statement += statement1
        auxiliary_var += copy.deepcopy(auxiliary_var1)
    return statement, auxiliary_var


def sr(var):
    """the ith row and j-th col of res is from the t-th row and (j+i)%4 th col of var(var left rotation i)"""
    res = [[["" for k in range(0, len(var[0][0]))] for j in range(0, len(var[0]))] for i in range(0, len(var))]
    for i in range(0, len(var)):
        for j in range(0, len(var[0])):
            for k in range(0, len(var[0][0])):
                res[i][j][k] = var[i][(j + i) % len(var[0])][k]
    return res


def var_dec(var, rou):
    return [[["{}_{}_{}_{}_{}".format(var, rou, i, j, k) for k in range(0, 8)] for j in range(0, 4)] for i in range(0, 4)]


def propagate(cd):
    statement = ""
    all_var = []
    auxiliary_var = []
    x = var_dec("x", 0)
    begin_var = copy.deepcopy(x)
    for rou in range(0, cd["total_round"]):
        all_var.append(copy.deepcopy(x))

        y = var_dec("y", rou)
        all_var.append(copy.deepcopy(y))

        statement += sbox_layer(copy.deepcopy(x), copy.deepcopy(y), cd["inequalities"])
        yy = copy.deepcopy(sr(copy.deepcopy(y)))
        x1 = var_dec("x", rou + 1)
        statement1, auxiliary_var1 = mc_layer(copy.deepcopy(yy), copy.deepcopy(x1), "t_{}".format(rou))
        statement += statement1
        auxiliary_var += copy.deepcopy(auxiliary_var1)
        x = copy.deepcopy(x1)
    all_var.append(copy.deepcopy(x))
    end_var = copy.deepcopy(x)
    return begin_var, end_var, statement, all_var, auxiliary_var


def head():
    return "Minimize\n\nSubject To\n"


def var_assign_value(var, value):
    statement = ""
    for i in range(0, 4):
        for j in range(0, 4):
            for k in range(0, 8):
                statement += "{} = {}\n".format(var[i][j][k], value[i][j][k])
    return statement


def trailer(all_var, auxiliary_var):
    statement = "Binary\n"
    for var in all_var:
        for i in range(0, 4):
            for j in range(0, 4):
                for k in range(0, 8):
                    statement += "{}\n".format(var[i][j][k])
    for var in auxiliary_var:
        statement += "{}\n".format(var)
    statement += "END"
    return statement


def model(cd):
    statement = head()
    begin_var, end_var, statement1, all_var, auxiliary_var = propagate(cd)
    statement += var_assign_value(copy.deepcopy(begin_var), copy.deepcopy(cd["b"]))
    statement += statement1
    statement += var_assign_value(copy.deepcopy(end_var), copy.deepcopy(cd["e"]))
    statement += trailer(all_var, auxiliary_var)
    if os.path.exists(cd["solve_file"]):
        os.remove(cd["solve_file"])
    f = open(cd["solve_file"], "w")
    f.write(statement)
    f.close()


def model_solve(milp_file):
    m = read(milp_file)
    m.optimize()
    if m.Status == 2:
        return False
    elif m.Status == 3:
        return True
    else:
        print("unknown error!")
