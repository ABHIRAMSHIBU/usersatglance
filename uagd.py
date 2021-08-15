import json
import os, pickle
import time
f=None
files_id=None
count=None
def getNewLogFile():
    global files_id
    global f
    f.close()
    files_id.append(files_id[-1]+1)
    f = open(f"/var/log/uag/uag.{files_id[-1]}.log", 'ab+')
    if len(files_id)>2:
        for i in files_id[:-2]:  
            os.remove("/var/log/uag/uag."+str(i)+".log")
def insertLog(logObject):
    global count
    global files_id
    global f
    if(count==720):
        getNewLogFile()
        count=0
    pickle.dump(logObject,f)
    f.flush()
    count+=1
if(not os.path.exists("/var/log/uag")):
    os.mkdir("/var/log/uag")
files=os.listdir("/var/log/uag")
files_id =[ int(i.split(".")[1]) for i in files ]
if files_id==[]:
    files_id.append(0)
del files
files_id.sort()
if(len(files_id)>2):
    for i in files_id[:-2]:  
        os.remove("/var/log/uag/uag."+str(i)+".log")
    files_id=files_id[:-2]
f = open(f"/var/log/uag/uag.{files_id[-1]}.log", 'ab+')
end = f.tell()
count = 0
seek=0
if end != 0:
    try:
        while(f.tell()!=end):
            seek = f.tell()
            pickle.load(f)
            count+=1
    except:
        f.seek(seek)

if count == 720:
    getNewLogFile()
try:
    while True:
        uag_out = os.popen("/usr/bin/env python3 uag.py -j").read() 
        timestamp = str(int(time.time()))
        uag_out = json.loads(uag_out)
        logObject = {"TimeStamp":timestamp,"log":uag_out}
        insertLog(logObject)
        time.sleep(30)
except KeyboardInterrupt:
    f.close()