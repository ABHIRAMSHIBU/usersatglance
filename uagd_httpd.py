import streamlit as st
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import plotly.express as px
import plotly.express as px
import time,os

st.set_page_config(page_title="User at Glance", page_icon=None, layout='wide', initial_sidebar_state='collapsed')
st.title("User at Glance")

def provider(dir, param, pp):
    all_files = os.listdir(dir)
    all_id = [int(i.split(".")[1]) for i in all_files]
    del all_files
    all_id.sort()
    pp = 30*pp # 60*0.5*hour

    print("Less than 24 hours!")
    f=open(f"{dir}/uag.{all_id[-1]}.log","rb")
    end = f.seek(0,2)
    f.seek(0,0)
    first_flag = True
    count=0
    lowdataFallback=False
    while(True):
        try:
            data=pickle.load(f)
            if(f.tell()==end):
                break
            else:
                count+=1
            if first_flag:
                plot_data = pd.DataFrame(columns=list(data['log'].keys()))
                first_flag = False
            temp_cpu = []
            for i in data['log'].keys():
                temp_cpu.append(data["log"][i][param])
            plot_data.loc[data["TimeStamp"]] = temp_cpu
            
        except Exception as e:
            print("Data corruption detected, exiting")
            break
    if(count<pp):
        lowdataFallback=True

    if lowdataFallback:
        print("FALL BACK>> LOW DATA COND")
        f1=open(f"{dir}/uag.{all_id[-1]}.log","rb")
        try:
            f2=open(f"{dir}/uag.{all_id[-2]}.log","rb")
            end = f2.seek(0,2)
            f2.seek(0,0)
            first_flag = True
            while(True):
                try:
                    data=pickle.load(f2)
                    if(f2.tell()==end):
                        break
                    else:
                        count+=1
                    if first_flag:
                        plot_data = pd.DataFrame(columns=list(data['log'].keys()))
                        first_flag = False
                    temp_cpu = []
                    for i in data['log'].keys():
                        temp_cpu.append(data["log"][i][param])
                    plot_data.loc[data["TimeStamp"]] = temp_cpu
                except Exception as e:
                    print("Data corruption detected, exiting")
                    break
            end = f1.seek(0,2)
            f1.seek(0,0)
            while(True):
                try:
                    data=pickle.load(f1)
                    if(f1.tell()==end):
                        break
                    temp_cpu = []
                    for i in data['log'].keys():
                        temp_cpu.append(data["log"][i][param])
                    plot_data.loc[data["TimeStamp"]] = temp_cpu
                except Exception as e:
                    print("Data corruption detected, exiting")
                    break
        except IndexError:
            pp=719
    print(count)
        
    
    return plot_data.iloc[-pp:,:]
def ts_to_time(ts):
    return str(datetime.fromtimestamp(int(ts)))

all_param = ['cpu', 'vmem', 'rmem', 'pmem', 'tasks']
side_param = st.sidebar.radio("Select Mode",["Individual","All"])
if side_param == "Individual":
    param = st.selectbox(label = "Type of Resource", options=all_param)
    auto_update = st.checkbox("Auto-Update")
    past_points = st.select_slider("History Range (Hr)",[i for i in range(1,49)])
    chart = st.empty()
    chart1 = st.empty()
    counter = 0
    while(True):
        if counter%30 == 0:
            f = provider("/var/log/uag/", param, past_points)
            f["time"] = f.index
            f["time"] = f["time"].apply(ts_to_time)
            f = f.set_index(["time"])
            fig = px.line(f)
            fig.layout = dict(title=param, xaxis = dict(type="category", categoryorder='category ascending'))
            # fig.update_layout(width=1700,height=700)
            chart.plotly_chart(fig,use_container_width=True)#,width=1100,height=900)
            counter = 0
        counter+=1
        chart1 = st.empty()
        if not auto_update:
            break
        time.sleep(1)
        
elif side_param == "All":
    past_points = st.select_slider("History Range (Hr)",[i for i in range(1,49)])
    for i in all_param:
        f = provider("/var/log/uag/", i, past_points)
        f["time"] = f.index
        f["time"] = f["time"].apply(ts_to_time)
        f = f.set_index(["time"])
        fig = px.line(f)
        fig.layout = dict(title=i, xaxis = dict(type="category", categoryorder='category ascending'))
        # fig.update_layout(width=1700,height=700)
        st.plotly_chart(fig,use_container_width=True)#,width=1100,height=900)
