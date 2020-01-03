import engine as eg
import time
from copy import deepcopy

e = eg.Engine('./data/폭조합용 세부자료_V2_190916.xls','./data/원자재내역.XLS')
e.read_file()
alloy = ["A1235"]#,"A1050","A1100","A8079",,"A8079","A3003","A8021","F308","F309","BRW04"]
start = time.time()
overlap = True
title = "중복붏허"

if overlap:
    title = "중복허용"

for i in alloy:
    temp_e = deepcopy(e)
    residual_rate = 0.3
    num_of_thread = 1
    if num_of_thread>8:
        num_of_loop = int(num_of_thread/8)
        print(num_of_loop)
        remainder = num_of_thread%8
        print(remainder)
        for j in range(num_of_loop):
            temp_e.run_thread(i,8,residual_rate,overlap)
        temp_e.run_thread(i,remainder,residual_rate,overlap)

    else:
        temp_e.run_thread(i,num_of_thread,residual_rate,overlap)

    print("finish! How long time: ",time.time()-start)
    best_result = temp_e.select_best_result()
    del temp_e
    e.save_excel(i,best_result,title)


#e.run_thread('A1050',1)
#print("finish! How long time: ",time.time()-start)
#best_result = e.select_best_result()
#e.save_excel('A1050',best_result)
