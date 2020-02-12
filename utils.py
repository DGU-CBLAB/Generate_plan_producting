import random
from collections import Counter
from copy import deepcopy
import math

def width_combi(small_group_index_start,small_group_index_end,temp_order_group_data,material_width,thickness,material_alloy,detail_code,CONST_OUT_OF_COUNT_NUM):
    ## 횟수 확인, 남은 횟수에 따라 확률값 부여
    count_index = [] #<- (확률,index)
    max_index_count = 0
    sum_count = 0
    for j in range(small_group_index_start,small_group_index_end):
        ## 횟수가 없는 오더도 포함
        if temp_order_group_data['횟수'][j]<CONST_OUT_OF_COUNT_NUM and temp_order_group_data['길이(기준)'][j] >0:
            prob = temp_order_group_data['횟수'][j]*(6-temp_order_group_data['우선순위'][j])+3
            count_index.append((prob,j))
            max_index_count += prob/(6-temp_order_group_data['우선순위'][j]) - 3
            sum_count += prob

        ## 횟수 모두 사용한 경우: 확률 1로 값 부여
        elif -temp_order_group_data['addition_횟수'][j]/temp_order_group_data['const_횟수'][j] < temp_order_group_data['최대생산량'][j]:
            count_index.append((1,j))
            max_index_count += 1
            sum_count += 1

    temp_width_list=[]
    temp_index_list=[]
    temp_count_list=[]
    temp_special_addition_count_list = []


    ## 횟수가 양수일 경우 -> elements(조합) 구함
    if sum_count >0:

        count_index.sort(reverse=True)
        index_count = -1
        index = -1

        min_width = temp_order_group_data['폭'][small_group_index_end-1]

        initial_mim_width, initial_max_mim_width = get_min_max_mim_width(1,thickness,material_alloy,detail_code)
#       max_index_count *=max_index_count

        while (index_count < max_index_count and material_width >= min_width+initial_mim_width):
            #'ALLOY','권취','TEMPER','두께','길이','내경','코아','폭' 일치 (small group)
            temp_width_list.append([])
            temp_index_list.append([])
            temp_count_list.append([])
            index_count += 1
            index += 1
            extra_width = material_width

            try_combi_count = 0
            check_only_addition = True
            num_of_combi = 0
            pre_mim_width = 0

            while(extra_width >= min_width and try_combi_count<min(10,sum_count)):
                ##횟수에 비례해서 선택
                rand = random.randrange(0,sum_count)
                for k in range(len(count_index)):
                    rand -= count_index[k][0]
                    if rand < 0:
                        j = count_index[k][1]
                        break

                mim_width, max_mim_width = get_min_max_mim_width(num_of_combi+1,thickness,material_alloy,detail_code)
                addition_mim_width = mim_width - pre_mim_width

                if check_push(temp_width_list[index],temp_order_group_data['폭'][j]+addition_mim_width,material_width):

                    if temp_order_group_data['횟수'][j] < CONST_OUT_OF_COUNT_NUM:
                        check_only_addition = False ## 추가 오더만으로 생산은 필요 없음

                    temp_width_list[index].append(temp_order_group_data['폭'][j]+addition_mim_width)
                    temp_count_list[index].append(temp_order_group_data['횟수'][j])
                    temp_index_list[index].append(j) #해당 index 저장
                    extra_width -= (temp_order_group_data['폭'][j]+addition_mim_width)
                    if detail_code != 'FIN' and num_of_combi>=2: ## 조합이 3개 초과할 수 없음, FIN이 아니라면
                        break;
                    num_of_combi +=1
                    pre_mim_width = mim_width

                try_combi_count+=1

            if len(temp_count_list[index]) > 0 and (not check_only_addition):
                ## 중복 index가 가능한 조합인지 확인
                count_index_list = Counter(temp_index_list[index])
                for k in range(len(temp_index_list[index])):
                    ## 중복되는 만큼 가능 횟수 나누어줌
                    if temp_count_list[index][k] != CONST_OUT_OF_COUNT_NUM:
                        temp_count_list[index][k] = temp_count_list[index][k] // count_index_list[temp_index_list[index][k]]

                    if temp_count_list[index][k] == 0: ## 초과 입력되는 경우
                        temp_count_list[index][k] =2 ##doubling을 고려하여 2번
                        find_index = False
                        for a in range(len(temp_special_addition_count_list)):
                            if temp_special_addition_count_list[a][1] == temp_index_list[index][k]: ##해당 index가 있을 경우
                                temp_special_addition_count_list[a][0] += 2 ##초과 횟수 추가
                                find_index = True
                                break;

                        if not find_index: ##해당 index가 없을 경우 새롭게 생성 [초과횟수(2),index]
                            temp_special_addition_count_list.append([2,temp_index_list[index][k]])

            mim_width, max_mim_width = get_min_max_mim_width(num_of_combi,thickness,material_alloy,detail_code)

                #본 조합이 좋은 조합이면 살리고 아니면 죽임
            if not(checkCombination(temp_width_list,temp_index_list,index,extra_width,material_width, max_mim_width-mim_width)) \
                    or check_only_addition:
                del temp_width_list[index]
                del temp_index_list[index]
                del temp_count_list[index]
                index -= 1

    return temp_width_list, temp_index_list, temp_count_list, temp_special_addition_count_list

