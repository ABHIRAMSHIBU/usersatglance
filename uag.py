import subprocess as sp
import os
from pprint import pprint
import sys
json=None
json_output=False
argv = sys.argv
if(len(argv)>1):
    if(argv[1]=="--json" or argv[1]=="-j"):
        json_output=True
        import json
ps = sp.Popen("ps -aux",stdout=sp.PIPE,shell=True)
python_pid=os.getpid()
output=ps.stdout.read().decode().split("\n")
output.pop()
list_of_process=[]
for i in output:
    try:
        split_i = i.split()
        split_i[10] = " ".join(split_i[10:])
        split_i = split_i[:11]
        list_of_process.append(split_i)
    except Exception as e:
        print("EXCEPTION:",e)
        print("ERROR:",i)
#print(output)
title = list_of_process.pop(0)
del output
table = dict()
for i in list_of_process:
    try:
        user,pid,cpu,pmem,vmem,rmem,tty,status,startt,exect,command = i
        if(int(pid)==int(python_pid) or int(pid)==int(ps.pid)):
            continue
        if(user in table.keys()):
            table[user]["cpu"]+=float(cpu)
            table[user]["vmem"]+=int(vmem)
            table[user]["rmem"]+=int(rmem)
            table[user]["pmem"]+=float(pmem)
            table[user]["tasks"]+=1
        else:
            table[user]={}
            table[user]["cpu"]=float(cpu)
            table[user]["vmem"]=int(vmem)
            table[user]["rmem"]=int(rmem)
            table[user]["pmem"]=float(pmem)
            table[user]["tasks"]=1
    except Exception as e:
        print("EXCEPTION_1:",e)
        print("ERROR_1:",i)
if(not json_output):
    pprint(table)
    print("TOTAL CPU:",sum([table[i]["cpu"] for i in table]))
else:
    print(json.dumps(table))
