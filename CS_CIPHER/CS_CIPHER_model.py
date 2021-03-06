#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = "HugeChaos"

from gurobipy import *
import CS_CIPHER.CS_CIPHER_specify
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
    for i in range(0, 8):
        statement += sbox(var1[8*i:8*(i+1)], var2[8*i:8*(i+1)], ine)
    return statement


def get_auxiliary_var(head1):
    auxiliary_var = []
    mat = CS_CIPHER.CS_CIPHER_specify.dl
    for r in range(0, len(mat)):
        for c in range(0, len(mat[0])):
            if mat[r][c] != 0:
                auxiliary_var.append("{}_{}_{}".format(head1, r, c))
    return auxiliary_var


def diffusion1(var1, var2, auxiliary_var_head):
    statement = ""
    auxiliary_var = get_auxiliary_var(auxiliary_var_head)
    mat = CS_CIPHER.CS_CIPHER_specify.dl
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


def diffusion_layer(var1, var2, auxiliary_var_head):
    statement = ""
    auxiliary_var = []
    for i in range(0, 4):
        statement1, auxiliary_var1 = diffusion1(var1[16*i:16*(i+1)], var2[16*i:16*(i+1)], "{}_{}".format(auxiliary_var_head, i))
        statement += statement1
        auxiliary_var += auxiliary_var1
    return statement, auxiliary_var


def var_perm(var):
    l1 = [0, 4, 1, 5, 2, 6, 3, 7]
    res = ["" for ii in range(0, 64)]
    for i in range(0, 8):
        for j in range(0, 8):
            res[8 * i + j] = var[8 * l1[i] + j]
    return res


def var_dec(var, rou):
    return ["{}_{}_{}".format(var, rou, i) for i in range(0, 64)]


def propagate(cd):
    statement = ""
    all_var = []
    x = var_dec("x", 0)
    begin_var = copy.deepcopy(x)
    for rou in range(0, cd["total_round"]):
        all_var.append(copy.deepcopy(x))

        y = var_dec("y", rou)
        all_var.append(copy.deepcopy(y))

        statement1, aux_var1 = diffusion_layer(copy.deepcopy(x), copy.deepcopy(y), "t_{}".format(rou))
        statement += statement1
        all_var.append(copy.deepcopy(aux_var1))
        x1 = var_dec("x", rou + 1)

        statement += sbox_layer(copy.deepcopy(y), copy.deepcopy(var_perm(x1)), cd["inequalities"])

        x = copy.deepcopy(x1)
    all_var.append(copy.deepcopy(x))
    end_var = copy.deepcopy(x)
    return begin_var, end_var, statement, all_var


def head():
    return "Minimize\n\nSubject To\n"


def var_assign_value(var, value):
    statement = ""
    for i in range(0, 64):
        statement += "{} = {}\n".format(var[i], value[i])
    return statement


def trailer(all_var):
    statement = "Binary\n"
    for var in all_var:
        for i in range(0, len(var)):
            statement += "{}\n".format(var[i])
    statement += "END"
    return statement


def model(cd):
    statement = head()
    begin_var, end_var, statement1, all_var = propagate(cd)
    statement += var_assign_value(copy.deepcopy(begin_var), copy.deepcopy(cd["b"]))
    statement += statement1
    statement += var_assign_value(copy.deepcopy(end_var), copy.deepcopy(cd["e"]))
    statement += trailer(all_var)
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