def width_combi_with_simple_heuristic(small_group_index_start,small_group_index_end,temp_order_group_data,material_width,thickness,material_alloy,detail_code,CONST_OUT_OF_COUNT_NUM):
    ## 횟수 확인, 남은 횟수에 따라 확률값 부여
    count_index = [] #<- (확률,index)
    max_index_count = 0
    sum_count = 0
    total_real_count = 1
    for j in range(small_group_index_start,small_group_index_end):
        ## 횟수가 없는 오더도 포함
        if -temp_order_group_data['addition_횟수'][j]/temp_order_group_data['const_횟수'][j] < temp_order_group_data['최대생산량'][j] \
            and temp_order_group_data['길이(기준)'][j] >0:
            if temp_order_group_data['횟수'][j] < CONST_OUT_OF_COUNT_NUM:
                total_real_count += temp_order_group_data['횟수'][j]
            else:
                total_real_count += 1
            prob = 1
            count_index.append((prob,j))
            sum_count += prob


    temp_width_list=[]
    temp_index_list=[]
    temp_count_list=[]


    ## 횟수가 양수일 경우 -> elements(조합) 구함
    if total_real_count >0:

        count_index.sort(reverse=True)
        index_count = -1
        index = -1

        min_width = temp_order_group_data['폭'][small_group_index_end-1]

        initial_mim_width, initial_max_mim_width = get_min_max_mim_width(1,thickness,material_alloy,detail_code)
        max_index_count = total_real_count
        temp_special_addition_count_list = []
        while (index_count < max_index_count and material_width >= min_width+initial_mim_width):
            #'ALLOY','권취','TEMPER','두께','길이','내경','코아','폭' 일치 (small group)
            temp_width_list.append([])
            temp_index_list.append([])
            temp_count_list.append([])
            index_count += 1
            index += 1
            extra_width = material_width

            try_combi_count = 0
            check_only_addition = True
            num_of_combi = 0
            pre_mim_width = 0

            while(extra_width >= min_width and try_combi_count<min(10,sum_count)):
                ##횟수에 비례해서 선택
                rand = random.randrange(0,sum_count)
                for k in range(len(count_index)):
                    rand -= count_index[k][0]
                    if rand < 0:
                        j = count_index[k][1]
                        break

                mim_width, max_mim_width = get_min_max_mim_width(num_of_combi+1,thickness,material_alloy,detail_code)
                addition_mim_width = mim_width - pre_mim_width

                if check_push(temp_width_list[index],temp_order_group_data['폭'][j]+addition_mim_width,material_width):

                    if temp_order_group_data['횟수'][j] < CONST_OUT_OF_COUNT_NUM:
                        check_only_addition = False ## 추가 오더만으로 생산은 필요 없음

                    temp_width_list[index].append(temp_order_group_data['폭'][j]+addition_mim_width)
                    temp_count_list[index].append(temp_order_group_data['횟수'][j])
                    temp_index_list[index].append(j) #해당 index 저장
                    extra_width -= (temp_order_group_data['폭'][j]+addition_mim_width)
                    if detail_code != 'FIN' and num_of_combi>=2: ## 조합이 3개 초과할 수 없음, FIN이 아니라면
                        break;
                    num_of_combi +=1
                    pre_mim_width = mim_width

                try_combi_count+=1

            ## temp_special_addition_count_list -> 남은 생산량 있는데 입력 조합에 초과해서 들어갈 경우
            ## temp_special_addition_count_list[i] -> [초과횟수,index]


            if len(temp_count_list[index]) > 0 and (not check_only_addition):
                ## 중복 index가 가능한 조합인지 확인
                count_index_list = Counter(temp_index_list[index])
                for k in range(len(temp_index_list[index])):
                    ## 중복되는 만큼 가능 횟수 나누어줌
                    if temp_count_list[index][k] != CONST_OUT_OF_COUNT_NUM:
                        temp_count_list[index][k] = temp_count_list[index][k] // count_index_list[temp_index_list[index][k]]

                    if temp_count_list[index][k] == 0: ## 초과 입력되는 경우
                        temp_count_list[index][k] =2 ##doubling을 고려하여 2번
                        find_index = False
                        for a in range(len(temp_special_addition_count_list)):
                            if temp_special_addition_count_list[a][1] == temp_index_list[index][k]: ##해당 index가 있을 경우
                                temp_special_addition_count_list[a][0] += 2 ##초과 횟수 추가
                                find_index = True
                                break;

                        if not find_index: ##해당 index가 없을 경우 새롭게 생성 [초과횟수(2),index]
                            temp_special_addition_count_list.append([2,temp_index_list[index][k]])
            mim_width, max_mim_width = get_min_max_mim_width(num_of_combi,thickness,material_alloy,detail_code)

                #본 조합이 좋은 조합이면 살리고 아니면 죽임
            if not(checkCombination(temp_width_list,temp_index_list,index,extra_width,material_width, max_mim_width-mim_width)) \
                    or check_only_addition:
                del temp_width_list[index]
                del temp_index_list[index]
                del temp_count_list[index]
                index -= 1

    return temp_width_list, temp_index_list, temp_count_list, temp_special_addition_count_list

