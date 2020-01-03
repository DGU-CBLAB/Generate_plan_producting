import random

def cal_combi_residual(temp_list,cal_realweight):
    sum_weight = 0
    for i in range(len(temp_list)):
        sum_weight += temp_list[i][0]
    residual = cal_realweight - sum_weight
    if residual > 0:
        return residual
    else:
        return 1000

def reset_count(select_list, temp_list):
    for i in range(len(select_list)):
        for j in range(len(temp_list[2])):
            if check_index(select_list[i][2],temp_list[2][j]):
                for k in range(len(select_list[i][2])):
                    if select_list[i][2][k] == temp_list[2][j]:
                        if select_list[i][3][k] < temp_list[3][j]:
                            temp_list[0] = 10000000
                        temp_list[3][j] = select_list[i][3][k]

    temp_list[1] = min(temp_list[3])
    return temp_list

def check_material(material_company,material_temper,material_thickness,order_material,order_temper,order_thickness):
    material_list = order_material.split(',')
    material_check = False
    temper_check = False
    thickness_check = False
    if order_material == '무관':
        material_check = True
    else:
        for material in material_list:
            if material == material_company:
                material_check = True

    if material_temper == order_temper:
        temper_check = True

    if order_thickness <= material_thickness:
        thickness_check = True

    return (material_check and temper_check and thickness_check)

def cal_residual(real_weight,combi_weight):
    return real_weight-combi_weight

def check_index(index_list, index):
    for i in index_list:
        if i == index:
            return False

    return True

def check_list_index(index_list, index,count):
    if count>0:
        return True
    elif count ==0:
        return False

    for i in range(len(index_list)):
        for j in range(len(index_list[i])):
            if index_list[i][j] == index:
                return False
    return True

def find_possible_index(tried_material_list, index_list, list_size,index):
    while(1):
        if not check_index(tried_material_list,index) and not check_index(index_list,index) :
            index = random.randrange(0,list_size)#(index+1)%list_size
	    #index = random.randrange(0,list_size)%
        else:
            return index

def reset_index(list_size, index):
    if (list_size-1) == index:
        return list_size
    else:
        return index

def check_push(list,new_value,max_value):
    temp =0
    for value in list:
        temp += value
    temp+=new_value
    return (temp <= max_value)

def sum_list(list):
    temp =0
    for value in list:
        temp += value
    return temp

def check_residual_ratio(realweight,realweight_list,residual_list):
    for i in range(len(realweight_list)):
        if round(realweight/1000)==realweight_list[i]:
            if residual_list[i]/(residual_list[i]+realweight_list[i]) <= 0.2:
                return True
    return False

def get_residual(realweight,realweight_list,residual_list):
    for i in range(len(realweight_list)):
        if round(realweight/1000)==realweight_list[i]:
            return residual_list[i]
    return 0

def checkCombination(temp_list,temp_index_list,index,extra_width,max_width):

    temp_index = temp_index_list[index][:]
    temp_index.sort()

    ##기존 조합 있는지 확인
    for i in range(len(temp_index_list)-1):
        temp_sorted_index = temp_index_list[i][:]
        temp_sorted_index.sort()
        if temp_index == temp_sorted_index:
            return False

    if extra_width >=0 and extra_width<=100:
        return True
    else:
        return False

def combiWeight(thickness,width_list,length,weight,repeat):
    sum_width=0
    for width in width_list:
        sum_width+= width

    combi_weight = thickness*sum_width*length*weight*2.71*0.000001*repeat*2
    return (combi_weight)

def realWeight(thickness,width,length,weight,repeat):
    real_weight = thickness*width*length*weight*2.71*0.000001*repeat*2
    return (real_weight)

def calculateRepeat(thickness,width,length,goal_weight):
    repeat = 0
    corrent_weight =0
    goal_weight *=1000
    while(corrent_weight<=goal_weight):
        repeat+=1
        corrent_weight = realWeight(thickness,width,length,1,repeat)
    return repeat

def expectRealweight(realweight):
    return round(realweight/1000)

def expectSumRealweight(realweight_list):
    sum_realweight=0
    for realweight in realweight_list:
        sum_realweight += realweight
    return round(sum_realweight/1000)

def calculateRest(input_realweight,sum_realweight):
    return round(input_realweight-sum_realweight)

