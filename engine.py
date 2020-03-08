import utils
import pandas as pd
import random
from datetime import datetime
import math
from collections import Counter
from functools import reduce
import threading
from copy import deepcopy
import time

class Engine:
	def __init__(self,order_file_name="",material_file_name="",mim_file_name="",overlap="False"):
		self.data_location = ""
		self.order_file_name=order_file_name
		self.material_file_name=material_file_name
		self.mim_file_name=mim_file_name
		self.material_data = pd.DataFrame()
		self.order_data = pd.DataFrame()
		self.mim_data = pd.DataFrame()
		self.big_group_name_list = [];
		self.big_group_index_list=[]
		self.material_name_list=[]
		self.material_index_list=[]
		self.result_list = []
		self.compare_list = []
		self.best_result = []
		self.overlap = overlap
		self.alloy_pair_list = []
		self.weight_extra_width=0.3; self.weight_combi_count=0.1; self.weight_over_production=0.1; self.weight_residual_material=0.6;
		self.weight_need_combi=0.5; self.weight_over_production_ratio=0.1; self.weight_wasted_materail=0.4;

	def read_file(self):
		self.order_data = pd.read_excel(self.order_file_name)
		self.material_data = pd.read_excel(self.material_file_name)
		self.mim_data = pd.read_excel(self.mim_file_name)
		for i in range(len(self.material_file_name)):
			if self.material_file_name[len(self.material_file_name)-i-1] == "/":
				self.data_location = self.material_file_name[0:(len(self.material_file_name)-i)]
				break
		self.process_data()
		self.set_big_and_material_group_info()

    #재고기반 grouping
	def process_data(self):
		## data sorting
		self.material_data = self.material_data.sort_values(by=['ALLOY','TEMPER','실폭','포장중량','생산일자'],ascending=False).reset_index()
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
			goal_weight = self.order_data['생산량'][i]*(1-self.order_data['최소생산량'][i])
			repeat = utils.calculateRepeat(thickness,width,length,goal_weight)
			if utils.check_doubling(self.order_data['권취'][i]) and (repeat)%2 !=0 : ## 더블링인 경우 2의 배수로 저장
				repeat+=1
			self.order_data['횟수'][i] = repeat
			if self.order_data['우선순위'][i] == 0:
				self.order_data['우선순위'][i] = 5

		self.order_data['const_횟수'] = self.order_data['횟수']
		self.order_data['addition_횟수'] = 0
		self.order_data = self.order_data.sort_values(by=['ALLOY_1','권취','TEMPER','원자재_M','원자재_T','두께','길이(기준)','내경','코아','폭'],\
				                      ascending=False).reset_index(drop=True)



	def set_big_and_material_group_info(self,version=1):
		alloy_vesrion = 'ALLOY_1'
		if version ==2:
			alloy_vesrion = 'ALLOY_2'
		## set big group info
		for i in range(self.order_data.shape[0]):
			temp=str(self.order_data[alloy_vesrion][i])
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

	def new_get_current_big_group_info(self,current_big_group_name):
		##small_group 선택
		group_name =  current_big_group_name
		temp_order_group_data = pd.DataFrame()
		temp_material_group_data = pd.DataFrame()
		material_index = -1

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
		temp_order_group_data = temp_order_group_data.sort_values(by=['세부품목','권취','TEMPER','원자재_M','원자재_T','두께','길이(기준)','내경','코아','폭'],\
				                            ascending=False).reset_index(drop=True)
		material_m_list = list(set(list(temp_order_group_data['원자재_M'])))
		delete_index = -1
		for i in range(len(material_m_list)):
			if ',' in material_m_list[i]:
				temp = material_m_list[i].split(',')
				material_m_list[i] = temp[0]
				for j in range(1,len(temp)):
					material_m_list.append(temp[j])
		try:
			material_m_list.remove('무관')
		except:
			pass
		material_m_list = list(set(list(material_m_list)))
		m_group_list = []
		# m_group_list = [ [m, [middle_group_name,[small_group_name1, index1, index2, ... ],[small_group_name2, index1, index2, ... ]]] ]
		#				[ [ 0,  [j,  [k]	] ]
		if len(material_m_list) == 0:
			material_m_list.append('무관')

		for m in range(len(material_m_list)):
			temp_m_group_index = []
			temp_m_name =  material_m_list[m]
			temp_m_group = [ temp_m_name ]

			for i in range(temp_order_group_data.shape[0]):
				temp_order_m_list = ['무관']
				if temp_order_group_data['원자재_M'][i] != '무관':
					temp_order_m_list = (temp_order_group_data['원자재_M'][i]).split(',')

				for j in temp_order_m_list:
					if j == temp_m_name or j == '무관':
						temp_m_group_index.append(i)
						break

			##set middle group
			middle_group_name = []
			for i in temp_m_group_index:
				temp=str(temp_order_group_data['세부품목'][i])+'-'
				temp+=str(temp_order_group_data['권취'][i])+'-'
				temp+=str(temp_order_group_data['TEMPER'][i])+"-"
				temp+=str(temp_order_group_data['원자재_T'][i])+"-"
				temp+=str(temp_order_group_data['두께'][i])
				check = True
				for j in range(len(middle_group_name)):
					if(temp==middle_group_name[j]):
						check = False
						break
				if check:
					middle_group_name.append(temp)

			for i in range(len(middle_group_name)):
				temp_middle_group_name = middle_group_name[i]
				temp_m_group.append([temp_middle_group_name])

			small_group_name =[]
			small_group_index = []

			for i in temp_m_group_index:
				temp=str(temp_order_group_data['세부품목'][i])+"-"
				temp+=str(temp_order_group_data['권취'][i])+"-"
				temp+=str(temp_order_group_data['TEMPER'][i])+"-"
				temp+=str(temp_order_group_data['원자재_T'][i])+"-"
				temp+=str(temp_order_group_data['두께'][i])
				for j in range(1,len(temp_m_group)):
					if temp_m_group[j][0]==temp:
						temp+="-"+str(temp_order_group_data['내경'][i])+"-"
						temp+=str(temp_order_group_data['길이(기준)'][i])+"-"
						temp+=temp_order_group_data['코아'][i]
						check = True

						for k in range(1,len(temp_m_group[j])):
							if(temp==temp_m_group[j][k][0]):
								temp_m_group[j][k][1].append(i)
								check = False
								break
						if check:
							temp_m_group[j].append([temp,[i]])

			m_group_list.append(temp_m_group)

		return temp_order_group_data, temp_material_group_data , m_group_list



	def get_combination(self, current_big_group_name,over_producton_rate):
		temp_order_group_data, temp_material_group_data, mt_m_group_list = self.new_get_current_big_group_info(current_big_group_name)
		print(temp_order_group_data)

		temp_material_group_data.to_csv("temp_material_group_data",index=True,sep='\t')

		CONST_OUT_OF_COUNT_NUM = 100000
		over_producton_rate = over_producton_rate

		SUM_OF_SCOURE = 0
		SUM_OF_SCOURE_COUNT = 0

		#랜덤으로 값 추출
		#조합 가능한 폭 list
		selected_list = []
		selected_material=[]
		holding_material=[]

		total_addition_count = 0
		current_count = 0
		mt_m_group_random_index_list = list(range(len(mt_m_group_list)))
		random.shuffle(mt_m_group_random_index_list)

		print("@@@@@@@@@@@@@@@@@@@@@current_big_group_name: ", current_big_group_name)
		for ver in range(len(mt_m_group_list)):
			random_index = mt_m_group_random_index_list[ver]
			middle_group_info = []
			for i in range(1,len(mt_m_group_list[random_index])):
				middle_group_info.append(mt_m_group_list[random_index][i])


			middle_group_random_index_list = list(range(len(middle_group_info)))
			random.shuffle(middle_group_random_index_list)

			for r in range(len(middle_group_info)):
				random_middle_index = middle_group_random_index_list[r]
				print("진행률: ",r/len(middle_group_info))
				middle_group_total_count = 0
				middle_group_index_list = []
				for i in range(1,len(middle_group_info[random_middle_index])):
					for j in middle_group_info[random_middle_index][i][1]:
						if temp_order_group_data['횟수'][j]!= CONST_OUT_OF_COUNT_NUM: ##남은 횟수 확인
							middle_group_total_count += temp_order_group_data['횟수'][j]
							middle_group_index_list.append(j)

				middle_start_index = middle_group_info[random_middle_index][1][1][0]

				combi_try_count = -1
				standard_score = 100
				n = -1
				total_best_score = -CONST_OUT_OF_COUNT_NUM
				total_best_select_list = []
				total_best_material_index = -1
				total_best_material_realweight = 0
				total_best_special_list = []


				one_more = 0
				need_new_material = 0
				while middle_group_total_count > 0:
					combi_try_count +=1
					search_count = -1

					new_material = False

					## 원자재 검색
					possible = False

					while 1:
						possible = True
						n = (n+1)%len(temp_material_group_data)

						if not(self.overlap):
							for i in holding_material:
								if i == n:
									possible = False

							for i in selected_material:
								if i == n:
									possible = False

						if possible:
							## 원자재 정보 setting
							material_code = temp_material_group_data['제품코드'][n]
							material_company=material_code[len(material_code)-1]
							material_temper = temp_material_group_data['TEMPER'][n]
							material_thickness = temp_material_group_data['실두께'][n]
							material_alloy = utils.translate_alloy(temp_material_group_data['ALLOY'][n])
							material_width = temp_material_group_data['실폭'][n]
							material_weight = float(temp_material_group_data['포장중량'][n])/1000

							thickness = temp_order_group_data['두께'][middle_start_index]
							processed_weight= utils.calculateRealweight(thickness,material_weight)

							if current_big_group_name == 'A8021' and temp_order_group_data['원자재_M'][middle_start_index] == '무관':
								order_material = 'N'
							else:
								order_material = temp_order_group_data['원자재_M'][middle_start_index]

							possible = utils.check_material(material_company, material_temper, material_thickness, \
													order_material, temp_order_group_data['원자재_T'][middle_start_index], thickness)

							if possible:
								holding_material.append(n)
								break

						search_count +=1

						if search_count > len(temp_material_group_data):
							## 사용 가능한 원자재가 없을 경우 -> 새로운 조건을 넣어야함
							new_material = True
							possible = False
							break

					#새로운 원자재를 구매해야하는 경우
					if need_new_material >len(temp_material_group_data)*1.5:
						break;

					if new_material:
						need_new_material +=1

					else:   ##원자재 존재할 경우 -> 조합 시작
						combi_width_list=[]
						combi_index_list=[]
						combi_count_list=[]
						special_addition_count_list = []

						for i in range(1,len(middle_group_info[random_middle_index])):

							small_group_index_list = middle_group_info[random_middle_index][i][1]
							small_group_start_index = small_group_index_list[0]
							max_index_count = 0
							temp_width_list=[]; temp_index_list=[]; temp_count_list =[]; #special_addition_count_list =[];
								## 산업재, 박박, 후박, FIN 등
							detail_code = temp_order_group_data['세부품목'][small_group_start_index]
							temp_material_width = material_width

							temp_width_list, temp_index_list, temp_count_list,special_addition_count_list \
								= utils.width_combi(self.mim_data,small_group_index_list,temp_order_group_data,\
									temp_material_width,thickness,material_alloy,detail_code,CONST_OUT_OF_COUNT_NUM)

										#좋은 조합 모음 and 새로운 조합
							if len(temp_width_list)!=0:
								temp_width_list.append(temp_order_group_data['길이(기준)'][small_group_start_index])
								combi_width_list.append(temp_width_list)
								combi_index_list.append(temp_index_list)
								combi_count_list.append(temp_count_list)

						########조합 종목 선택
						#폭 조합 ->  길이 조합 -> middle group set 조합
						sorted_realweight_list = [] #무게, 횟수, index_list, count_list, combi_width_list, 가로 손실 길이 ,낭비량

						max_realweight = 0
						if len(combi_width_list)>0 :

							for i in range(len(combi_width_list)):
								#각 조합의 길이는 마지막에 있음
								temp_length = combi_width_list[i][len(combi_width_list[i])-1]

								for j in range(len(combi_width_list[i])-1):

									min_repeat_count = min(combi_count_list[i][j])
									temp_sum_width = utils.sum_list(combi_width_list[i][j])
									temp_realweight_list = []
									doubing = utils.check_doubling(temp_order_group_data['권취'][combi_index_list[i][0][0]])

									for k in range(min_repeat_count):
										if (doubing and (k+1)%2 ==0) or (not doubing): ##더블링 조건에 맞게 무게 계산
										    ## 낭비, 생산량 계산
											temp_residual = round(utils.realWeight(thickness,material_width-temp_sum_width,temp_length,1,k+1)/1000,2)
											temp_real_weight = round(utils.realWeight(thickness,temp_sum_width,temp_length,1,k+1)/1000,2)
											zero_list = []
											for l in range(len(combi_count_list[i][j])):
												zero_list.append(0)

											if temp_real_weight+temp_residual < material_weight:
										    	#무게, 횟수, index_list, count_list, combi_width_list, 추가 count_list ,가로 손실 길이 ,낭비량
												temp_realweight_list.append([temp_real_weight,k+1,combi_index_list[i][j],\
																			combi_count_list[i][j],combi_width_list[i][j],zero_list,\
												         					material_width-temp_sum_width,temp_residual])

									if len(temp_realweight_list)!=0:
										temp_realweight_list.sort(reverse=True)
										sorted_realweight_list.append(temp_realweight_list)

						## 폭조합 결과 없을 경우
						if len(sorted_realweight_list)==0:
						    standard_score -= 1
						    need_new_material +=1
						    combi_try_count +=1
						else:
							#elements 조합 시작 -> set 생성
						    ## 초기 잔여량은 원자재 사용 무게 / 무게 순으로 sort
							sorted_realweight_list.sort(reverse=True)
							best_score = -CONST_OUT_OF_COUNT_NUM
							max_count = 0
							min_weight = 100

							for i in range(len(sorted_realweight_list)):
								max_count += len(sorted_realweight_list[i])
								if sorted_realweight_list[i][len(sorted_realweight_list[i])-1][0] < min_weight:
									min_weight = sorted_realweight_list[i][len(sorted_realweight_list[i])-1][0]

							temp_best_score = -CONST_OUT_OF_COUNT_NUM
							try_total_count = int(len(sorted_realweight_list)*math.sqrt(len(sorted_realweight_list)))
							if try_total_count < 10:
								try_total_count *= (10-try_total_count)
							while try_total_count >0:
								try_total_count -=1
								temp_list = []
								combi_count = 0
								temp_total_extra = processed_weight
								temp_sum_redisual = 0
								temp_try_count = -1
								temp_combi_weight = 0
								temp_extra_width = 0

								## 길이 조합
								while combi_count < min(4,len(sorted_realweight_list)) \
								 		and temp_try_count<min(10,max_count) and min_weight < temp_total_extra:

									temp_try_count += 1
									i = random.randrange(0,len(sorted_realweight_list))
									j = random.randrange(0,len(sorted_realweight_list[i]))
								    ## overlap check: 이미 동일한 조합 존재할 경우 선택하지 않음
									check_overlap_index = False
									temp_select_index = deepcopy(sorted_realweight_list[i][j][2])
									temp_select_index.sort()
									for a in range(len(temp_list)):
										for b in range(len(temp_list[a])):
											temp_check_index_list = deepcopy(temp_list[a][2])
											temp_check_index_list.sort()
										if temp_check_index_list == temp_select_index:
											check_overlap_index = True
											break;

										#추가로 더 넣을 수 있는지 확인
									if temp_total_extra -(sorted_realweight_list[i][j][0]+sorted_realweight_list[i][j][-1]) > -processed_weight*0.1 \
										and (not check_overlap_index):
										temp_list.append(deepcopy(sorted_realweight_list[i][j]))
										temp_total_extra -= (sorted_realweight_list[i][j][0]+sorted_realweight_list[i][j][-1])
										temp_sum_redisual += sorted_realweight_list[i][j][-1]
										temp_combi_weight += sorted_realweight_list[i][j][0]
										temp_extra_width += sorted_realweight_list[i][j][-2]
										combi_count +=1

								temp_score = -CONST_OUT_OF_COUNT_NUM
								temp_addition_weight = 0

								## 추가 생산 조합
								if len(temp_list) >0 :
									not_additional_temp_list = deepcopy(temp_list)
									not_additional_sum_redisual = temp_sum_redisual+temp_total_extra

									pre_count = 0
									temp_addition_count = 1
									addition_residual = 0
									addition_weight = 0

									#무게, 횟수, index_list, count_list, combi_width_list, 추가 count_list, 가로 손실 길이 ,낭비량
									## 가장 빈도수가 낮은 조합 횟수 최대로 늘림
									min_index= -1
									min_count = CONST_OUT_OF_COUNT_NUM
									for i in range(len(temp_list)):
									    if min_count >= temp_list[i][1]:
									    	min_index = i; min_count = temp_list[i][1];

									## doubling체크
									doubing = utils.check_doubling(temp_order_group_data['권취'][temp_list[min_index][2][0]])
									temp_length = temp_order_group_data['길이(기준)'][temp_list[min_index][2][0]]
									temp_sum_width = utils.sum_list(temp_list[min_index][4])

									## 추가 생산
									while 1:
										if ((doubing and (temp_addition_count)%2 ==0) or (not doubing)): ##더블링 조건에 맞게 무게 계산
											addition_weight = round(utils.realWeight(thickness,temp_sum_width,temp_length,1,temp_addition_count)/1000,2)
											addition_residual = round(utils.realWeight(thickness,temp_list[min_index][-2],temp_length,1,temp_addition_count)/1000,2)

											if temp_total_extra - (addition_weight+addition_residual) <= 0:
												## 원자재 무게를 넘어갈 경우 그전 추가생산량으로 처리
												if temp_combi_weight+temp_sum_redisual+(addition_weight+addition_residual) >= material_weight:
													temp_addition_count = pre_count
													addition_residual = round(utils.realWeight(thickness,temp_list[min_index][-2],temp_length,1,pre_count)/1000,2)
													addition_weight = round(utils.realWeight(thickness,temp_sum_width,temp_length,1,pre_count)/1000,2)
												break;

											pre_count = temp_addition_count
										temp_addition_count+=1

									temp_list[min_index][1] += temp_addition_count
									temp_list[min_index][0] += addition_weight
									temp_list[min_index][-1] += addition_residual




									### ex) [0, 0, 0, 1] -> 나중에 그 횟수를 따로 처리
									for i in range(len(temp_list[min_index][3])):
										if temp_order_group_data['횟수'][temp_list[min_index][2][i]] != CONST_OUT_OF_COUNT_NUM:
											temp_list[min_index][5][i]= min(temp_list[min_index][3][i]-temp_list[min_index][1],0)
										else:
											temp_list[min_index][5][i]= -temp_list[min_index][1]

									temp_weight_sum = 0
									for i in range(len(temp_list)):
										temp_weight_sum += temp_list[i][0]#+temp_list[i][-1])

									### 점수 계산에 필요한 값들 update
									temp_total_residual =material_weight - temp_weight_sum#temp_sum_redisual+(temp_total_extra-addition_weight+addition_residual)
									temp_combi_weight += addition_weight

									## 각각의 추가 생산 비율의 합으로 점수 계산
									sum_each_addition_rate = 0

									## 중복되는 index count 계산
									temp_index_dict = utils.index_count_dict(temp_list,'normal')
									temp_addidion_dict = utils.index_count_dict(temp_list,'addition')

									possible_count = True
									over_extra = False
									#not_producted_order = False
									for i in temp_index_dict.keys():
										non_additional_index_count = temp_index_dict[i]
										current_count = temp_order_group_data['횟수'][i]
										const_count = temp_order_group_data['const_횟수'][i]
										used_count = const_count - current_count
										addition_count = temp_addidion_dict[i]
										expected_count = used_count+non_additional_index_count + addition_count
										## 추가 생산 비율 추가
										#sum_each_addition_rate += addition_count/const_count

										if expected_count/const_count > 1+temp_order_group_data['최대생산량'][i]:
											penalty = ((expected_count/const_count)-(1+temp_order_group_data['최대생산량'][i]))+1
											penalty = penalty*(temp_order_group_data['우선순위'][i]-1)-1
											sum_each_addition_rate += penalty

											possible_count = False

										elif current_count == const_count:
											sum_each_addition_rate *= 0.8

									## 추가 생산 가능한 경우 계산
									if not possible_count:
										non_addtional_temp_score = 1 - (self.weight_extra_width*(temp_extra_width/80)\
									                        +self.weight_combi_count*(combi_count-1)\
															+self.weight_residual_material*(not_additional_sum_redisual/processed_weight))

										additional_temp_score = 1 - (self.weight_extra_width*(temp_extra_width/80)\
										                        +self.weight_combi_count*(combi_count-1)\
																+self.weight_over_production*sum_each_addition_rate\
																+self.weight_residual_material*(temp_total_residual/processed_weight))

										if non_addtional_temp_score > additional_temp_score:
											temp_list = not_additional_temp_list
											temp_total_residual = not_additional_sum_redisual
											sum_each_addition_rate = 0


									temp_score = 1 -  (self.weight_extra_width*(temp_extra_width/80)\
															+self.weight_combi_count*(combi_count-1)\
															+self.weight_over_production*sum_each_addition_rate\
															+self.weight_residual_material*(temp_total_residual/processed_weight))
									temp_score *=100
									## best 조합 선택
									if total_best_score < temp_score:
										total_best_score = temp_score
										total_best_select_list = deepcopy(temp_list)
										total_best_material_index = n
										total_best_material_realweight = processed_weight
										total_best_special_list = special_addition_count_list


							#### 좋은 재료가 없을 경우
							if total_best_score == -CONST_OUT_OF_COUNT_NUM:
								need_new_material += 1
								combi_try_count +=1
								standard_score -= 5

							elif combi_try_count > len(temp_material_group_data) or standard_score<= total_best_score: #standard_score<=total_best_score or combi_try_count >= len(temp_material_group_data)*2 :

								need_new_material = -100
								print(total_best_score)

								## best list 입력
								select_list = (total_best_select_list)
								best_score = total_best_score
								n = total_best_material_index
								special_addition_count_list = total_best_special_list
								processed_weight = total_best_material_realweight
								material_width  = temp_material_group_data['실폭'][n]
								combi_try_count = 0
								standard_score = 100
								print(select_list)

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
												error = temp_order_group_data['횟수'][select_list[i][2][j]] - order_count
												if error < 0:
													order_count += error
													order_addition_count += error

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
									#special_addition_count_list = []


								#제거 목록 index 선택
								selected_material.append(n)
								selected_material.sort()
								temp_selected_list = []
								temp_selected_list.append(n)
								temp_selected_list.append(select_list)
								selected_list.append(temp_selected_list)

								#설정 초기화
								n = random.randrange(0,len(temp_material_group_data))
								SUM_OF_SCOURE += total_best_score
								SUM_OF_SCOURE_COUNT +=1
								total_best_score = -CONST_OUT_OF_COUNT_NUM
								total_best_select_list = []
								total_best_material_index = -1
								total_best_material_realweight = 0

							elif standard_score>total_best_score:
								if total_best_score>10:
									standard_score += math.log((110-standard_score)/(120-total_best_score))*(120/total_best_score)*(100/(len(temp_material_group_data)))
								else:
									standard_score += math.log((110-standard_score)/(120-total_best_score))*abs(total_best_score)*(100/(len(temp_material_group_data)))

							combi_try_count +=1

						try:
							holding_material.remove(n)
						except:
							pass

		#temp_order_group_data.to_csv("result",index=True,sep='\t')
		#temp_material_group_data.to_csv("material_result",index=True,sep='\t')

		#len(temp_material_group_data)/len(selected_list)는 얼만큼 원자재를 많이 사용했는지 나타냄
		rate_of_using_material=len(selected_list)/len(temp_material_group_data)
		avg_score = 0
		try:
			avg_score =  (SUM_OF_SCOURE/SUM_OF_SCOURE_COUNT)
			return selected_list, temp_order_group_data ,temp_material_group_data,avg_score, rate_of_using_material
		except:
			return False, False, False, False, False


	def new_get_result_data(self,selected_list, temp_order_group_data,temp_material_group_data,avg_score,rate_of_using_material):
		total_combi_weigth_sum = 0
		total_extra_weigth_sum = 0
		total_order_weigth_sum = 0
		total_residaul_weigth_sum = 0
		total_wasted_weight_sum = 0
		order_list = []
		for i in range(len(temp_order_group_data['제품코드'])):
		    order_list.append([temp_order_group_data['제품코드'][i],0,[]])

		# order info_list 생성
		order_info_list = []

		## 조합 dataframe, save excel file
		combi_df_list = []
		for i in range(len(selected_list)):

			temp_material_index = selected_list[i][0]
			material_weight = temp_material_group_data['포장중량'][temp_material_index]
			material_width = temp_material_group_data['실폭'][temp_material_index]
			material_strip_lot = temp_material_group_data['STRIP LOT'][temp_material_index]
			temp_material_info_list =["","","","",""]
			#[원자재 코드(0), 원자재 폭(1), STRIP LOT(2), ROLL(3), 투입량(4)]
			temp_combi_weigth_sum = 0

			temp_material_info_list[0] = i+1 #(temp_material_group_data['index'][temp_material_index])
			temp_material_info_list[1] = temp_material_group_data['제품코드'][temp_material_index]
			temp_material_info_list[2] = (material_width)
			temp_material_info_list[3] = (material_strip_lot)
			temp_material_info_list[4] = (material_weight)

			temp_combi_info_list = []
			for j in range(len(selected_list[i][1])):
				j_first_index = selected_list[i][1][j][2][0]
				temp_combi_info = ["","","","","","","","","","","","","","","",""]
				#[분리항(0), 폭조합 규격_1(1), 폭조합 규격_2(2), 폭조합 규격_3(3), 폭조합 규격_4(4),
									# 폭조합 중량_1(5), 폭조합 중량_2(6), 폭조합 중량_3(7), 폭조합 중량_4(8), 폭조합 중량 합께(9),
									# 폭합계(10), 폭 차이(11), 제품 길이(12), 분리 횟수(13), 수율(%)(14), 잔량(15)]

				temp_width_sum =0
				temp_weight_sum = 0
				temp_count = selected_list[i][1][j][1]
				temp_length = temp_order_group_data['길이(기준)'][j_first_index]
				temp_thickness = temp_order_group_data['두께'][j_first_index]


				for k in range(len((selected_list[i][1][j][2]))):
					temp_order_info = ["","","",""] #제품규격(0), 주문량(1), 조합량(2), 원자재(3)

					k_index = selected_list[i][1][j][2][k]
					temp_width = temp_order_group_data['폭'][k_index]
					temp_width_sum += temp_width
					temp_weight = round(utils.realWeight(temp_thickness,temp_width,temp_length,1,temp_count))
					temp_weight_sum += temp_weight
					temp_combi_info[1+k] = temp_order_group_data['제품코드'][k_index]
					temp_combi_info[5+k] = temp_weight

					temp_order_info[0] = temp_order_group_data['제품코드'][k_index]
					temp_order_info[1] = temp_order_group_data['생산량'][k_index]*1000
					temp_order_info[2] = temp_weight
					temp_order_info[3] = temp_material_group_data['제품코드'][temp_material_index]+'/'+str(temp_material_index)
					order_info_list.append(temp_order_info)

				temp_combi_weigth_sum += temp_weight_sum
				temp_combi_info[0] = str(j+1)+"_"+str(len(selected_list[i][1]))
				temp_combi_info[9] = temp_weight_sum
				temp_combi_info[10] = temp_width_sum
				temp_combi_info[11] = material_width-temp_width_sum
				temp_combi_info[12] = temp_length
				temp_combi_info[13] = temp_count
				if j == len(selected_list[i][1])-1:
					temp_combi_info[14] = temp_combi_weigth_sum/material_weight
					temp_combi_info[15] = material_weight-temp_combi_weigth_sum
				temp_combi_info_list.append(temp_combi_info)

				total_combi_weigth_sum += temp_combi_weigth_sum
				#if temp_combi_weigth_sum/material_weight > 0.8:
				total_wasted_weight_sum += material_weight-temp_combi_weigth_sum
				#else:
				#	total_residaul_weigth_sum += material_weight-temp_combi_weigth_sum

			for j in range(len(temp_combi_info_list)):
				temp_list = []
				if j == 0:
					for k in range(len(temp_material_info_list)):
						temp_list.append(temp_material_info_list[k])
				else:
					for k in range(len(temp_material_info_list)):
						temp_list.append("")
				for k in range(len(temp_combi_info_list[j])):
					temp_list.append(temp_combi_info_list[j][k])

				combi_df_list.append(temp_list)

		combi_df = pd.DataFrame(columns =['NO.','원자재 코드', 'STRIP LOT','ROLL','투입량', '분리항','폭조합 규격_1','폭조합 규격_2',\
										'폭조합 규격_3', '폭조합 규격_4','폭조합 중량_1', '폭조합 중량_2', '폭조합 중량_3', '폭조합 중량_4',\
										'폭조합 중량 합께','폭합계', '폭 차이', '제품 길이', '분리 횟수', '수율', '잔량'],data=combi_df_list)
		order_df_list = []
		order_index_list = []
		material_check_list = []  ## 원자재 check list 생성
		for i in range(len(temp_order_group_data)):
			total_order_weigth_sum += temp_order_group_data['생산량'][i]*1000
			order_index_list.append(temp_order_group_data['제품코드'][i])

		#order_index_list = list(set(order_index_list))

		for i in range(len(order_index_list)):
			temp_order_info = ["",0,0,0,"","","","","","","","","","","","","",""]
			##제품규격(0)	주문량(1)	조합량(2)	부족량(3)	원자재_1(4)	코일수_1(5)	원자재_2(6)
			#코일수_2(7)	원자재_3(8)	코일수_3(9) 원자재_4(10)	코일수_4(11)	원자재_5(12)	코일수_5(13)
			#발주 원자재_1(14)	발주 코일수_1(15)	발주 원자재_2(16)	발주 코일수_2(17)
			temp_order_info[0] = order_index_list[i]
			temp_order_info[1] = temp_order_group_data['생산량'][i]*1000#order_info_list[j][1]
			for j in range(len(order_info_list)):
				if order_info_list[j][0] == temp_order_info[0]:
					temp_order_info[2] += order_info_list[j][2]
					k = 4
					not_include_check = True
					while k<14: ## 중보되는 원자재 있는지 확인
						if temp_order_info[k] == order_info_list[j][3]:
							not_include_check = False
							break
						k += 2

					if not_include_check:
						k = 4
						while k<14:
							if temp_order_info[k] =="":
								temp_order_info[k] = order_info_list[j][3]
								not_check = True
								for n in range(len(material_check_list)):
									if material_check_list[n] == order_info_list[j][3]:
										not_check = False
										break
								if not_check :
									material_check_list.append(order_info_list[j][3])
									temp_order_info[k+1] = 1
								else:
									temp_order_info[k+1] = '포함'
								break

							k += 2

			order_df_list.append(temp_order_info)

		for i in range(len(order_df_list)):
			order_df_list[i][3] = order_df_list[i][1] - order_df_list[i][2]
			if order_df_list[i][3]<0:
				total_extra_weigth_sum -= order_df_list[i][3]
				total_combi_weigth_sum += order_df_list[i][3]

		order_df = pd.DataFrame(columns =['제품규격','주문량',	'조합량','부족량','원자재_1','코일수_1','원자재_2',\
		'코일수_2','원자재_3','코일수_3','원자재_4','코일수_4','원자재_5','코일수_5',\
		'발주 원자재_1','발주 코일수_1','발주 원자재_2','발주 코일수_2'],data=order_df_list)

		total_need_weight_sum = total_order_weigth_sum - total_combi_weigth_sum
		ratio_of_extra_per_need = total_extra_weigth_sum/total_combi_weigth_sum


		result_score = 50-50*(self.weight_need_combi*(total_need_weight_sum/total_order_weigth_sum) + self.weight_over_production_ratio*ratio_of_extra_per_need \
						+ self.weight_wasted_materail*(total_wasted_weight_sum/total_combi_weigth_sum) ) \
						+ 0.5*(avg_score+(1-len(selected_list)/len(temp_material_group_data))*(total_combi_weigth_sum/total_order_weigth_sum))
						# + 20*(total_residaul_weigth_sum/total_combi_weigth_sum) )
		print("result_score",result_score)

		self.result_list.append([result_score, combi_df, order_df])

	def start_combi(self,big_group_name,over_producton_rate):
		selected_list, temp_order_group_data, temp_material_group_data, avg_score, rate_of_using_material\
		 					= self.get_combination(big_group_name,over_producton_rate)
		#self.get_result_data(selected_list, temp_order_group_data,temp_material_group_data,avg_score, rate_of_using_material)
		if selected_list != False:
			self.new_get_result_data(selected_list, temp_order_group_data,temp_material_group_data,avg_score, rate_of_using_material)

	def run_thread(self,big_group_name="",num_of_thread=1,over_producton_rate=0.3):
		threads = []
		for i in range(num_of_thread):
			th = threading.Thread(target=self.start_combi, args=(big_group_name,over_producton_rate))
			threads.append(th)

		for i in range(num_of_thread):
			threads[i].start()

		for i in range(num_of_thread):
			threads[i].join()


	def select_best_result(self):
		try:
			best_result = self.result_list[0]
			for i in range(1,len(self.result_list)):
				if best_result[0] < self.result_list[i][0]:
					best_result = self.result_list[i]

			return best_result
		except:
			print("There is no result")

	def save_excel(self,big_group_name,best_result,title=""):
		try:
			print("best_result[0]",best_result[0])
			combi_df = best_result[1]
			result_df = best_result[2]

			now = datetime.now()
			time = str(now.year)+'_'+str(now.month)+'_'+str(now.day)+'_'+str(now.hour)+'_'+str(now.minute)+'_'
			file_name=title+time+big_group_name+"_result.xlsx"
			writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
			combi_df.to_excel(writer,index=False,sheet_name ='combi_result')
			result_df.to_excel(writer,index=False,sheet_name ='product_result')
			writer.close()
		except:
			pass