def sub_brute(CONST_OUT_OF_COUNT_NUM,temp_order_group_data,small_group_index_end,current_index,current_index_count,thickness,material_width,material_alloy,detail_code,\
                width_list,index_list,count_list,pre_mim_width,extra_width, all_width_list,all_index_list,all_count_list,all_special_list):

    temp_width_list=deepcopy(width_list); temp_index_list = deepcopy(index_list); temp_count_list= deepcopy(count_list);
    if current_index_count == temp_order_group_data['횟수'][current_index] and current_index == small_group_index_end-1:
        return 1;

    if -temp_order_group_data['addition_횟수'][current_index]/temp_order_group_data['const_횟수'][current_index] \
            < temp_order_group_data['최대생산량'][current_index] and temp_order_group_data['길이(기준)'][current_index] >0:
        num_of_combi = len(width_list)

        full_pattern = False

        mim_width, max_mim_width = get_min_max_mim_width(num_of_combi+(current_index_count),thickness,material_alloy,detail_code)
        addition_mim_width = mim_width - pre_mim_width

        if check_push(width_list,temp_order_group_data['폭'][current_index]*(current_index_count)+addition_mim_width,material_width):

            for i in range(current_index_count):

                if detail_code != 'FIN' and num_of_combi+(i+1) >= 4: ## 조합이 3개 초과할 수 없음, FIN이 아니라면
                    full_pattern = True
                    break

                mim_width, max_mim_width = get_min_max_mim_width(num_of_combi+(i+1),thickness,material_alloy,detail_code)
                addition_mim_width = mim_width - pre_mim_width

                if check_push(width_list,temp_order_group_data['폭'][current_index]*(i+1)+addition_mim_width,material_width) and\
                    not(full_pattern):
                    temp_width_list.append(temp_order_group_data['폭'][current_index]+addition_mim_width)
                    temp_count_list.append(temp_order_group_data['횟수'][current_index])
                    temp_index_list.append(current_index) #해당 index 저장
                    extra_width -= (temp_order_group_data['폭'][current_index]+addition_mim_width)
                    pre_mim_width = mim_width


    next_index = current_index+1

    if next_index < small_group_index_end and not(full_pattern):
        next_index_possible_count = temp_order_group_data['횟수'][next_index];
        for i in range(next_index_possible_count):
            brute(CONST_OUT_OF_COUNT_NUM,temp_order_group_data,small_group_index_end,next_index,i+1,thickness,material_width,\
                material_alloy,detail_code,width_list,index_list,count_list,pre_mim_width,extra_width,all_width_list,\
                all_index_list,all_count_list,all_special_list)

