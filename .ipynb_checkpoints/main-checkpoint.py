import engine as eg
import threading 

e = eg.Engine('./data/폭조합용 세부자료_V2_190916.xls','./data/원자재내역.XLS')
e.read_file()
e.run_thread('A8021',20)

best_result = e.select_best_result()
e.save_excel('A8021',best_result)
for i in e.compare_list:
	print(i)

