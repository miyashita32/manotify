#!/usr/local/bin/python3
#coding:utf-8

"""
2018/09/22
宮下
LineNotifyMA通知システム
"""

import requests
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime

short13 = [0]*12 #短期線
long75 = [0]*74 #長期線
rsi14 = [0]*13 #RSI

def gettime(): #時間を取得/引数:なし/返り値:True or False
	now = datetime.now()
	return now.hour*10000 + now.minute*100 + now.second

def getPrice(): #Investing.comから現在の価格を取得する/引数:無し/返り値:価格(list)
	url = "https://jp.investing.com/indices/japan-225-futures"
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
	r = requests.get(url, headers=headers)
	soup = BeautifulSoup(r.text, "lxml")

	return soup.select("#quotes_summary_current_data > div.left > div.inlineblock > div.top.bold.inlineblock > #last_last")

def send(message): #line notifyを使いLineにメッセージを送信/引数:メッセージ(str)/返り値:無し
	url = "https://notify-api.line.me/api/notify"
	token = 'JP0ik6Y5ZpGQxCqxD1vhHjnBYedf0g0cMTwVy8lVkfO'#ここにアクセストークンを入力します。
	headers = {"Authorization" : "Bearer "+ token}
	
	payload = {"message" : message}

	r = requests.post(url ,headers = headers ,params=payload)
	
def gettime(): #時間を取得/引数:なし/返り値:True or False
	now = datetime.now()
	return now.hour*10000 + now.minute*100 + now.second

def week(): #曜日が月~金かを判定/引数:なし/返り値:True or False
	now = datetime.now()
	#0: 月, 1: 火, 2: 水, 3: 木, 4: 金, 5: 土, 6: 日
	if now.weekday() < 5:
		return True
	else:
		return False

def zaraba(ntime): #ザラ場(8:45~15:10)かどうかを判定/引数:時間/返り値:True or False
	if 84500 < ntime < 151000:
		return True
	else:
		return False

def opend(ntime): #市場が空いている時間かどうかを判定/引数:時間/返り値:T or F
	if 84500 < ntime < 151000 or 163000 < ntime or ntime < 53000:
		return True
	else:
		return False
		
def stock(price): #25と75の先頭を消去し一番うしろに現価格を追加/引数:価格/返り値:無し
	global short13
	global long75
	global rsi14
	
	short13.append(price)
	short13.pop(0)

	long75.append(price)
	long75.pop(0)
	
	rsi14.append(price)
	rsi14.pop(0)
	
def average(nowPrice): #25と75の平均/引数:現価格/返り値:[13平均,75平均](List)
	sum13 = 0
	sum75 = 0
	
	for x in short13:
		sum13 += x
		
	for x in long75:
		sum75 += x
		
	sum13 += nowPrice
	sum75 += nowPrice
	
	###
	print(short13)
	print(sum13/25)
	print(sum75/75)
	###
	
	return [sum13/13,sum75/75]

def RSI(nowPrice): #RSI/引数:現価格/返り値:RSI(int)
	sumP = 0
	sumM = 0
	
	RSI = 0

	for x in range(12):
		dif = rsi14[x + 1] - rsi14[x]
		if dif >= 0:
			sumP += dif
		else:
			sumM -= dif

	dif = nowPrice - rsi14[12]
	if dif >= 0:
		sumP += dif
	else:
		sumM -= dif
	try:
		RSI = int(sumP/(sumP + sumM) * 100)
	except:
		pass
	
	###
	print(rsi14)
	print(RSI)
	###
	
	return RSI
	
while True:
	ntime = gettime()
	if ntime%5 > 4.5 and opend(ntime):#5秒ごと and 市場が開いているか
		oriPrice = getPrice()#mes(list)から価格だけを抽出してmessage(str)に格納
		price = re.search('[0-9]{2},[0-9]{3}.[0-9]{1}', str(oriPrice[0]) ).group() #priceはString型
		
		price = float( price.replace(',','')) #priceをfloat型へ変換
		
		###
		print(price)
		###
		
		ave = average( price )
		rsi = RSI( price )
		
		if zaraba(ntime):
			if rsi>=30 and ave[0]-40>price and ave[1]-40>price:
				send("買いMA発動中")
			elif rsi<70 and ave[0]+40<price and ave[1]+40<price:
				send("売りMA発動中")
			else:
				pass
		else:
			pass
				
		if ntime%500 > 499.5:#5分ごと
			###
			print(price)
			###
			stock( price )
		else:
			pass
			
		###
		print("\n")
		###
		
		time.sleep(0.1)#未検証
	else:
		pass