import utils
import pandas as pd
import random
from datetime import datetime
import math
from collections import Counter
from functools import reduce
import threading 

class Engine:
	def __init__(self,order_file_name,material_file_name):
		self.order_file_name=order_file_name
		self.material_file_name=material_file_name
		self.material_data = pd.DataFrame()
		self.order_data = pd.DataFrame()
		self.big_group_name_list = [];
		self.big_group_index_list=[]
		self.material_name_list=[]
		self.material_index_list=[]
		self.result_list = []
		self.compare_list = []

	def read_file(self):
		self.order_data = pd.read_excel(self.order_file_name)
		self.material_data = pd.read_excel(self.material_file_name)
		self.process_data()
		self.set_big_and_material_group_info()

    #재고기반 grouping
	def process_data(self):

		## data sorting 
		self.material_data = self.material_data.sort_values(by=['ALLOY','TEMPER','포장중량','실폭','생산일자'],ascending=False).reset_index()
		self.order_data = self.order_data.fillna(0)
		self.order_data = self.order_data.drop(['팀'],axis=1)

		## 데이터 정리 -> 폭조합 x, 제품코드 0, 생산량 0 행 제거
		drop_index=[]
		for i in range(len(self.order_data)):
			if self.order_data['제품코드'][i]==0 or self.order_data['폭조합'][i]=='X' or self.order_data['생산량'][i] == 0:
				drop_index.append(i)
		self.order_data = self.order_data.drop(drop_index)
		self.order_data = self.order_data.reset_index(drop=True)

		## 횟수 설정
		self.order_data['횟수']=0
		for i in range(len(self.order_data)):
			thickness = self.order_data['두께'][i]
			width = self.order_data['폭'][i]
			length = self.order_data['길이(기준)'][i]
			goal_weight = self.order_data['생산량'][i]
			repeat = utils.calculateRepeat(thickness,width,length,goal_weight)
			if utils.check_doubling(self.order_data['권취'][i]) and (repeat)%2 !=0 : ## 더블링인 경우 2의 배수로 저장
				repeat+=1
			self.order_data['횟수'][i] = repeat

		self.order_data['const_횟수'] = self.order_data['횟수']
		self.order_data['const_addition_횟수'] = 0 
		self.order_data['addition_횟수'] = 0
		self.order_data = self.order_data.sort_values(by=['ALLOY_1','권취','TEMPER','원자재_M','원자재_T','두께','길이(기준)','내경','코아','폭'],\
				                      ascending=False).reset_index(drop=True)

    
	def set_big_and_material_group_info(self):

		## set big group info
		for i in range(self.order_data.shape[0]):
			temp=str(self.order_data['ALLOY_1'][i])
			temp=utils.translate_alloy(temp)
			check = 0
			for j in range(len(self.big_group_name_list)):
				if(temp==self.big_group_name_list[j]):
			 	   check +=1
			 	   break

			if(check==0):
				self.big_group_name_list.append(temp)
				self.big_group_index_list.append(i)

		## set material group info
		for i in range(self.material_data.shape[0]):
			temp=str(self.material_data['ALLOY'][i])
			check = 0
			for j in range(len(self.material_name_list)):
				if(temp==self.material_name_list[j]):
				    check +=1
				    break
			if(check==0):
				self.material_name_list.append(temp)
				self.material_index_list.append(i)
		

	

	def get_certain_big_group_info(self,certain_big_group_name):
		##small_group 선택
		group_name =  certain_big_group_name
		temp_order_group_data = pd.DataFrame()
		temp_material_group_data = pd.DataFrame()

		#small_group_name에 맞는 order data 추출
		for i in range(len(self.big_group_name_list)):
			if group_name == (self.big_group_name_list[i]):
				material_index = i
				break
		if i != len(self.big_group_name_list)-1:
			temp_order_group_data = self.order_data[self.big_group_index_list[material_index]:self.big_group_index_list[material_index+1]].reset_index(drop=True)       
		else:
			temp_order_group_data = self.order_data[self.big_group_index_list[material_index]:len(self.order_data)].reset_index(drop=True)       


		#small_group_name에 맞는 material data 추출
		for i in range(len(self.material_name_list)):
			if group_name == self.material_name_list[i]:
				material_index = i
				break
		if i != len(self.material_name_list)-1:
			temp_material_group_data = self.material_data[self.material_index_list[material_index]:self.material_index_list[material_index+1]].reset_index(drop=True)
		else:
			temp_material_group_data = self.material_data[self.material_index_list[material_index]:len(self.material_data)].reset_index(drop=True)
		    	    
		## 새롭게 sorting
		temp_order_group_data = temp_order_group_data.sort_values(by=['권취','TEMPER','원자재_M','원자재_T','두께','길이(기준)','내경','코아','폭'],\
				                            ascending=False).reset_index(drop=True) 

		##set small group
		small_group_name =[]
		small_group_index = []
		for i in range(temp_order_group_data.shape[0]):
			temp=str(temp_order_group_data['권취'][i])+"-"
			temp+=str(temp_order_group_data['TEMPER'][i])+"-" 
			temp+=str(temp_order_group_data['원자재_M'][i])+"-"
			temp+=str(temp_order_group_data['원자재_T'][i])+"-"
			temp+=str(temp_order_group_data['두께'][i])+"-"
			temp+=str(temp_order_group_data['내경'][i])+"-"
			temp+=str(temp_order_group_data['길이(기준)'][i])+"-"
			temp+=temp_order_group_data['코아'][i]
			check = 0
			for j in range(len(small_group_name)):
				if(temp==small_group_name[j]):
					check +=1
					break
			if(check==0):
				small_group_name.append(temp)
				small_group_index.append(i)

		small_group_name.append("end")
		small_group_index.append(len(temp_order_group_data))

		##set middle group        
		middle_group_name = []
		middle_group_index=[]
		for i in range(temp_order_group_data.shape[0]):
			temp=str(temp_order_group_data['권취'][i])+'-'
			temp+=str(temp_order_group_data['TEMPER'][i])+"-"
			temp+=str(temp_order_group_data['원자재_M'][i])+"-"
			temp+=str(temp_order_group_data['원자재_T'][i])+"-"
			temp+=str(temp_order_group_data['두께'][i])
			check = 0
			for j in range(len(middle_group_name)):
				if(temp==middle_group_name[j]):
					check +=1
					break
			if(check==0):
				middle_group_name.append(temp)
				middle_group_index.append(i)

		middle_group_name.append("end")
		middle_group_index.append(len(temp_order_group_data))

		return temp_order_group_data, temp_material_group_data ,\
			middle_group_name, middle_group_index, \
			small_group_name, small_group_index; 

	def get_combination(self, certain_big_group_name):
		temp_order_group_data, temp_material_group_data , \
		middle_group_name, middle_group_index, \
		small_group_name, small_group_index = self.get_certain_big_group_info(certain_big_group_name)
	
		CONST_OUT_OF_COUNT_NUM = 100000
		RESIDUAL_RATE = 0.3

		SUM_OF_SCOURE = 0 
		SUM_OF_SCOURE_COUNT = 0
		SUM_OF_TOTAL_COUNT = 0
		temp_order_group_data['횟수'] = temp_order_group_data['const_횟수'] 
		temp_order_group_data['addition_횟수'] = 0 #temp_order_group_data['const_addition_횟수'] 

		#랜덤으로 값 추출
		#조합 가능한 폭 list
		selected_list = []
		selected_material=[]
		selected_df_list=[]

		count_zero=-1
		sum_residual=0
		sum_addition_weight = 0
		selected_weight=0
		total_count = utils.sum_list(temp_order_group_data['횟수'])
		total_addition_count = 0 
		current_count = 0 

		best_selected_list = []
		select_list = []
		best_sum_weight = 0

		next = False

		for r in range(len(middle_group_index)-len(middle_group_index),len(middle_group_index)-1):#len(middle_group_index)-1            
			start_index=0
			end_index = 0
			      
			for i in range(len(small_group_index)): #'권취','TEMPER','두께'가 동일한 범위 선택(middle group 선택)
				if middle_group_index[r] == small_group_index[i]: 
					start_index = i
				elif middle_group_index[r+1] == small_group_index[i]:
					end_index = i
					break;
			
			##남은 middle group 내 남은 무게 계산
			middle_group_total_weight = 0
			middle_group_total_count = 0
			for i in range(small_group_index[start_index],small_group_index[end_index]):
				if temp_order_group_data['횟수'][i]!= CONST_OUT_OF_COUNT_NUM: ##남은 횟수 확인
					middle_group_total_count += temp_order_group_data['횟수'][i]
				
			combi_try_count = -1
			standard_score = 100
				
			n= 0
			total_best_score = -CONST_OUT_OF_COUNT_NUM
			total_best_select_list = []
			total_best_material_num = -1
			total_best_residual = CONST_OUT_OF_COUNT_NUM
			total_best_addition_weight = 0
			total_best_combi_weight = 0
			total_best_material_realweight = 0
			total_tri_count = 0
			need_new_material_soure = 0
			one_more = 0
			
			     
			#print("small_group_index[start_index],small_group_index[end_index]"\
			#	      ,small_group_index[start_index],small_group_index[end_index])
			#print("middle_group_total_count",middle_group_total_count)
				
			range_weight = small_group_index[end_index] - small_group_index[start_index]
				
			while middle_group_total_count > 0: #  and total_tri_count < len(temp_material_group_data)  
				combi_try_count +=1
				search_count = -1

				new_material = False
				    
				## 원자재 검색
				possible = False
				while 1:
					#n = utils.find_possible_index(tried_material_list, selected_material, len(temp_material_group_data),n)
					#tried_material_list.append(n)
					#print(tried_material_list)
					#n += 1
					n = random.randrange(0,len(temp_material_group_data))
					#n = n%len(temp_material_group_data)

					## 원자재 정보 setting
					material_code = temp_material_group_data['제품코드'][n]
					material_company=material_code[len(material_code)-1]
					material_temper = temp_material_group_data['TEMPER'][n]
					const_width = temp_material_group_data['실폭'][n]
					material_alloy = utils.translate_alloy(temp_material_group_data['ALLOY'][n]) 
					width = temp_material_group_data['실폭'][n]
					weight = float(temp_material_group_data['포장중량'][n])/1000
					thickness = temp_order_group_data['두께'][small_group_index[start_index]]
					cal_realweight= utils.calculateRealweight(thickness,weight)
					if certain_big_group_name == 'A8021' and temp_order_group_data['원자재_M'][middle_group_index[r]] == '무관':
						order_material = 'N'
					else:
						order_material = temp_order_group_data['원자재_M'][middle_group_index[r]]
					
					possible = utils.check_material(material_company,material_temper,thickness,\
								          order_material,\
								          temp_order_group_data['원자재_T'][middle_group_index[r]],\
								          temp_order_group_data['두께'][middle_group_index[r]])
					if possible:
						break
					
					search_count +=1
					if search_count > len(temp_material_group_data)*(2.5):
						## 사용 가능한 원자재가 없을 경우 -> 새로운 조건을 넣어야함
						new_material = True
						possible = False
						break
					    
				#새로운 원자재를 구매해야하는 경우
					
				if need_new_material_soure >len(temp_material_group_data)*(2.5):
					#print("need new material!!!!%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
					break;
				      
				if not possible and new_material:
					#print("not possible and new_material")
					need_new_material_soure +=1      
					
				else:   ##원자재 존재할 경우 -> 조합 시작
	  
					#print("material_code: ",material_code, n)
					combi_list=[]
					combi_index_list=[]
					combi_count_list=[]
					#print("width",width)
					SUM_OF_TOTAL_COUNT +=1
					for i in range(start_index,end_index):  #'권취','TEMPER','두께' 일치
					    
						max_index_count = 0
					    
						## group_index_start, group_index_end 설정
						group_index_start = small_group_index[i]
						if i < len(small_group_index)-1:
							group_index_end = small_group_index[i+1]
						else:
							group_index_end = small_group_index[i]
						
						## 산업재, 박박, 후박, FIN 등
						detail_code = temp_order_group_data['세부품목'][group_index_start]
						
						## 횟수 확인, 남은 횟수에 따라 확률값 부여
						count_index = [] #<- (확률,index)
						max_index_count = 0
						sum_count = 0 
						for j in range(group_index_start,group_index_end):
						
							#rand_choice = random.randrange(0,2)
							## 횟수가 없는 오더도 포함
							if temp_order_group_data['횟수'][j]<CONST_OUT_OF_COUNT_NUM:
								prob = temp_order_group_data['횟수'][j]#*temp_order_group_data['횟수'][j]
								count_index.append((prob,j)) 
								max_index_count += temp_order_group_data['횟수'][j]##횟수에 맞게 max_index_count 설정
								sum_count += prob
							## 횟수 모두 사용한 경우: 최초에 횟수가 10 이상일 경우 확률 1로 값 부여
							elif (temp_order_group_data['addition_횟수'][j] == 0 and\
								temp_order_group_data['const_횟수'][j] > 10) :
								count_index.append((1,j)) 
								max_index_count += 1 
								sum_count += 1
						     
						temp_list=[]
						temp_index_list=[]
						temp_count_list=[]
					    	
						## 횟수가 양수일 경우 -> elements(조합) 구함
						if sum_count >0:
						
							count_index.sort(reverse=True)   
							index_count = -1
							index = -1
						
							min_width = temp_order_group_data['폭'][group_index_end-1]
							initial_mim_width = utils.get_mim_width(1,thickness,material_alloy,detail_code)
							max_index_count *=2
							while (index_count < max_index_count and width >= min_width+initial_mim_width): #'ALLOY','권취','TEMPER','두께','길이','내경','코아','폭' 일치
								temp_list.append([])
								temp_index_list.append([])
								temp_count_list.append([])
								index_count += 1
								index += 1
								extra_width = width
							    
								try_combi_count = 0
								check_only_addition = True
								num_of_combi = 0
								pre_mim_width = 0
							    
							    
							   	#addition_mim_width = initial_mim_width
								while(extra_width >= min_width and try_combi_count<100):
								##횟수에 비례해서 선택
									rand = random.randrange(0,sum_count)
									for k in range(len(count_index)):
										rand -= count_index[k][0]
										if rand < 0:
											j = count_index[k][1]
											break
									#j =0 
									mim_width = utils.get_mim_width(num_of_combi+1,thickness,material_alloy,detail_code) 
									addition_mim_width = mim_width - pre_mim_width
									
									if utils.check_push(temp_list[index],temp_order_group_data['폭'][j]+addition_mim_width,width):
									    
										if temp_order_group_data['횟수'][j] < CONST_OUT_OF_COUNT_NUM:
											check_only_addition = False ## 추가 오더만으로 생산은 필요 없음
										temp_list[index].append(temp_order_group_data['폭'][j]+addition_mim_width)
										temp_count_list[index].append(temp_order_group_data['횟수'][j])
										temp_index_list[index].append(j) #해당 index 저장
										extra_width -= (temp_order_group_data['폭'][j]+addition_mim_width)
										num_of_combi +=1
										pre_mim_width = mim_width
									try_combi_count+=1
							   	### special_addition_count_list -> 남은 생산량 있는데 입력 조합에 초과해서 들어갈 경우
							    	## special_addition_count_list[i] -> [초과횟수,index]
								special_addition_count_list = [] 
							    
								if len(temp_count_list[index]) > 0 and (not check_only_addition):
									## 중복 index가 가능한 조합인지 확인
									count_index_list = Counter(temp_index_list[index])
									for k in range(len(temp_index_list[index])):
									    ## 중복되는 만큼 가능 횟수 나누어줌
										temp_count_list[index][k] = temp_count_list[index][k] // count_index_list[temp_index_list[index][k]]
									    
										if temp_count_list[index][k] == 0: ## 초과 입력되는 경우
											temp_count_list[index][k] =2 ##doubling을 고려하여 2번
											find_index = False
											for a in range(len(special_addition_count_list)):
												if special_addition_count_list[a][1] == temp_index_list[index][k]: ##해당 index가 있을 경우
													special_addition_count_list[a][0] += 2 ##초과 횟수 추가
													find_index = True
													break;
												
											if not find_index: ##해당 index가 없을 경우 새롭게 생성 [초과횟수(2),index]
											    special_addition_count_list.append([2,temp_index_list[index][k]])
								    
								    #본 조합이 좋은 조합이면 살리고 아니면 죽임
								if not(utils.checkCombination(temp_list,temp_index_list,index,extra_width,width)) \
									    or check_only_addition:
									del temp_list[index]
									del temp_index_list[index]
									del temp_count_list[index]
									index += -1
								
							#좋은 조합 모음 and 새로운 조합
							if len(temp_list)!=0 and temp_order_group_data['길이(기준)'][j] >0:
							    temp_list.append(temp_order_group_data['길이(기준)'][j])#각 조합의 길이는 마지막에 넣음
							    combi_list.append(temp_list)
							    combi_index_list.append(temp_index_list)
							    combi_count_list.append(temp_count_list)
						

					########조합 종목 선택
			       
					#elements(조합) 변환 ->  해당 원자재에 맞게 elements 변환 -> 변환된 elements를 조합하여 set을 만듬
					sorted_realweight_list = [] #무게, 횟수, index_list, count_list, combi_list, 가로 손실 길이 ,낭비량
				       
					max_realweight = 0
					if len(combi_list)>0 :
						for i in range(len(combi_list)):
						#각 조합의 길이는 마지막에 있음
							temp_length = combi_list[i][len(combi_list[i])-1]
							for j in range(len(combi_list[i])-1): 
							    
								min_repeat_count = min(combi_count_list[i][j])
								#print(combi_index_list)
								temp_w = utils.sum_list(combi_list[i][j])
								temp = []
								doubing = utils.check_doubling(temp_order_group_data['권취'][combi_index_list[i][0][0]])

								for k in range(min_repeat_count):
									if (doubing and (k+1)%2 ==0) or (not doubing): ##더블링 조건에 맞게 무게 계산
									    	## 낭비량 계산 
										temp_residual = round(utils.realWeight(thickness,(width)-temp_w,temp_length,1,k+1)/1000)
										zero_list = []
										for l in range(len(combi_count_list[i][j])):
											zero_list.append(0)
										
									    	#무게, 횟수, index_list, count_list, combi_list, 추가 count_list ,가로 손실 길이 ,낭비량
										temp.append([round(utils.realWeight(thickness,temp_w,temp_length,1,k+1)/1000,2),k+1\
										         ,combi_index_list[i][j],combi_count_list[i][j],combi_list[i][j],zero_list,\
										         (width)-temp_w,temp_residual])
									    
								if len(temp)!=0:
									temp.sort(reverse=True)
									sorted_realweight_list.append(temp)
				  
					## elements 없을 경우
					if len(sorted_realweight_list)==0:
					    standard_score -= 0.1
					    combi_try_count +=1
						
					    
					else:   #elements 조합 시작 -> set 생성
					    #원자재 무게보다 많이 나가는 조합 버림       
						for i in range(len(sorted_realweight_list)):
							del_index=0
							for j in range(len(sorted_realweight_list[i])):
								if sorted_realweight_list[i][j][0] > cal_realweight:
									del_index = j
								else:
									sorted_realweight_list[i] = sorted_realweight_list[i][del_index:len(sorted_realweight_list[i])]
									break;
						        
					    	## 초기 잔여량은 원자재 사용 무게 / 무게 순으로 sort
						select_residual=CONST_OUT_OF_COUNT_NUM
					    	#select_addition_weight=0
						select_list=[]
						sorted_realweight_list.sort(reverse=True)
						start_combi=True
						best_score = -CONST_OUT_OF_COUNT_NUM
						combi_weight = 0
						max_count = 1
					    
						##max_count 설정
						for i in range(len(sorted_realweight_list)):
							max_count += len(sorted_realweight_list[i])#*len(sorted_realweight_list[i])
					   
						count = -1
						max_count *=2
						while(count<max_count):
							count+=1
							temp_list = []
							combi_count = 0 
							temp_total_extra = cal_realweight
							temp_sum_redisual = 0
							temp_try_count = -1
							temp_combi_weight = 0
							temp_extra_width = 0 
							   
							while(combi_count<2 and temp_try_count<10):
							    
								temp_try_count += 1
								i = random.randrange(0,len(sorted_realweight_list))
								j = random.randrange(0,len(sorted_realweight_list[i]))
								
							    	## overlap check
								check_overlap_index = False
								temp_select_index = sorted_realweight_list[i][j][2][:]
								temp_select_index.sort()
								for a in range(len(temp_list)):
									for b in range(len(temp_list[a])):
										temp_check_index_list = temp_list[a][2][:]
										temp_check_index_list.sort()
									if temp_check_index_list == temp_select_index:
										check_overlap_index = True
										break;
								        
								#추가로 더 넣을 수 있는지 확인
								if temp_total_extra -(sorted_realweight_list[i][j][0]+sorted_realweight_list[i][j][-1]) >= -cal_realweight*0.02\
									and (not check_overlap_index):
							    
									temp_list.append(sorted_realweight_list[i][j])
									temp_total_extra -= (sorted_realweight_list[i][j][0]+sorted_realweight_list[i][j][-1])
									temp_sum_redisual += sorted_realweight_list[i][j][-1]
									temp_combi_weight += sorted_realweight_list[i][j][0]
									temp_extra_width += sorted_realweight_list[i][j][-2]
									combi_count +=1
								
							temp_score = -CONST_OUT_OF_COUNT_NUM
							temp_addition_weight = 0
						
						## 추가 생산량이 있더라도 한번도 생산하지 않은 것들을 생산
						used = True
						for i in range(len(temp_list)):
						    for j in range(len(temp_list[i][2])):
						        k = temp_list[i][2][j]
						        if temp_order_group_data['횟수'][k] == temp_order_group_data['const_횟수'][k] or \
						            (temp_order_group_data['횟수'][j] >5 and temp_order_group_data['횟수'][j] <9):#:#
						            used = False
						            break;
						        #elif (temp_order_group_data['횟수'][j] <3):
						        #    used = True
						        #    break;
						                
						if temp_total_extra <= cal_realweight*RESIDUAL_RATE or not(used): # len(temp_list)>0 : #and temp_total_extra >= cal_realweight*0.1
						    
						    pre_count = 0
						    addition_count = 0
						    addition_residual = 0
						    addition_weight = 0
					    
						    #무게, 횟수, index_list, count_list, combi_list, 추가 count_list, 가로 손실 길이 ,낭비량
						    ## 가장 빈도수가 낮은 조합 횟수 최대로 늘림
						    min_index= -1
						    min_count = CONST_OUT_OF_COUNT_NUM
						    for i in range(len(temp_list)):
						        if min_count >= temp_list[i][1]:
						            min_index = i; min_count = temp_list[i][1];
						        
						    ## doubling체크
						    doubing = utils.check_doubling(temp_order_group_data['권취'][temp_list[min_index][2][0]])
						    temp_length = temp_order_group_data['길이(기준)'][temp_list[min_index][2][0]]
						    temp_w = utils.sum_list(temp_list[min_index][4])
						        
						    ## 계획을 초과하는 생산하는 횟수 따로 기록
						    while 1:
						        if ((doubing and (addition_count)%2 ==0) or (not doubing)): ##더블링 조건에 맞게 무게 계산
						            addition_weight = round(utils.realWeight(thickness,temp_w,temp_length,1,addition_count)/1000)
						            addition_residual = round(utils.realWeight(thickness,temp_list[min_index][-2],temp_length,1,addition_count)/1000)

						            if temp_total_extra - addition_weight <= 0:
						                if temp_total_extra -(addition_weight+addition_residual) < -cal_realweight*0.01:
						                    addition_count = pre_count
						                    addition_residual = round(utils.realWeight(thickness,temp_list[min_index][-2],temp_length,1,pre_count)/1000)
						                    addition_weight = round(utils.realWeight(thickness,temp_w,temp_length,1,pre_count)/1000)
						                break;
						            else:
						                pre_count = addition_count

						        addition_count+=1

						    temp_list[min_index][1] += addition_count
						    temp_list[min_index][0] += addition_weight
						               
						        ### ex) [0, 0, 0, 1] -> 나중에 그 횟수를 따로 처리
						    for i in range(len(temp_list[min_index][3])):
						        if temp_order_group_data['횟수'][temp_list[min_index][2][i]] != CONST_OUT_OF_COUNT_NUM: 
						            temp_list[min_index][5][i]= min(temp_list[min_index][3][i]-temp_list[min_index][1],0)
						        else:
						            temp_list[min_index][5][i]= -temp_list[min_index][1]

						        

						    ### 점수 계산에 필요한 값들 update            
						    temp_total_residual =(temp_total_extra-addition_weight+addition_residual)
						    temp_combi_weight += addition_weight
						    
						    #temp_addition_weight +=addition_weight
						    
						    addition_count = 0
						    combi_total_count = 0      
						    test=0
						    for i in range(len(temp_list)):
						        test += len(list(set(temp_list[i][2])))
						        combi_total_count += temp_list[i][1]*len(temp_list[i][2])
						        addition_count += -utils.sum_list(temp_list[i][5])
						        
						    ## special_addition_count_list 계산
						    if len(special_addition_count_list)!=0:
						        for i in range(len(special_addition_count_list)):
						            addition_count +=\
						            (special_addition_count_list[i][0]-temp_order_group_data['횟수'][special_addition_count_list[i][1]])
						    
						    used_material = 0;
						    for i in selected_material:
						    	if n == i:
						    		used_material = 1;	
						        						    						    

						    temp_score = 100 - (100*((temp_total_residual/cal_realweight)+2*(temp_extra_width/70))\
						                        +temp_extra_width*((combi_count-1)/3)+400*(addition_count/combi_total_count)+100*used_material) #100*(addition_weight/cal_realweight)
					
						#새로운 조합이 더 좋을 경우
						# 점수 비교
						if best_score < temp_score:
			    
						    ##중복 index 확인
						    no_overlap = True
						    temp_index_list = []

						    for i in range(len(temp_list)):
						        temp_index_list +=list(set(temp_list[i][2])) #사용되는 index list(중복 제거)

						    if temp_index_list != list(set(temp_index_list)): #다른 조합간에 겹치는 index 존재할 경우   
						        temp_index_list = list(set(temp_index_list)) #중복 제거 list 
						        test_dict = {}
						        for i in temp_index_list: #dict 초기화
						            test_dict[i] = 0
						            
						        for i in range(len(temp_list)):
						            for j in range(len(temp_list[i][2])):
						                test_dict[temp_list[i][2][j]] += temp_list[i][1] #각 index가 얼마나 사용되지 입력
						                
						            
						        for i in test_dict.keys(): 
						            if temp_order_group_data['횟수'][i] < test_dict[i]: #조합에서 사용되는 양이 사용 가능한 양보다 많을 경우
						                no_overlap = False
						                break
						                
						    if no_overlap:
						        combi_weight = temp_combi_weight
						        best_score = temp_score 
						        select_residual = temp_total_residual
						        select_list = temp_list
						
					    
						    ## total_best 초기화                                          
						if total_best_score < best_score or len(total_best_select_list)==0:
							temp_sum = 0
							for i in range(len(select_list)):
								temp_sum +=select_list[i][0]
							
								        
							if temp_sum <= cal_realweight :
								total_best_score = best_score
								total_best_select_list = select_list
								total_best_material_num = n
								total_best_material_realweight = cal_realweight
								total_best_residual = select_residual
								total_best_combi_weight = combi_weight
					
						#### 좋은 재료가 없을 경우
					if total_best_score == -CONST_OUT_OF_COUNT_NUM:
						
						need_new_material_soure +=1
						combi_try_count +=1

					#elif (standard_score<=total_best_score) and len(total_best_select_list)>0 and one_more > 1:
					#	pre_scoure = standard_score
					#	standard_score = total_best_score + math.log((120-standard_score)/(120-total_best_score))
					#	one_more += (pre_scoure/standard_score)#*(combi_try_count/len(temp_material_group_data))

					elif standard_score<=total_best_score or combi_try_count > len(temp_material_group_data)*1.5: #  and total_best_score>-50  and total_best_score>-100 
						#print("total_best_material_num: ",total_best_material_num," total_best_score: ",total_best_score, " combi_try_count: ",combi_try_count,"  len(temp_material_group_data)",len(temp_material_group_data) )
						self.compare_list.append([total_best_score,combi_try_count,len(temp_material_group_data)])
						one_more = 0
						need_new_material_soure = 0
						## 재설정
						select_list = total_best_select_list
						best_score = total_best_score
						n = total_best_material_num
						select_residual = total_best_residual
						combi_weight = total_best_combi_weight
						cal_realweight = total_best_material_realweight
						weight = float(temp_material_group_data['포장중량'][n])/1000
						width  = temp_material_group_data['실폭'][n]
						combi_try_count = 0 
						standard_score = 100

						for i in range(len(select_list)):
							for j in range(len(select_list[i][2])):
								special_addition_index = False
								for k in range(len(special_addition_count_list)):
									if select_list[i][2][j] == special_addition_count_list[k][1]:
										special_addition_index = True
										break;
								    
								if not special_addition_index:         
									if temp_order_group_data['횟수'][select_list[i][2][j]] < CONST_OUT_OF_COUNT_NUM:
										order_count = (select_list[i][1]+select_list[i][5][j])
										order_addition_count = select_list[i][5][j]    
										temp_order_group_data['횟수'][select_list[i][2][j]] -= order_count
										middle_group_total_count -= order_count
										current_count += order_count

										temp_order_group_data['addition_횟수'][select_list[i][2][j]] += order_addition_count
										total_addition_count += order_addition_count
										if temp_order_group_data['횟수'][select_list[i][2][j]] <=0:
											temp_order_group_data['횟수'][select_list[i][2][j]] = CONST_OUT_OF_COUNT_NUM    
									else:
										temp_order_group_data['addition_횟수'][select_list[i][2][j]] -= select_list[i][1]
										total_addition_count -= select_list[i][1]
								    
						if len(special_addition_count_list) !=0:
							for i in range(len(special_addition_count_list)):
								special_addition_count =\
									special_addition_count_list[i][0] - temp_order_group_data['횟수'][special_addition_count_list[i][1]]
								temp_order_group_data['addition_횟수'][special_addition_count_list[i][1]] -= special_addition_count
								current_count += temp_order_group_data['횟수'][special_addition_count_list[i][1]]
								middle_group_total_count -= temp_order_group_data['횟수'][special_addition_count_list[i][1]]
								total_addition_count -= special_addition_count
								temp_order_group_data['횟수'][special_addition_count_list[i][1]] = CONST_OUT_OF_COUNT_NUM
							special_addition_count_list = []
						temp_sum = 0
						for i in range(group_index_start,group_index_end):
							if temp_order_group_data['횟수'][i] != CONST_OUT_OF_COUNT_NUM:
								temp_sum += temp_order_group_data['횟수'][i] 
						       
								
						#print("middle_group_index range: ",small_group_index[start_index],small_group_index[end_index])
						#print("material 번호: ",n)
						#print("width: ",width,"weight:", weight)
						#print("투입량:",cal_realweight)
						#print("조합량:",combi_weight)
						#print("material_index",n,"실손량: ",select_residual)
						#제거 목록 index 선택
						sum_residual += select_residual
						selected_material.append(n)
						selected_material.sort()
						temp_selected_list = []
						temp_selected_list.append(n)
						temp_selected_list.append(select_list)
						selected_list.append(temp_selected_list)
						
						n = random.randrange(0,len(temp_material_group_data))
						SUM_OF_SCOURE += total_best_score 
						SUM_OF_SCOURE_COUNT +=1
						total_best_score = -CONST_OUT_OF_COUNT_NUM
						total_best_select_list = []
						total_best_material_num = -1
						total_best_residual = CONST_OUT_OF_COUNT_NUM
						total_best_combi_weight = 0
						total_best_material_realweight = 0

						

					elif combi_try_count > len(temp_material_group_data)*2 : #total_best_score <-500 and 
						combi_try_count =0
						break;    
					else:   
						if math.log((120-standard_score)/(120-total_best_score)) > -5:
							standard_score += math.log((120-standard_score)/(120-total_best_score)) 
						combi_try_count +=1
						
		return selected_list, temp_order_group_data ,temp_material_group_data, (SUM_OF_SCOURE/SUM_OF_SCOURE_COUNT)       

	def get_result_data(self,selected_list, temp_order_group_data,temp_material_group_data,avg_score):
		temp_order_group_data
		temp_material_group_data
		selected_list

		order_list = []
		for i in range(len(temp_order_group_data['제품코드'])):
		    order_list.append([temp_order_group_data['제품코드'][i],0,[]])
		    
		## 조합 dataframe, save excel file
		combi_df_list = []
		for i in range(len(selected_list)):
			meterial_weight = temp_material_group_data['포장중량'][selected_list[i][0]]
			temp_list =[]
			temp_list.append(temp_material_group_data['index'][selected_list[i][0]])
			temp_list.append(temp_material_group_data['제품코드'][selected_list[i][0]])
			temp_list.append(meterial_weight)
			temp_width_sum = []
			temp_weight_list = []
			temp_length_sum = ""
			temp_length = 0
			temp_count_sum = ""
			temp_index_sum = ""
			temp_order_num = []
			temp_width = ""

			for j in range(len(selected_list[i][1])):
				temp_length_sum += str(temp_order_group_data['길이(기준)'][selected_list[i][1][j][2][0]])+"  "
				temp_count_sum += str(selected_list[i][1][j][1])+"  "
				temp_index_sum += str(selected_list[i][1][j][2])+"  "
				width_sum =0
				
				for k in range(len((selected_list[i][1][j][2]))):
					temp_order_num.append(temp_order_group_data['제품코드'][selected_list[i][1][j][2][k]])
					width_sum += float(temp_order_group_data['폭'][selected_list[i][1][j][2][k]])
					temp_width = temp_order_group_data['폭'][selected_list[i][1][j][2][k]]
					temp_length = temp_order_group_data['길이(기준)'][selected_list[i][1][j][2][k]]
					temp_thickness = temp_order_group_data['두께'][selected_list[i][1][j][2][k]]
					temp_weight_list.append(round(utils.realWeight(temp_thickness,temp_width,temp_length,1,selected_list[i][1][j][1])))

					for m in range(len(order_list)):
						if order_list[m][0] == temp_order_group_data['제품코드'][selected_list[i][1][j][2][k]]:
					    		order_list[m][1] += round(utils.realWeight(temp_thickness,temp_width,temp_length,1,selected_list[i][1][j][1]))
					    		order_list[m][2].append(temp_material_group_data['제품코드'][selected_list[i][0]]+' / '+temp_material_group_data['ROLL'][selected_list[i][0]]+' / '+\
                                           					str(temp_material_group_data['포장중량'][selected_list[i][0]]))
				temp_order_num.append(' / ')    
				temp_width_sum.append(width_sum)
			    
			cal_meterial_weight = utils.calculateRealweight(temp_thickness,meterial_weight)
			temp_list.append(cal_meterial_weight)
			weight_list_sum = reduce(lambda x1,x2: x1+x2,temp_weight_list)
			temp_list.append(weight_list_sum)
			temp_list.append(cal_meterial_weight-weight_list_sum)
			temp_list.append(temp_material_group_data['실폭'][selected_list[i][0]])
			temp_list.append(temp_width_sum)    
			temp_list.append(temp_material_group_data['실폭'][selected_list[i][0]]-temp_width_sum)
			temp_list.append(temp_weight_list)
			temp_list.append(temp_length_sum)
			temp_list.append(temp_count_sum)
			temp_list.append(temp_order_num)
			combi_df_list.append(temp_list)
		combi_df = pd.DataFrame(columns =['원자재 index','원자재 제품코드','원자재 포장중량','가공무게','조합 무게합','남은 무게'\
				                  ,'원자재 실폭','주문 실폭합',"폭 차(mim 포함)",'조합 무게','조합 길이','조합 횟수','조합 제품코드'],data=combi_df_list)
		combi_df = combi_df.sort_values(['원자재 index'])

		for i in range(len(order_list)):
			order_list[i][2] = list(set(order_list[i][2]))

		order_code_list = []
		for i in range(len(order_list)):
		    order_code_list.append(order_list[i][0])

		order_code_list = list(set(order_code_list))
		order_code_list.sort()
		order_code_result_list =[]
		for i in range(len(order_code_list)):
			temp_list = [order_code_list[i],0,0,0,[],'','','']
			for j in range(len(order_list)):
				if temp_list[0] == order_list[j][0]:
					temp_list[1] += order_list[j][1]
					temp_list[4]= order_list[j][2]
			temp_list[1] = round(temp_list[1])
			for j in range(len(temp_order_group_data['제품코드'])):
				if temp_list[0] == order_list[j][0]:
					temp_list[2] = round(temp_order_group_data['생산량'][j]*1000)
			temp_list[3] = round(temp_list[2]-temp_list[1])
			temp_list[4] = list(set(temp_list[4]))

			order_code_result_list.append(temp_list)
		extra_sum =0
		total_sum =0.0
		need_sum =0
		result_df =  pd.DataFrame(columns =['제품코드','조합량','주문량','필요생산량(<0:추가생산량)','투입 원자재','','',''],\
				          data=order_code_result_list)
		
		for i in range(len(result_df)):
			if result_df['필요생산량(<0:추가생산량)'][i]<0:
				extra_sum+= result_df['필요생산량(<0:추가생산량)'][i]
			else:
				need_sum +=result_df['필요생산량(<0:추가생산량)'][i] 
			total_sum += (result_df['주문량'][i])
		    
		residual_sum = 0
		for i in range(len(combi_df)):
			residual_sum += float(combi_df["남은 무게"][i])
		    
		temp_list =['','','','','','','','']
		order_code_result_list.append(temp_list)
		temp_list =['','','','','','','','']
		order_code_result_list.append(temp_list)

		temp_list =["총 추가 생산량",-int(extra_sum),"미 생산량",int(need_sum),"주문량",total_sum,"총 낭비량",int(residual_sum)]
		
		##result score 계산
		result_score = 50-50*((need_sum/total_sum) + (extra_sum/(total_sum-need_sum)) + (residual_sum/(total_sum-need_sum))) + avg_score/2

		order_code_result_list.append(temp_list)
		result_df =  pd.DataFrame(columns =['제품코드','조합량','주문량','필요생산량(<0:추가생산량)','투입 원자재','','',''],\
				          data=order_code_result_list)

		self.result_list.append([result_score, combi_df, result_df])


	def start_combi(self,big_group_name):
		selected_list, temp_order_group_data, temp_material_group_data, avg_score = self.get_combination(big_group_name)
		self.get_result_data(selected_list, temp_order_group_data,temp_material_group_data,avg_score)
			

	def run_thread(self,big_group_name,num_of_thread):
		threads = []
		for i in range(num_of_thread):
			th = threading.Thread(target=self.start_combi, args=(big_group_name,))
			threads.append(th)

		for i in range(num_of_thread):
			threads[i].start()

		for i in range(num_of_thread):
			threads[i].join()
		 	

	def select_best_result(self):
		best_result = self.result_list[0]
		for i in range(1,len(self.result_list)):
			if best_result[0] < self.result_list[i][0]:
				best_result = self.result_list[i]
			print(self.result_list[i][0])

		return best_result

	def save_excel(self,big_group_name,best_result):
		print("best_result[0]",best_result[0])
		combi_df = best_result[1]
		result_df = best_result[2]
		
		now = datetime.now()
		time = str(now.year)+'_'+str(now.month)+'_'+str(now.day)+'_'+str(now.hour)+'_'+str(now.minute)+'_'
		file_name=time+big_group_name+"_result.xlsx"
		writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
		combi_df.to_excel(writer,sheet_name ='combi_result')
		result_df.to_excel(writer,sheet_name ='product_result')
		writer.close()
  
