import engine as eg
import time
from copy import deepcopy
overlap = False
#e = eg.Engine('./data/폭조합용 세부자료_V2_190916.xls','./data/원자재내역.XLS',overlap)
e = eg.Engine('./data/폭조합용 세부자료_V3_일반재.xls','./data/원자재내역_200604.xlsx','./data/mim.xlsx',overlap,1)
e.read_file()
e.speed_ratio = 1
alloy = ["A1050"]#,"A1250""A1050","A1100","A8079","A3003","A8021","F308","F309","BRW04"]
## A3003, F308, BRW04, F309-> 적절한 원자재가 없음

start = time.time()


e.overlap = overlap


for i in alloy:
    temp_e = deepcopy(e)
    #over_producton_rate = 0.3 #추가 비율
    num_of_thread = 8

    if num_of_thread>8:
        num_of_loop = int(num_of_thread/8)
        print(num_of_loop)
        remainder = num_of_thread%8
        print(remainder)
        for j in range(num_of_loop):
            temp_e.run_thread(i,8) #alloy name, 추가 생산비율, 중복허용여부
        temp_e.run_thread(i,remainder)

    else:
        temp_e.run_thread(i,num_of_thread)

    print("finish! How long time: ",time.time()-start)
    best_result = temp_e.select_best_result()

    del temp_e
    title = "update_my_algo"
    title+='_t_'+str(round(time.time()-start,2))+'s'
    e.save_excel(i,best_result,title)