def brute(CONST_OUT_OF_COUNT_NUM,temp_order_group_data,small_group_index_end,current_index,current_index_count,thickness,material_width,material_alloy,detail_code,\
                width_list,index_list,count_list,pre_mim_width,extra_width, all_width_list,all_index_list,all_count_list,all_special_list):

    print(current_index,small_group_index_end,current_index_count)

    temp_width_list=deepcopy(width_list); temp_index_list = deepcopy(index_list); temp_count_list= deepcopy(count_list);

    full_pattern = False
    if -temp_order_group_data['addition_횟수'][current_index]/temp_order_group_data['const_횟수'][current_index] \
            < temp_order_group_data['최대생산량'][current_index] and temp_order_group_data['길이(기준)'][current_index] >0:
        num_of_combi = len(width_list)


        mim_width, max_mim_width = get_min_max_mim_width(num_of_combi+(current_index_count),thickness,material_alloy,detail_code)
        addition_mim_width = mim_width - pre_mim_width

        if check_push(width_list,temp_order_group_data['폭'][current_index]*(current_index_count)+addition_mim_width,material_width):


            for i in range(current_index_count):

                if detail_code != 'FIN' and num_of_combi+(i+1) >= 4: ## 조합이 3개 초과할 수 없음, FIN이 아니라면
                    full_pattern = True
                    break

                mim_width, max_mim_width = get_min_max_mim_width(num_of_combi+(i+1),thickness,material_alloy,detail_code)
                addition_mim_width = mim_width - pre_mim_width

                if check_push(width_list,temp_order_group_data['폭'][current_index]*(i+1)+addition_mim_width,material_width) and\
                    not(full_pattern):
                    temp_width_list.append(temp_order_group_data['폭'][current_index]+addition_mim_width)
                    temp_count_list.append(temp_order_group_data['횟수'][current_index])
                    temp_index_list.append(current_index) #해당 index 저장
                    extra_width -= (temp_order_group_data['폭'][current_index]+addition_mim_width)
                    pre_mim_width = mim_width


    next_index = -1
    if current_index != small_group_index_end-1:
        for i in range(current_index+1, small_group_index_end):
            if temp_order_group_data['횟수'][i] != CONST_OUT_OF_COUNT_NUM:
                next_index = i
                break;


        if next_index != -1 and not(full_pattern):
            next_index_possible_count = temp_order_group_data['횟수'][next_index];

            if -temp_order_group_data['addition_횟수'][next_index]/temp_order_group_data['const_횟수'][next_index] \
                    < temp_order_group_data['최대생산량'][next_index] and temp_order_group_data['길이(기준)'][next_index] >0:

                for i in range(next_index_possible_count+1):
                    #print(current_index, next_index, small_group_index_end, i)
                    brute(CONST_OUT_OF_COUNT_NUM,temp_order_group_data,small_group_index_end,next_index,i,thickness,material_width,\
                        material_alloy,detail_code,width_list,index_list,count_list,pre_mim_width,extra_width,all_width_list,\
                        all_index_list,all_count_list,all_special_list)

    else:
        temp_special_addition_count_list = []
        check_only_addition = True
