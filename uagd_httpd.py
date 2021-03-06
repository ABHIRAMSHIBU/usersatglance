#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import plotly.express as px
import plotly.express as px
import time,os
import sys
import linecache
import gc

st.set_page_config(page_title="User at Glance", page_icon=None, layout='wide', initial_sidebar_state='collapsed')
st.title("User at Glance")
gc.collect()
def getUserCount():
    return int(os.popen("cat /etc/passwd | wc -l").read().strip())

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def provider(dir,param,pp):
    buff = time.time()
    all_files = os.listdir(dir)
    all_id = [int(i.split(".")[1]) for i in all_files]
    del all_files
    all_id.sort()
    # pp = 30*pp # 60*0.5*hour
    user_id = {}
    user_id_generator=0
    #----------------
    # Single File cond
    # Multi File cond
    # Data
    # Data Processing
    #----------------
    #Single file Cond
    dataMatrix=[]
    max_users = getUserCount()
    fileCurrent = open(f"{dir}/uag.{all_id[-1]}.log","rb")

        # Seek to end to know size
    eof=fileCurrent.seek(0,2)
    fileCurrent.seek(0,0)
    count=0
    insertIndex=0
    while(True):
        if(fileCurrent.tell()>=eof):
            break
        data=pickle.load(fileCurrent)
        ts=data["TimeStamp"]
        body=data["log"]
        users=body.keys()
        row = [0 for i in range(max_users)]
        for i in users:
            if i not in user_id:
                user_id[i]=user_id_generator
                user_id_generator+=1
            current_user_id = user_id[i]
            row[current_user_id] = float(body[i][param])
        row.insert(0,ts)
        dataMatrix.append(row)
        count+=1
    fileCurrent.close()
    #Multi File cond
    if(count<pp and len(all_id)>1):
        fileCurrent = open(f"{dir}/uag.{all_id[-2]}.log","rb")
            # Seek to end to know size
        eof=fileCurrent.seek(0,2)
        fileCurrent.seek(0,0)
        while(True):
            if(fileCurrent.tell()>=eof):
                break
            data=pickle.load(fileCurrent)
            ts=data["TimeStamp"]
            body=data["log"]
            users=body.keys()
            row = [0 for i in range(max_users)]
            for i in users:
                if i not in user_id:
                    user_id[i]=user_id_generator
                    user_id_generator+=1
                current_user_id = user_id[i]
                row[current_user_id] = float(body[i][param])
            row.insert(0,ts)
            dataMatrix.insert(insertIndex,row)
            insertIndex+=1
            count+=1
    #We are left with count no data
    dataMatrix = np.array(dataMatrix,dtype=float)[:,:len(user_id)+1]
    if param in ['vmem','rmem']:
        dataMatrix[:,1:] = dataMatrix[:,1:]/(1024*1024)
    ans = pd.DataFrame(dataMatrix,columns = ["time"]+list(user_id.keys())).set_index(["time"]).iloc[-pp:,:]
    del dataMatrix
    return ans

def ts_to_time(ts):
    return str(datetime.fromtimestamp(int(ts)))

all_param = ['cpu', 'vmem', 'rmem', 'pmem', 'tasks']
side_param = st.sidebar.radio("Select Mode",["Individual","All"])
if side_param == "Individual":
    param = st.selectbox(label = "Type of Resource", options=all_param)
    auto_update = st.checkbox("Auto-Update")
    past_points = st.select_slider("History Range",[i for i in range(60,720*2)])
    chart = st.empty()
    chart1 = st.empty()
    counter = 0
    hogger_title = st.empty()
    hogger_data = st.empty()
    if param == "cpu":
        Y_TITLE = "CPU use (%)"
    elif param == "vmem":
        Y_TITLE = "Virtual Memory use (GB)"
    elif param == "rmem":
        Y_TITLE = "Residential Memory use (GB)"
    elif param == "pmem":
        Y_TITLE = "Percentage Memory use (%)"
    elif param == "tasks":
        Y_TITLE = "Tasks (Thread)"
    while(True):
        if counter%30 == 0:
            f = provider("/var/log/uag/", param, past_points)
            actual_points = f.shape[0]
            f["time"] = f.index
            f["time"] = f["time"].apply(ts_to_time)
            f = f.set_index(["time"])
            fig = px.line(f)
            fig.layout = dict(title=f"{param} usage for {actual_points} points", xaxis = dict(type="category", categoryorder='category ascending', title="Time"), yaxis = dict(title=Y_TITLE))
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightYellow')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightYellow')    
            # fig.update_layout(width=1700,height=700)
            chart.plotly_chart(fig,use_container_width=True)#,width=1100,height=900)
            counter = 0

            hogger_title.subheader("Hogger Board")
            hogger_data.write(pd.DataFrame(f.mean(),columns=[f"{param} usage"]).sort_values(by=f"{param} usage",ascending=False))
        counter+=1
        chart1 = st.empty()
        if not auto_update:
            break
        time.sleep(1)
        
elif side_param == "All":
    past_points = st.select_slider("History Range",[i for i in range(60,720*2)])
    for i in all_param:
        if i == "cpu":
            Y_TITLE = "CPU use (%)"
        elif i == "vmem":
            Y_TITLE = "Virtual Memory use (GB)"
        elif i == "rmem":
            Y_TITLE = "Residential Memory use (GB)"
        elif i == "pmem":
            Y_TITLE = "Percentage Memory use (%)"
        elif i == "tasks":
            Y_TITLE = "Tasks (Thread)"
        f = provider("/var/log/uag/", i, past_points)
        actual_points = f.shape[0]
        f["time"] = f.index
        f["time"] = f["time"].apply(ts_to_time)
        f = f.set_index(["time"])
        fig = px.line(f,)
        fig.layout = dict(title=f"{i} usage for {actual_points} points", xaxis = dict(type="category", categoryorder='category ascending', title="Time"), yaxis = dict(title=Y_TITLE))
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightYellow')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightYellow')
        # fig.update_layout(width=1700,height=700)
        st.plotly_chart(fig,use_container_width=True)#,width=1100,height=900)
