from django.shortcuts import render, render_to_response
from django.http import HttpResponse
import  os
import sys
import random
from datetime import datetime
from bson.json_util import dumps, loads
from pymongo import MongoClient
import pandas as pd
import numpy as np
import json
from . import LicensingDataAnalyticsStructured

client=MongoClient('mongodb://test:Lab123@ds137040.mlab.com:37040/hackit8')
db=client.get_default_database()
print ("connected succesfully")

def index(request):
	print ("Starting App")
	data = {}
	data.update(get_products())
	data.update(get_entitlements())
	data.update(get_customers())
	return render(request, 'hackit8/index.html', data)

def get_products():
	ProductsId = []
	value1 = db.License_Count.find({ }, {"PRODUCT":1,"_id":0} )
	for val in value1:
		ProductsId.append(str(val["PRODUCT"]))
	products = {}
	products['products'] = list(set(ProductsId))
	return products

def get_entitlements():
	EntitlementsId = []
	value1 = db.License_Count.find({ }, {"ENTITLEMENT_NAME":1,"_id":0} )
	for val in value1:
		EntitlementsId.append(str(val["ENTITLEMENT_NAME"]))
	entitlements = {}
	entitlements['entitlements'] = list(set(EntitlementsId))
	return entitlements

def get_customers():
	CustomerId = []
	value1 = db.License_Count.find({ }, {"CUSTOMER":1,"_id":0} )
	for val in value1:
		CustomerId.append(str(val["CUSTOMER"]))
	customers = {}
	customers['customers'] = list(set(CustomerId))
	return (customers)

def _get_products(request):
	print("getting products")
	product_list = []
	customer = request.POST['customer']
	print("Req_get_products" + str(customer))
	products = db.License_Count.find({"CUSTOMER": customer}, {"PRODUCT":1,"_id":0} )
	for product in products:
		product_list.append(str(product["PRODUCT"]))
	result ={}
	result['products'] = list(set(product_list))
	print (result)
	return HttpResponse(json.dumps(result))


def _get_entitlements(request):
	print("getting entilements")
	entitlements_list = []
	customer = request.POST['customer']
	product = request.POST['product']
	print("Req_get_products" + str(customer) + " " + str(product))
	entitlements = db.License_Count.find({"CUSTOMER": customer, "PRODUCT": product}, {"ENTITLEMENT_NAME":1,"_id":0} )
	for entitlement in entitlements:
		entitlements_list.append(str(entitlement["ENTITLEMENT_NAME"]))
	result ={}
	result['entitlements'] = list(set(entitlements_list))
	print (result)
	return HttpResponse(json.dumps(result))

def _get_alldata(request):
	print("getting all data")
	main_date_dict = {}
	main_maxcount_dict = {}
	final_dict = {}
	date_dict = {}
	maxcount_dict = {}
	jsonstr = "["
	Date = ""
	year = ""
	mnt = ""
	day = ""
	Month = {"Jan":'01',"Feb":'02',"Mar":'03',"Apr":'04',"May":'05',"Jun":'06',"Jul":'07',"Aug":'08',"Sep":'09',"Oct":'10',"Nov":'11',"Dec":'12'}
	date_list = []
	maccount_list = []
	customer = request.POST['customer']
	product = request.POST['product']
	entitlement = request.POST['entitlement']
	print ("REq:" + str(customer) + " " +str(product)+ " " +str(entitlement))
	data = db.License_Count.find({"CUSTOMER": customer, "PRODUCT": product,"ENTITLEMENT_NAME": entitlement}, {"DATE":1,"MAX_COUNT":1,"_id":0})
	counter = 0;
	for i in data:
		print(i)
		maxcount_dict[str(counter)] = str(i["MAX_COUNT"])
		date_dict[str(counter)] = str(i["DATE"])
		strng={}
		pdate = str(i["DATE"])
		pdate = pdate.split('-')
		ldate = list(pdate)
		year = "20"+ldate[2]
		mnt = Month[ldate[1]] 
		day = ldate[0]
		Date = year+mnt+day
		pcount = str(i["MAX_COUNT"])
		strng["date"] = Date
		strng["max_count"]=pcount
		jsonstr = jsonstr + dumps(strng) + ","
		counter = counter + 1
	print ("count is " + str(counter))
	main_date_dict["DATE"] = date_dict
	main_maxcount_dict["MAX_COUNT"] = maxcount_dict
	final_dict.update(main_maxcount_dict)
	final_dict.update(main_date_dict)

	jsonstr_list = list(jsonstr)
	jsonstr_list[-1] = ""
	jsonstr = "".join(jsonstr_list)
	jsonstr = jsonstr + "]"

	data = json.loads(jsonstr)
	dt = pd.DataFrame(data)
	dt['DATE_TIME'] = pd.to_datetime(dt['date'],format='%Y%m%d')
	dt['MAX_COUNT'] = pd.to_numeric(dt['max_count'], errors='coerce')
	dt.sort_values(['DATE_TIME'], ascending=[True], inplace=True)
	date_list = []
	count_list = []
	for dateValue in dt['DATE_TIME'].tolist():
		date_list.append((str(np.asarray(dateValue))[0:10]).replace('-',''))

	for countValue in dt['MAX_COUNT'].tolist():
		count_list.append((str(np.asarray(countValue))))

	Date_Count_dict = {}
	Date_Count_list = []
	cnt = 0
	for val in date_list:
		Date_Count_dict = {}
		Date_Count_dict["date"]=date_list[cnt]
		Date_Count_dict["max_count"]=count_list[cnt]
		cnt =cnt + 1
		Date_Count_list.append(Date_Count_dict)

	print("Plot Dictionary")
	print(final_dict)
	x_y_coord = LicensingDataAnalyticsStructured.main(jsonstr,entitlement)
	xycord1 = x_y_coord["predict"]
	xycord2 = x_y_coord["max_count"]
	st = json.dumps(Date_Count_list) + "|||" + json.dumps(xycord1) + "|||" + json.dumps(xycord2) 
	#return render_to_response('hackit8/index.html', jsonstr)
	return HttpResponse(st)