#        print(temp_width_list)

        for i in range(len(temp_index_list)):
            temp_index = temp_index_list[i]
            if temp_order_group_data['폭'][temp_index] != CONST_OUT_OF_COUNT_NUM:
                check_only_addition = False
                break


        if len(temp_count_list) > 0 and (not check_only_addition):
            ## 중복 index가 가능한 조합인지 확인
            count_index_list = Counter(temp_index_list)
            for k in range(len(temp_index_list)):
                ## 중복되는 만큼 가능 횟수 나누어줌
                if temp_count_list[k] != CONST_OUT_OF_COUNT_NUM:
                    temp_count_list[k] = temp_count_list[k] // count_index_list[temp_index_list[k]]

                if temp_count_list[k] == 0: ## 초과 입력되는 경우
                    temp_count_list[k] =2 ##doubling을 고려하여 2번
                    find_index = False
                    for a in range(len(temp_special_addition_count_list)):
                        if temp_special_addition_count_list[a][1] == temp_index_list[k]: ##해당 index가 있을 경우
                            temp_special_addition_count_list[a][0] += 2 ##초과 횟수 추가
                            find_index = True


                    if not find_index: ##해당 index가 없을 경우 새롭게 생성 [초과횟수(2),index]
                        temp_special_addition_count_list.append([2,temp_index_list[k]])
            num_of_combi = len(temp_index_list)
            mim_width, max_mim_width = get_min_max_mim_width(num_of_combi,thickness,material_alloy,detail_code)


            if (checkCombination(temp_width_list,temp_index_list,-1,extra_width,material_width, max_mim_width-mim_width)):
                #print(temp_width_list)
                all_width_list.append(temp_width_list)
                all_index_list.append(temp_index_list)
                all_count_list.append(temp_count_list)
                for i in range(len(temp_special_addition_count_list)):
                    all_special_list.append(temp_special_addition_count_list[i])
        return 0

def width_combi_with_brute(small_group_index_start,small_group_index_end,temp_order_group_data,material_width,thickness,material_alloy,detail_code,CONST_OUT_OF_COUNT_NUM):
    print('start')
    temp_width_list=[]
    temp_index_list=[]
    temp_count_list=[]
    temp_special_addition_count_list = []
    first_index = -1
    firt_index_possible_count = 0
    for i in range(small_group_index_start,small_group_index_end):
        if temp_order_group_data['횟수'][i] != CONST_OUT_OF_COUNT_NUM:
            first_index = i
            firt_index_possible_count = temp_order_group_data['횟수'][i]
            break;

    pre_mim_width = 0
    extra_width = material_width

    width_list = []; index_list = []; count_list = [];
    if first_index != -1:
        for i in range(firt_index_possible_count+1):
            brute(CONST_OUT_OF_COUNT_NUM,temp_order_group_data,small_group_index_end,first_index,i,thickness,material_width,material_alloy,detail_code,\
                width_list,index_list,count_list,pre_mim_width, extra_width,temp_width_list,temp_index_list,temp_count_list,temp_special_addition_count_list)

    print('end')
    return temp_width_list, temp_index_list, temp_count_list, temp_special_addition_count_list

