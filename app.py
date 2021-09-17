# import library
import pywebio
from pywebio.input import input, FLOAT, file_upload
from pywebio.output import put_text, put_html, put_markdown, put_table, put_buttons, put_file, put_processbar, set_processbar, put_row, clear
from pywebio.session import hold

import gurobi as gp
from gurobi import GRB
import pandas as pd
import numpy as np
from gurobipy import quicksum
import time
import io

# function to calculate model
def btn_click(btn_val):
    put_text("Solving ...")
    put_processbar('bar')
    for i in range(1, 11):
        set_processbar('bar', i / 10)
        time.sleep(0.1)
    # put_text("You click %s " % btn_val)
    # prepare date before fed to model
    # Setting global variable
    classes = btn_val[0]
    k = btn_val[1]
    old_class = list(range(1, len(classes)+1))
    new_class = list(range(1, int(k)+1))
    print(new_class)
    w_stu = 1
    w_phy = 1
    w_mus = 1

    students = [list(classes[i]['Student'].values) for i in range(len(classes))]
    N = [len(students[i]) for i in range(len(students))]

    study = [list(classes[i]['Study'].values) for i in range(len(classes))]
    sport = [list(classes[i]['Physical'].values) for i in range(len(classes))]
    music = [list(classes[i]['Musical'].values) for i in range(len(classes))]
    leadership = [list(classes[i]['Leadership'].values) for i in range(len(classes))]
    gender = [list(classes[i]['Gender'].values) for i in range(len(classes))]
    piano = [list(classes[i]['Piano'].values) for i in range(len(classes))]
    star = [list(classes[i]['Star'].values) for i in range(len(classes))]
    relay = [list(classes[i]['Relay'].values) for i in range(len(classes))]
    marathon = [list(classes[i]['Marathon'].values) for i in range(len(classes))]
    pair = [list(classes[i]['Pair'].values) for i in range(len(classes))]
    unpair = [list(classes[i]['Unpair'].values) for i in range(len(classes))]



    # map score
    score_study = {(students[j][i], old_class[j], new_class[k]) : study[j][i] for j in range(len(old_class)) for i in range(N[j]) for k in range(len(new_class))}
    score_sport = {(students[j][i], old_class[j], new_class[k]) : sport[j][i] for j in range(len(old_class)) for i in range(N[j]) for k in range(len(new_class))}
    score_music = {(students[j][i], old_class[j], new_class[k]) : music[j][i] for j in range(len(old_class)) for i in range(N[j]) for k in range(len(new_class))}
    score_leadership = {(students[j][i], old_class[j], new_class[k]) : leadership[j][i] for j in range(len(old_class)) for i in range(N[j]) for k in range(len(new_class))}
    score_gender = {(students[j][i], old_class[j], new_class[k]) : gender[j][i] for j in range(len(old_class)) for i in range(N[j]) for k in range(len(new_class))}
    score_piano = {(students[j][i], old_class[j], new_class[k]) : piano[j][i] for j in range(len(old_class)) for i in range(N[j]) for k in range(len(new_class))}
    score_star = {(students[j][i], old_class[j], new_class[k]) : star[j][i] for j in range(len(old_class)) for i in range(N[j]) for k in range(len(new_class))}
    score_relay = {(students[j][i], old_class[j], new_class[k]) : relay[j][i] for j in range(len(old_class)) for i in range(N[j]) for k in range(len(new_class))}
    score_marathon = {(students[j][i], old_class[j], new_class[k]) : marathon[j][i] for j in range(len(old_class)) for i in range(N[j]) for k in range(len(new_class))}
    score_pair = {(students[j][i], old_class[j], new_class[k]) : pair[j][i] for j in range(len(old_class)) for i in range(N[j]) for k in range(len(new_class))}
    score_unpair = {(students[j][i], old_class[j], new_class[k]) : unpair[j][i] for j in range(len(old_class)) for i in range(N[j]) for k in range(len(new_class))}

    # Declare and initialize model
    m = gp.Model('RAP')

    # Add variables to model
    x = m.addVars([(students[j][i], old_class[j], new_class[k]) for j in range(len(old_class)) for i in range(N[j]) for k in range(len(new_class))], name='x', vtype='B')
    # max-min study score
    ms = m.addVar()
    ss = m.addVar()
    mp = m.addVar()
    sp = m.addVar()
    mm = m.addVar()
    sm = m.addVar()

    # Debug
    # Add constraints to model
    class_old = m.addConstrs((x.sum(i, j, '*') == 1 for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)), name='old_class')
    class_reor_max = m.addConstrs((x.sum('*', j, k) <= int(N[j-1]/len(new_class)) + 1 for j in range(1, len(old_class)+1) for k in new_class), name='reor_class_max')
    class_reor_min = m.addConstrs((x.sum('*', j, k) >= int(N[j-1]/len(new_class)) for j in range(1, len(old_class)+1) for k in new_class), name='reor_class_max')
    class_new_max = m.addConstrs((x.sum('*','*', k) <= int(sum(N)/len(new_class)) + 1 for k in new_class), name='new_class_max')
    class_new_min = m.addConstrs((x.sum('*','*', k) >= int(sum(N)/len(new_class)) for k in new_class), name='new_class_min')

    max_study = m.addConstrs((gp.quicksum(x[i,j,k] * score_study[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) <= ms for k in new_class), name='maxs')
    min_study = m.addConstrs((gp.quicksum(x[i,j,k] * score_study[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) >= ss for k in new_class), name='mins')

    max_sport = m.addConstrs((gp.quicksum(x[i,j,k] * score_sport[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) <= mp for k in new_class), name='maxsp')
    min_sport = m.addConstrs((gp.quicksum(x[i,j,k] * score_sport[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) >= sp for k in new_class), name='minsp')

    max_music = m.addConstrs((gp.quicksum(x[i,j,k] * score_music[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) <= mm for k in new_class), name='maxm')
    min_music = m.addConstrs((gp.quicksum(x[i,j,k] * score_music[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) >= sm for k in new_class), name='minm')

    lead = m.addConstrs((gp.quicksum(x[i,j,k] * score_leadership[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) >= 1 for k in new_class), name='laed')
    piano = m.addConstrs((gp.quicksum(x[i,j,k] * score_piano[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) >= 1 for k in new_class), name='piano')

    all_gen = 0 # calculate all gender
    for j in range(len(old_class)):
        all_gen += sum(gender[j])
    gen_max = m.addConstrs((gp.quicksum(x[i,j,k] * score_gender[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) <= int(all_gen/len(new_class)) + 1 for k in new_class), name='gender_max')
    gen_min = m.addConstrs((gp.quicksum(x[i,j,k] * score_gender[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) >= int(all_gen/len(new_class)) for k in new_class), name='gender_min')

    all_star = 0 # calculate all star
    for j in range(len(old_class)):
        all_star += sum(star[j])
    star_max = m.addConstrs((gp.quicksum(x[i,j,k] * score_star[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) <= int(all_star/len(new_class)) + 1 for k in new_class), name='star_max')
    star_min = m.addConstrs((gp.quicksum(x[i,j,k] * score_star[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) >= int(all_star/len(new_class)) for k in new_class), name='star_min')

    relay_boy = m.addConstrs((gp.quicksum(x[i,j,k] * score_relay[i,j,k] * score_gender[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) >= 4 for k in new_class), name='relay_b')
    relay_girl = m.addConstrs((gp.quicksum(x[i,j,k] * score_relay[i,j,k] * (1-score_gender[i,j,k]) for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) >= 4 for k in new_class), name='relay_g')

    all_marathon = 0
    for j in range(len(old_class)):
        all_marathon += sum(marathon[j])
    marathon_max = m.addConstrs((gp.quicksum(x[i,j,k] * score_marathon[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) <= int(all_marathon/len(new_class)) + 1 for k in new_class), name='mara_max')
    marathon_min = m.addConstrs((gp.quicksum(x[i,j,k] * score_marathon[i,j,k] for j in range(1, len(old_class)+1) for i in range(1, N[j-1]+1)) >= int(all_marathon/len(new_class)) for k in new_class), name='mara_min')

    a = []
    for j in old_class:
        l = [(x+1, y+1) for x in range(N[j-1]) for y in range(N[j-1]) if pair[j-1][x] == pair[j-1][y] and pair[j-1][x] > 0 and pair[j-1][y]>0 and x!=y]
        print(l)
        data = {tuple(sorted(item)) for item in l}
        data = list(data)
        a.append(data)
    i_1_j = []
    i_2_j = []
    i_1 = []
    i_2 = []
    for i in a:
        #print(i)
        for s in i:
            i_1.append(s[0])
            i_2.append(s[1])
        i_1_j.append(i_1)
        i_2_j.append(i_2)
        i_1=[]
        i_2=[]
    pair_con = m.addConstrs(((x[i,j,k]) == (x[l,j,k]) for j in range(1, len(old_class)+1) for i in i_1_j[j-1] for l in i_2_j[j-1] for k in new_class), name='pair')

    b = []
    for j in old_class:
        l = [(x+1, y+1) for x in range(N[j-1]) for y in range(N[j-1]) if unpair[j-1][x] == unpair[j-1][y] and unpair[j-1][x] > 0 and unpair[j-1][y]>0 and x!=y]
        print(l)
        data = {tuple(sorted(item)) for item in l}
        data = list(data)
        b.append(data)
    print(b)
    ui_1_j = []
    ui_2_j = []
    ui_1 = []
    ui_2 = []
    for i in b:
        #print(i)
        for s in i:
            ui_1.append(s[0])
            ui_2.append(s[1])
        ui_1_j.append(ui_1)
        ui_2_j.append(ui_2)
        ui_1=[]
        ui_2=[]

    print(type(ui_1_j))
    for j in range(1, len(old_class)+1):
        print(j)
        print("---")
        for i in ui_1_j[j-1]:
            print(i)


    print(type(i_1_j))
    for j in range(1, len(old_class)+1):
        print(j)
        print("---")
        for i in i_1_j[j-1]:
            print(i)
    unpair_con = m.addConstrs(((x[i,j,k]) * (x[l,j,k]) == 0 for j in range(1, len(old_class)+1) for i in ui_1_j[j-1] for l in ui_2_j[j-1] for k in new_class), name='unpair')



    # Set objective function
    m.setObjective((ms-ss)*w_stu + (mp-sp)*w_phy + (mm-sm)*w_mus,  GRB.MINIMIZE)
    m.write('RAP_Global.lp')
    m.optimize()

    # # Display optimal values of decision variables
    for v in m.getVars():
        if v.x > 1e-6:
            print(v.varName, v.x)

    # # Display optimal total matching score
    put_text('Solved')
    put_text('Total matching score: ', m.objVal)

    # Save table
    table = []
    for j in range(1, len(old_class)+1):
        for i in range(1, N[j-1]+1):
            for k in new_class:
                if(x[i, j, k].X == 1):
                    table.append([i,j,k])

    # Save file to download
    df = pd.DataFrame(table, columns=['Student No.', 'Old class', 'New class'])
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False)  # write to BytesIO buffer
    towrite.seek(0)
    put_file('assignment.xlsx', towrite.getvalue(), 'Download file')
    return table

def cro():
    #height = input("Input your height(cm)：", type=FLOAT)
    #weight = input("Input your weight(kg)：", type=FLOAT)
    put_markdown('# **Class Re-organization Problem**')
    classes_file = file_upload(multiple=True)
    print(type(classes_file))




    #print(classes_file)
    #print(classes_file[0])
    df = pd.DataFrame(classes_file)
    print(df)
    print(df['content'])

    # convert file to data frame
    classes = []
    for content in df['content']:
        text = content
        text = text.decode("utf-8")
        data = text
        df_data = pd.DataFrame([x.split(',') for x in data.split('\r\n')])
        new_header = df_data.iloc[0] #grab the first row for the header
        df_data = df_data[1:] #take the data less the header row
        df_data.columns = new_header #set the header row as the df header
        df_data['﻿Student'] = df_data.rename(columns = {'﻿Student': 'Student'}, inplace = True)
        df_data = df_data.drop('﻿Student', axis=1)
        df_data = df_data.reset_index(drop=True)
        print(df_data.dtypes)
        df_data = df_data.astype('int64')
        print(df_data.dtypes)
        classes.append(df_data)
    print(classes)

    k = input("Input number of new classes", type=FLOAT)
    print(type(k))
    table = btn_click([classes,k])
    put_table(table, header=["Student No.", "Old class", "New class"])
    hold()

if __name__ == '__main__':
    pywebio.start_server(cro, port=80)