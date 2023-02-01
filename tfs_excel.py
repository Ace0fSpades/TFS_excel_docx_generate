from itertools import count
from typing import ItemsView
from tfs import TFSAPI
import xlsxwriter



pat = "icct64e7fzwbpe2fvbo52jq3nsj7c34rdqgp32h7j74ye7ox5jhq" # Ключ доступа

client = TFSAPI("https://tfs.content.ai/", project="HQ/ContentAI",pat=pat) # Соединение с тфс

custom_start = '01-01-2023' # Дата начала
custom_end = '31-01-2023' # Дата конца

# Запрос 
query = """SELECT [System.AssignedTo], [Tags]
FROM workitems
WHERE [System.State] = 'Done' AND [System.AssignedTo] <> ' '  AND [System.WorkItemType] = 'Task' AND ([Created Date] >= ' """ + custom_start + """ ' AND [Closed Date] <= ' """ + custom_end + """ ')
ORDER BY [System.AssignedTo]
"""

wiql = client.run_wiql(query)
workitems = wiql.workitems # Получаем объекты из запроса

members = [] # Лист прикрепленных к задаче людей
tags = [] # Лист тегов

for x in workitems: # Выборка данных
    if (x['AssignedTo']):
        members.append(x['AssignedTo'][:x['AssignedTo'].find(' <')]) 
    else:
        members.append(x['AssignedTo'])    
    tags.append(x['Tags'])
    

# ============================Табличка======================================================

list_array = [[None]]  # Двумерный лист для заполнения
dict_tags = {} # Словарь тегов
dict_names = {} # Словарь имен

for i in range(len(tags)): # Заполнение словаря тегов и первой строчки листа
    if tags[i] not in list_array[0]:
        dict_tags[tags[i]] = len(list_array[0])
        list_array[0].append(tags[i])

dict_tags['Default'] = len(list_array[0]) # Добавляем в словарь и лист значения Default для задач без тегов и Sum для проверки
list_array[0].append('Default')
dict_tags['Sum'] = len(list_array[0])
list_array[0].append('Sum')

for i in range(len(members)): # Заполнение словаря имен и первого столбца листа
    if members[i] not in dict_names.keys():
        dict_names[members[i]] = len(list_array)
        list_array.append([members[i]])
        list_array[-1].extend([0]*(len(list_array[0])-1))

for i in range(len(members)): # Подсчет задач, к которым прикреплен конкретный человек
    if (dict_names.get(members[i])):
        if (dict_tags.get(tags[i])):
            list_array[dict_names.get(members[i])][dict_tags.get(tags[i])] += 1
            list_array[dict_names.get(members[i])][dict_tags.get('Sum')] += 1
        else:
            list_array[dict_names.get(members[i])][dict_tags.get('Default')] += 1
            list_array[dict_names.get(members[i])][dict_tags.get('Sum')] += 1

for i in range(1, len(list_array)): # Перезапись в процентной форме (0 значения заполняются ' ')
    for j in range(1, len(list_array[0])):
        if (list_array[i][j] > 0):
            list_array[i][j] = str(round((list_array[i][j]/list_array[i][dict_tags.get('Sum')])*100, 2)) + '%'
        else:
            list_array[i][j] = ' '

workbook = xlsxwriter.Workbook('Time_Management.xlsx') # Создание excel файла
worksheet = workbook.add_worksheet() # Создание таблицы

for i in range(len(list_array)): # Заполнение таблицы с помощью двумерного листа
    for j in range(len(list_array[0])):
        worksheet.write(i,j,list_array[i][j])        

workbook.close() # Сохраняем файл

    




