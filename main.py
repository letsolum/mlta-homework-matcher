from PyPDF2 import PdfReader
from urllib import request
import pandas as pd
import os,  sys, csv


def get_raw():
    lis = os.listdir('.')
    curr = []
    for file in lis:
        if file.find('pdf') == -1:
            continue
        curr.append(file)
    if len(curr) == 0:
        print("There isn't any .pdf files :( Copy it to current directory!")
        sys.exit()
    print('Choose the name of file with HW from variants:')
    for i in range(len(curr)):
        print(i + 1, '. ', curr[i], sep = '')
    num = int(input())
    raw_pdf = PdfReader(curr[num - 1])
    return raw_pdf

def get_name():
    name = input("Input your last and first name (Пупкин Денис): ")
    while len(pdf_finder(name, all_pages)) == 0:
        name = input("Error!\nInput your last and first name (Пупкин Денис): ")
    return name

def pdf_finder(some_text, pages):
    curr_pos = []
    for i in range(len(pages)):
        page = pages[i].extract_text()
        if page.find(some_text) == -1:
            continue
        curr_pos.append(i)
    return curr_pos


def extract_name(page):
    temp = 'алгоритмов, '
    text = page.extract_text()
    if text.find('МФТИ, ФПМИ') != 0:
        return 'b3bra'
    ind = text.find(temp)
    ind += len(temp) + len('01.01.2000, ')
    ans = ''
    while text[ind] != ',':
        ans += text[ind]
        ind += 1
    return ans


def start_of_new_task(text, ind):
    i = ind
    if (text[i:i + 2] != '.\n' and text[i:i + 2] != '?\n') or i + 2 == len(text):
        return 0
    i += 2
    l = 0
    if text[i] == 'Д':
        i += 1
    while text[i:i + l + 1].isdigit():
        l += 1
    if l == 0 or text[i + l] != '.':
        return 0
    return int(text[i:i + l])

def get_tasks(pos, all_pages):
    main_page = all_pages[pos]
    main_text = main_page.extract_text()
    while pos + 1 < len(all_pages) and extract_name(all_pages[pos + 1]) == 'b3bra':
        main_text += '\n'
        main_text += all_pages[pos + 1].extract_text()
        pos += 1
    prv_txt = main_text
    splt = main_text.split('\n')
    main_text = ''
    for e in splt:
        if e.find('принос') + e.find('балл') != -2:
            continue
        main_text += e + '\n'
    ind = main_text.find('устно')
    tasks = []
    while ind + 4 < len(main_text):
        if start_of_new_task(main_text, ind) != 0:
            ind += 2
            tasks.append('')
            while ind < len(main_text) and start_of_new_task(main_text, ind) == 0:
                tasks[-1] += main_text[ind]
                ind += 1
        else:
            ind += 1
    return tasks

def get_curr_table(name):
    url = "https://docs.google.com/spreadsheets/d/1A1GgBHQIStjRAK3wNlVc60Vneih0488woI5tPvkfFwk/export?format=xlsx&"
    response = request.urlretrieve(url, name + ".xlsx")

def get_sheet(name):
    name += '.xlsx'
    workbook = pd.read_excel(name, 'Sheet1', engine = 'openpyxl')
    workbook.to_csv (r'fuck.csv', index = None, header=True)
    f = open('fuck.csv', 'r')
    new_book_csv = csv.reader(f)
    workbook = list(new_book_csv)
    f.close()
    return workbook

def transform_sheet(sheet, trigger):
    ans = dict()
    ind = -1
    for i in range(len(sheet[0])):
        e = sheet[0][i]
        if e.find(trigger) != -1 and e[0] != 'к':
            ind = i
            break
    if ind == -1:
        return False
    while sheet[1][ind].isdigit() == False and sheet[1][ind][0] != 'Д':
        ind += 1
    #print(sheet[1][ind], ind)
    ind_end = ind
    while sheet[1][ind_end] != 'сумма':
        ind_end += 1
    for i in range(2, len(sheet)):
        if len(sheet[i][1]) == 0 or sheet[i][1][0] == 'с':
            continue
        name = sheet[i][1].split(' ')[0] +  ' ' + sheet[i][1].split(' ')[1]
        ans[name] = set()
        for j in range(ind, ind_end):
            if sheet[i][j] == '1':
                ans[name].add(sheet[1][j])
    return ans
    
def extract_date(page):
    text = page.extract_text()
    ans = text[text.find('алгоритмов, ') + len('алгоритмов, '):text.find('алгоритмов, ') + len('алгоритмов, ') + 10]
    return ans    

def find_matchings():
    eq_for_tasks = dict()
    eq_for_people = dict()
    fast_tasks = set(tasks)
    for i in range(1, len(all_pages)):
        curr_n = extract_name(all_pages[i])
        if curr_n == 'b3bra' or curr_n == name:
            continue
        curr_t = get_tasks(i, all_pages)
        for t1 in curr_t:
            num_task = t1[:t1.find('.')]
            if t1 in fast_tasks:
                if num_task not in eq_for_tasks:
                    eq_for_tasks[num_task] = [curr_n]
                else:
                    eq_for_tasks[num_task].append(curr_n)
                if curr_n not in eq_for_people:
                    eq_for_people[curr_n] = [num_task]
                else:
                    eq_for_people[curr_n].append(num_task)
    return [eq_for_tasks, eq_for_people]

def print_out(eq_for_people, eq_for_tasks, are_done):
    print('There are all task-base matches:')
    for t in eq_for_tasks:
        print('Task ', t, ':', sep = '')
        for e in eq_for_tasks[t]:
            print(e, ' ' * (10 - len(e)) + '\u274C' * int(t not in are_done[e])  + '\u2705' * int(t in are_done[e]))
        print('*' * 34)

    print('/' * 34)
    print('/' * 34)
    print('/' * 34)
    print('There are all people-base matches:')
    for t in eq_for_people:
        print(t, ':', sep = '')
        for e in eq_for_people[t]:
            print(e, ' ' * (5 - len(str(e))) + '\u274C' * int(e not in are_done[t])  + '\u2705' * int(e in are_done[t]))
        print('*' * 34)

#######################################################################################################
#######################################################################################################
#######################################################################################################

all_pages = get_raw().pages
name = get_name()

pos = pdf_finder(name, all_pages)[0]
tasks = get_tasks(pos, all_pages)

name_of_table = 'table_with_marks'
get_curr_table(name_of_table)

sheet = get_sheet(name_of_table)
date = input("Input the name of HW how is it written in the GDocs (домашка 22.11.2022): ") #extract_date(all_pages[pos])
are_done = transform_sheet(sheet, date)
if type(are_done) == bool:
    are_done = transform_sheet(sheet, date[:5])

ans = find_matchings()
eq_for_tasks, eq_for_people = ans[0], ans[1] 

print_out(eq_for_people, eq_for_tasks, are_done)

os.remove(name_of_table + '.xlsx')
os.remove('fuck.csv')


    
