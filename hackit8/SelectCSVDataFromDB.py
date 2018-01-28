from bson.json_util import dumps
from pymongo import MongoClient

def select_date_count_from_db(PID,licensetype,customer):
	try:
		url='mongodb://test:Lab123@ds137040.mlab.com:37040/hackit8'

		client=MongoClient(url)
		db=client.get_default_database()
		print("connected succesfully")

		jsonstr = "["

		Date = ""
		year = ""
		mnt = ""
		day = ""
		value = db.license_count.find( { "PRODUCTID" : PID,"ENTITLEMENT_NAME":licensetype,"CUSTOMER":customer},{"MAX_COUNT":1,"_id":0,"DATE":1} )
		Month = {"Jan":'01',"Feb":'02',"Mar":'03',"Apr":'04',"May":'05',"Jun":'06',"Jul":'07',"Aug":'08',"Sep":'09',"Oct":'10',"Nov":'11',"Dec":'12'}
		for i in value:
			strng={}
			pdate = str(i["DATE"])
			pdate = pdate.split('-')
			ldate = list(pdate)
			year = "20"+ldate[2]
			mnt = Month[ldate[1]] 
			day = ldate[0]
			Date = year+mnt+day
			pcount = str(i["MAX_COUNT"])
			strng["DATE"] = Date
			strng["MAX_COUNT"]=pcount
			jsonstr = jsonstr + dumps(strng) + ","
		jsonstr_list = list(jsonstr)
		jsonstr_list[-1] = ""
		jsonstr = "".join(jsonstr_list)
		jsonstr = jsonstr + "]"
		return jsonstr
	except Exception as e:
		print("Could Not Connect To MongoDb: " + str(e))

def main():
    print("Main works")
    print(select_date_count_from_db())
 
if __name__ == "__main__":
    main()