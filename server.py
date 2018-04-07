#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
web сервис проверки деталей по VIN

'''
import sqlite3
from flask import Flask, jsonify 
from flask import abort
from flask import make_response

db_filename = 'sqlite\\renault.sqlite'
def check_number_by_vin(number, vin):
    
    res = []
    conn = sqlite3.connect(db_filename)
    c = conn.cursor() 
    #выборка всех комплексных индексов с позициями по каталогу и номеру детали
    sql_str = "select [complexindex],[pos],[numcat] from items where [numcat] = (select [numcat] from vins where [vin] = '{}') and [number] = '{}'".format(vin, number)
    res = []
    try:
        res = list(c.execute(sql_str))#[0][0]
    except:
        res = []                  
    if len(res) == 0:
        return "no"    
    #идея - надо пройти по каждой паре [complexindex] и [pos] и подсчитать количество number
    #если хоть в одном случае будет больше одного, то отправляем в variant    
    for i in range(len(res)):
        complexindex = res[i][0]
        pos = res[i][1]
        numcat = res[i][2]
        #подсчёт номеров под одной позицией в одной таблице деталей (комплексном индексе) в каталоге
        sql_str = "select count([number]) from items where [numcat] = '{}' and [complexindex] = '{}' and [pos] = '{}'".format(numcat, complexindex, pos)
        number_count = list(c.execute(sql_str))[0][0]
        print("numcat={}, complexindex={}, pos={}, number_count={}".format(numcat, complexindex, pos, str(number_count)))
        if number_count > 1: 
            return "variant"
    return "yes"

app = Flask(__name__) 

#http://localhost:5000/CheckNumberByVIN/api/v1.0/VF6BG06A1BPC15063|5003101151|5000745512qq|0000767399
@app.route('/CheckNumberByVIN/api/v1.0/<string:vinnum>', methods=['GET']) 
def check_by_vin(vinnum):
    if vinnum and len(vinnum) >= 17:
        raw = vinnum.split("|")
        vin = raw[0]
        nums = []
        for i in range(1, len(raw)):
            num = raw[i]
            res = check_number_by_vin(num, vin)
            nums.append("{}={}".format(num, res))            

        return jsonify({'vin': vin, 'fits': nums})
    else:
        return jsonify({'error': 'VIN length less than 17 characters'})

@app.errorhandler(404) 
def not_found(error):     
    return make_response(jsonify({'error': 'Empty request'}), 404) 

if __name__ == '__main__':     
    app.run(debug=True)

