import engine as eg
import time

e = eg.Engine('/home/leo/알류미늄/폭조합용 세부자료_V2_190916.xls','원자재내역.XLS')
e.read_file()
start = time.time()
e.run_thread('A1235',10)
print("finish! How long: ",time.time()-start)
best_result = e.select_best_result()
e.save_excel('A1235',best_result)