def width_brute(small_group_index_start,small_group_index_end,temp_order_group_data,material_width,thickness,material_alloy,detail_code,CONST_OUT_OF_COUNT_NUM):
    temp_width_list=[]
    temp_index_list=[]
    temp_count_list=[]
    temp_special_addition_count_list = []
    #firt_index_possible_count = temp_order_group_data['횟수'][small_group_index_start]
    pre_mim_width = 0
    extra_width = material_width
    for i in range(small_group_index_start,small_group_index_end):
        width_list = []; index_list = []; count_list = [];
        for j in range(firt_index_possible_count):
            brute(CONST_OUT_OF_COUNT_NUM,temp_order_group_data,small_group_index_end,small_group_index_start,i+1,thickness,material_width,material_alloy,detail_code,\
                width_list,index_list,count_list,pre_mim_width, extra_width,temp_width_list,temp_index_list,temp_count_list,temp_special_addition_count_list)

    #for i in
    #print(temp_width_list)
    print("end")
    return temp_width_list, temp_index_list, temp_count_list, temp_special_addition_count_list

def width_combi_with_better_greedy(small_group_index_start,small_group_index_end,temp_order_group_data,material_width,thickness,material_alloy,detail_code,CONST_OUT_OF_COUNT_NUM):
    temp_width_list=[]
    temp_index_list=[]
    temp_count_list=[]
    index =-1

    min_width = temp_order_group_data['폭'][small_group_index_end-1]

    initial_mim_width, initial_max_mim_width = get_min_max_mim_width(1,thickness,material_alloy,detail_code)
    for i in range(small_group_index_start,small_group_index_end):
        temp_width_list.append([])
        temp_index_list.append([])
        temp_count_list.append([])
        index += 1
        num_of_combi = 0
        pre_mim_width = 0
        check_only_addition = True
        full_pattern = False
        extra_width = material_width
        for j in range(i, small_group_index_end):
            if -temp_order_group_data['addition_횟수'][j]/temp_order_group_data['const_횟수'][j] < temp_order_group_data['최대생산량'][j]\
                and temp_order_group_data['길이(기준)'][j] >0:
                for k in range(min(4,temp_order_group_data['횟수'][j])):
                    mim_width, max_mim_width = get_min_max_mim_width(num_of_combi+1,thickness,material_alloy,detail_code)
                    addition_mim_width = mim_width - pre_mim_width

                    if check_push(temp_width_list[index],temp_order_group_data['폭'][j]+addition_mim_width,material_width):

                        if temp_order_group_data['횟수'][j] < CONST_OUT_OF_COUNT_NUM:
                            check_only_addition = False ## 추가 오더만으로 생산은 필요 없음

                        temp_width_list[index].append(temp_order_group_data['폭'][j]+addition_mim_width)
                        temp_count_list[index].append(temp_order_group_data['횟수'][j])
                        temp_index_list[index].append(j) #해당 index 저장
                        extra_width -= (temp_order_group_data['폭'][j]+addition_mim_width)
                        if detail_code != 'FIN' and num_of_combi>=2: ## 조합이 3개 초과할 수 없음, FIN이 아니라면
                            full_pattern = True
                            break;
                        num_of_combi +=1
                        pre_mim_width = mim_width

                if full_pattern:
                    break;

        ## temp_special_addition_count_list -> 남은 생산량 있는데 입력 조합에 초과해서 들어갈 경우
        ## temp_special_addition_count_list[i] -> [초과횟수,index]

        temp_special_addition_count_list = []

        if len(temp_count_list[index]) > 0 and (not check_only_addition):
            #print(temp_index_list[index])
                ## 중복 index가 가능한 조합인지 확인
            count_index_list = Counter(temp_index_list[index])
            for k in range(len(temp_index_list[index])):
                ## 중복되는 만큼 가능 횟수 나누어줌
                if temp_count_list[index][k] != CONST_OUT_OF_COUNT_NUM:
                    temp_count_list[index][k] = temp_count_list[index][k] // count_index_list[temp_index_list[index][k]]

                if temp_count_list[index][k] == 0: ## 초과 입력되는 경우
                    temp_count_list[index][k] =2 ##doubling을 고려하여 2번
                    find_index = False
                    for a in range(len(temp_special_addition_count_list)):
                        if temp_special_addition_count_list[a][1] == temp_index_list[index][k]: ##해당 index가 있을 경우
                            temp_special_addition_count_list[a][0] += 2 ##초과 횟수 추가
                            find_index = True
                            break;

                    if not find_index: ##해당 index가 없을 경우 새롭게 생성 [초과횟수(2),index]
                        temp_special_addition_count_list.append([2,temp_index_list[index][k]])
        mim_width, max_mim_width = get_min_max_mim_width(num_of_combi,thickness,material_alloy,detail_code)

                #본 조합이 좋은 조합이면 살리고 아니면 죽임
        if not(checkCombination(temp_width_list,temp_index_list,index,extra_width,material_width, max_mim_width-mim_width)) \
                or check_only_addition:
            del temp_width_list[index]
            del temp_index_list[index]
            del temp_count_list[index]
            index -= 1

    return temp_width_list, temp_index_list, temp_count_list, temp_special_addition_count_list

