import engine as eg


e = eg.Engine('/home/leo/알류미늄/폭조합용 세부자료_V2_190916.xls','원자재내역.XLS')
e.read_file()
selected_list, temp_order_group_data, temp_stock_group_data = e.get_combination('A8021')
combi_df,result_df = e.get_result_data(selected_list, temp_order_group_data,temp_stock_group_data)
e.save_excel('A8021',combi_df,result_df)



