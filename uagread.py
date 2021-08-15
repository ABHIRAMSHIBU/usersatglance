import sys
import pickle
from pprint import pprint
count=0
if(len(sys.argv)>1):
    if(sys.argv[1]=="--help" or sys.argv[1]=="-h"):
        print("Example Usage")
        print("To open 0th log")
        print("\t"+sys.argv[0]+" uag.0.log")
    else:
        f=open(sys.argv[1],"rb")
        end = f.seek(0,2)
        f.seek(0,0)
        while(True):
            try:
                data=pickle.load(f)
                pprint(data)
                count+=1
                if(f.tell()==end):
                    break
            except:
                print("Data corruption detected, exiting")
                break
            
else:
    print(sys.argv[0]+" --help")

print("The count was",count)