def width_combi_with_greedy(small_group_index_start,small_group_index_end,temp_order_group_data,material_width,thickness,material_alloy,detail_code,CONST_OUT_OF_COUNT_NUM):
    temp_width_list=[]
    temp_index_list=[]
    temp_count_list=[]
    index =-1

    min_width = temp_order_group_data['폭'][small_group_index_end-1]

    initial_mim_width, initial_max_mim_width = get_min_max_mim_width(1,thickness,material_alloy,detail_code)
    for i in range(small_group_index_start,small_group_index_end):
        temp_width_list.append([])
        temp_index_list.append([])
        temp_count_list.append([])
        index += 1
        num_of_combi = 0
        pre_mim_width = 0
        check_only_addition = True
        full_pattern = False
        extra_width = material_width

        for j in range(min(4,temp_order_group_data['횟수'][i])):
            if -temp_order_group_data['addition_횟수'][i]/temp_order_group_data['const_횟수'][i] < temp_order_group_data['최대생산량'][i]\
                and temp_order_group_data['길이(기준)'][i] >0:

                mim_width, max_mim_width = get_min_max_mim_width(num_of_combi+1,thickness,material_alloy,detail_code)
                addition_mim_width = mim_width - pre_mim_width

                if check_push(temp_width_list[index],temp_order_group_data['폭'][i]+addition_mim_width,material_width):

                    if temp_order_group_data['횟수'][i] < CONST_OUT_OF_COUNT_NUM:
                        check_only_addition = False ## 추가 오더만으로 생산은 필요 없음

                    temp_width_list[index].append(temp_order_group_data['폭'][i]+addition_mim_width)
                    temp_count_list[index].append(temp_order_group_data['횟수'][i])
                    temp_index_list[index].append(i) #해당 index 저장
                    extra_width -= (temp_order_group_data['폭'][i]+addition_mim_width)
                    if detail_code != 'FIN' and num_of_combi>=2: ## 조합이 3개 초과할 수 없음, FIN이 아니라면
                        full_pattern = True
                        break;
                    num_of_combi +=1
                    pre_mim_width = mim_width

            if full_pattern:
                break;

        temp_special_addition_count_list = []

        if len(temp_count_list[index]) > 0 and (not check_only_addition):
            #print(temp_index_list[index])
                ## 중복 index가 가능한 조합인지 확인
            count_index_list = Counter(temp_index_list[index])
            for k in range(len(temp_index_list[index])):
                ## 중복되는 만큼 가능 횟수 나누어줌
                if temp_count_list[index][k] != CONST_OUT_OF_COUNT_NUM:
                    temp_count_list[index][k] = temp_count_list[index][k] // count_index_list[temp_index_list[index][k]]

                if temp_count_list[index][k] == 0: ## 초과 입력되는 경우
                    temp_count_list[index][k] =2 ##doubling을 고려하여 2번
                    find_index = False
                    for a in range(len(temp_special_addition_count_list)):
                        if temp_special_addition_count_list[a][1] == temp_index_list[index][k]: ##해당 index가 있을 경우
                            temp_special_addition_count_list[a][0] += 2 ##초과 횟수 추가
                            find_index = True
                            break;

                    if not find_index: ##해당 index가 없을 경우 새롭게 생성 [초과횟수(2),index]
                        temp_special_addition_count_list.append([2,temp_index_list[index][k]])
        mim_width, max_mim_width = get_min_max_mim_width(num_of_combi,thickness,material_alloy,detail_code)

                #본 조합이 좋은 조합이면 살리고 아니면 죽임
        if not(checkCombination(temp_width_list,temp_index_list,index,extra_width,material_width, max_mim_width-mim_width)) \
                or check_only_addition:
            del temp_width_list[index]
            del temp_index_list[index]
            del temp_count_list[index]
            index -= 1

    return temp_width_list, temp_index_list, temp_count_list, temp_special_addition_count_list


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
    #print("material_check",material_check)
    #print("temper_check",temper_check)
    #print("thickness_check",thickness_check)
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
            index = random.randrange(0,list_size)
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

