import engine as eg
import time
from copy import deepcopy

e = eg.Engine('/home/leo/알류미늄/폭조합용 세부자료_V2_190916.xls','원자재내역.XLS')
e.read_file()
alloy = ["A1100","A8079"]#,"A8079"]#,"A1100","A1235","A3003","A8021","F308","F309","BRW04"]
start = time.time()
for i in alloy:
    temp_e = deepcopy(e)
    residual_rate = 0.3
    nun_of_thread = 30
    if nun_of_thread>5:
        num_of_loop = int(nun_of_thread/10)
        for j in range(num_of_loop):
            temp_e.run_thread(i,10,residual_rate)
    else:
        temp_e.run_thread(i,nun_of_thread,residual_rate)

    print("finish! How long time: ",time.time()-start)
    best_result = temp_e.select_best_result()
    del temp_e
    e.save_excel(i,best_result)


#e.run_thread('A1050',1)
#print("finish! How long time: ",time.time()-start)
#best_result = e.select_best_result()
#e.save_excel('A1050',best_result)