def index_count_dict(temp_list,version='normal'):
    temp_index_list = []
    temp_dict = {}
    for i in range(len(temp_list)):
        temp_index_list +=list(set(temp_list[i][2])) #사용되는 index list(중복 제거)

    #if temp_index_list != list(set(temp_index_list)): #다른 조합간에 겹치는 index 존재할 경우
    temp_index_list = list(set(temp_index_list)) #중복 제거 list
    for i in temp_index_list: #dict 초기화
        temp_dict[i] = 0

    for i in range(len(temp_list)):
        for j in range(len(temp_list[i][2])):
            if version == 'normal':
                temp_dict[temp_list[i][2][j]] += temp_list[i][1] #각 index가 얼마나 사용되지 입력
            elif version =='addition':
                temp_dict[temp_list[i][2][j]] -= temp_list[i][5][j] #각 index가 얼마나 사용되지 입력

    return temp_dict

def calculateRealweight(thickness,input_weight):
    expect_ratio=0.95
    if thickness == 5 or thickness == 5.8 or thickness == 8 or thickness == 300:

        expect_ratio = 0.88

    elif thickness == 5.9 or thickness == 6 or thickness == 6.3 or thickness == 6.35:

        expect_ratio = 0.89

    elif thickness == 5.9 or thickness == 6 or thickness == 6.3 or thickness == 6.35:

        expect_ratio = 0.89

    elif thickness == 6.45 or thickness ==6.5:

        expect_ratio = 0.91

    elif thickness == 7:

        expect_ratio = 0.92

    elif thickness == 9  or thickness ==12  or thickness == 15:

        expect_ratio = 0.924

    elif thickness == 16 or thickness ==18 or thickness ==20 or thickness ==21.5:

        expect_ratio = 0.918

    elif (thickness == 23 or thickness == 25 or thickness == 28 or thickness == 28.5 or thickness == 29 or thickness == 30 or thickness ==34
        or thickness == 35 or thickness == 38 or thickness == 40 or thickness == 50 or thickness == 60 or thickness == 70 or thickness == 75
        or thickness == 80 or thickness == 90 or thickness == 97 or thickness == 100 or thickness == 101 or thickness == 105 or thickness == 108
        or thickness == 110 or thickness == 113 or thickness == 115 or thickness == 118 or thickness == 120 or thickness == 123
        or thickness == 140 or thickness == 145 or thickness == 150 or thickness == 160):

        expect_ratio = 0.92

    elif thickness == 190 or thickness == 200 or thickness == 240:

        expect_ratio = 0.95

    elif (thickness == 350 or thickness == 370 or thickness == 400 or thickness == 450 or thickness == 500 or thickness == 550
        or thickness == 600):

        expect_ratio = 0.95

    return round(expect_ratio*input_weight)

def translate_alloy(alloy):
    if alloy == 'AB':
        return 'A1050'
    elif alloy == 'AC' or alloy == 'AC,HC':
        return 'A1235'
    elif alloy == 'AE':
        return 'A1100'
    elif alloy == 'HC':
        return 'A8079'
    elif alloy == 'CG':
        return 'A3003'
    elif alloy == 'HS':
        return 'A8021'
    elif alloy == 'CS':
        return 'F308'
    elif alloy == 'CJ':
        return 'F309'
    elif alloy == 'LW':
        return 'BRW04'
    elif alloy == 'AB':
        return 'A1050'
    elif alloy == 'AC':
        return 'A1235'
    elif alloy == 'AE':
        return 'A1100'
    elif alloy == 'HC':
        return 'A8079'
    elif alloy == 'CG':
        return 'A3003'
    elif alloy == 'HS':
        return 'A8021'
    elif alloy == 'CS':
        return 'F308'
    elif alloy == 'CJ':
        return 'F309'
    elif alloy == 'LW':
        return 'BRW04'

def get_mim_width(num,thickness,alloy,detail_code):

    if detail_code == '산업재':
        if num == 1:
            return 30
        elif num == 2:
            return 30
        elif num == 3:
            return 30
        else:
            return 60

    elif detail_code == '박박':
        if num == 1:
            return 35
        elif num == 2:
            return 40
        elif num == 3:
            return 50
        else:
            return 60
    elif detail_code == '후박':
        if num == 1:
            return 35
        elif num == 2:
            return 50
        elif num == 3:
            return 60
        else:
            return 70

    elif thickness <= 12 and alloy == 'CG':
        if num ==1:
            return 35
        elif num ==(2 or 3):
            return 40
        else:
            return 60

    elif thickness <=13.5  and (alloy == 'AC'or alloy == 'AE'):
        if num == 1:
            return 40
        elif num == 2:
            return 50
        elif num == 3:
            return 60
        else:
            return 70

    else:
        if num == 1:
            return 30
        elif num == 2:
            return 40
        elif num == 3:
            return 50
        elif num ==4:
            return 60
        else:
            return 70

def check_doubling(doubling_code):
    if doubling_code == 'G' or doubling_code == 'M': #G M
        return True
    else:
        return False