def checkCombination(temp_list,temp_index_list,index,extra_width,max_width, max_mim):
    if index != -1:
        temp_index = temp_index_list[index][:]
        temp_index.sort()

        ##기존 조합 있는지 확인
        for i in range(len(temp_index_list)-1):
            temp_sorted_index = temp_index_list[i][:]
            temp_sorted_index.sort()
            if temp_index == temp_sorted_index:
                return False

    if extra_width >=0 and extra_width<= max_mim:
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
    while (corrent_weight<=goal_weight):
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

    elif alloy == 'A1050':
        return 'AB'
    elif alloy == 'A1235':
        return 'AC'
    elif alloy == 'A1100':
        return 'AE'
    elif alloy == 'A8079':
        return 'HC'
    elif alloy == 'A3003':
        return 'CG'
    elif alloy == 'A8021':
        return 'HS'
    elif alloy == 'F30':
        return 'CS8'
    elif alloy == 'F309':
        return 'CJ'
    elif alloy == 'BRW04':
        return 'LW'

def get_min_max_mim_width(num,thickness,alloy,detail_code):
    #return min, max

    if detail_code == '산업재':
        return 25, 40

    elif detail_code == '박박':
        if num == 1:
            return 35, 60
        elif num == 2:
            return 40, 70
        elif num == 3:
            return 50, 70
        else:
            return 60, 80
    elif detail_code == '후박':
        if num == 1:
            return 35, 60
        elif num == 2:
            return 50, 70
        elif num == 3:
            return 60, 80
        else:
            return 70, 90
    elif detail_code == '일반':
        if num == 1:
            return 35, 60
        elif num == 2:
            return 50, 70
        elif num == 3:
            return 60, 80
        else:
            return 70, 90

    elif thickness <= 12 and alloy == 'CG':
        return 35, 55

    elif thickness <=13.5  and (alloy == 'AC'or alloy == 'AE'):
        if num == 1:
            return 35, 55
        elif num == 2:
            return 45, 65
        else:
            return 65, 85

    else:
        if num == 1:
            return 30, 50
        elif num == 2:
            return 40, 60
        else:
            return 50, 70


def check_doubling(doubling_code):
    if doubling_code == 'G' or doubling_code == 'M': #G M
        return True
    else:
        return False
