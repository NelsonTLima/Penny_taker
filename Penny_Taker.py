import requests, json, concurrent.futures, sys
from tqdm import tqdm
from datetime import datetime, timedelta
from os import system
from time import sleep
main = True
try:
	from save.save_module import save
	bought, success, stop_losses, buying_price, buying_time, profits, trades = save()
except:
	bought = False
	success = 0
	stop_losses = 0
	buying_price = 0
	buying_time = ''
	profits = []
	trades = {}
save_dic = {}
selling_price = 0

with tqdm (total=3) as bar:
	while main == True:
		date_time = datetime.now()
		date = date_time.strftime('%d/%m/%Y - %H:%M:%S')
		date_day = date_time.strftime('%d-%m-%Y')
		urls = []
		currency = 'BTCUSDT'
		intervals = ['15m', '1h']
		urls_dic = {}

		def get_endpoint(currency, interval):
			symbols = {
				'currency' : f'?symbol={currency}',
				'interval' : f'&interval={interval}'
				}
		
			endpoints = {
				'price' : f"api/v3/ticker/bookTicker{symbols['currency']}",
				'klines': f"api/v3/klines{symbols['currency']}{symbols['interval']}"
				}
			
			return symbols, endpoints

		def get_data(url, timeout=2):
			try:
				request = requests.get(url)
				response = request.json()
				return response
			except:
				print('connection problem')

		def current_price():
			ask = float(response['askPrice'])
			bid = float(response['bidPrice'])
			return ask, bid

		def klines_m():
			data = response[-3:]
			return data

		def klines_h():
			data = response[-5:]
			return data

		def time_in_kline(data):
			time_in_data = str(data[0])
			timestamp_open = float(time_in_data[0:10])
			open_time = datetime.fromtimestamp(timestamp_open)
			close_time_in_data = str(data[6])
			timestamp_close = float(close_time_in_data[0:10])
			close_time = datetime.fromtimestamp(timestamp_close)
			return open_time, close_time

		def data_in_kline(data):
			open_kline = float(data[1])
			high = float(data[2])
			low = float(data[3])
			close = float(data[4])
			volume = float(data[5])
			return open_kline, high, low, close, volume

		def average():
			if len(lowest) >= 1:
				lowest_average = sum(lowest)/len(lowest)
			else:
				lowest_average = 0
			if len(highest) >= 1:
				highest_average = sum(highest)/len(highest)
			else:
				highest_average = 0
			return lowest_average, highest_average
		
		for interval in intervals:
			symbols, endpoints = get_endpoint(currency, interval)
			endpoint = endpoints['klines']
			url = f'https://api.binance.com/{endpoint}'
			urls.append(url)
			urls_dic[url] = interval
		
		endpoint = endpoints['price']
		url = f'https://api.binance.com/{endpoint}'
		urls.append(url)
		urls_dic[url] = 'price'

		try:	
			with concurrent.futures.ThreadPoolExecutor(max_workers=len(urls)) as executor:
				future_to_url = {executor.submit(get_data, url): url for url in urls}
				for future in concurrent.futures.as_completed(future_to_url):
					url = future_to_url[future]
					response = future.result()
					bar.update()
					
					if urls_dic[url] == intervals[0]:
						lowest = []
						highest = []
						data = klines_m()
						
						for data in data:
							open_kline, high, low, close, volume = data_in_kline(data)
							open_time, close_time = time_in_kline(data)
							if open_kline < close:
								highest.append(volume)
							else:
								lowest.append(volume)

						selling_volume, buying_volume = average()

						if selling_volume > buying_volume:
							volume_raise = False
						else:
							volume_raise = True

						if len(lowest) <= len(highest):
							candle_raise = True
						else:
							candle_raise = False
				
					elif urls_dic[url] == intervals[1]:
						data = klines_h()
						lowest = []
						highest = []
						
						for data in data:
							open_kline, high, low, close, volume = data_in_kline(data)
							open_time, close_time = time_in_kline(data)
							lowest.append(low)
							highest.append(high)

						lowest_average, highest_average = average()
						resistance = highest_average
						half_way = (lowest_average + highest_average)/2
						buying_zone_end = (lowest_average + half_way)/2
						buying_zone_start = (lowest_average + min(lowest))/2
						stop_loss = min(lowest)
				
					else:
						ask, bid = current_price()

				if bought == False:
					if candle_raise == True:
						if volume_raise == True:
							if ask < buying_zone_end:
								if ask > buying_zone_start:
									buying_price = ask
									buying_time = date
									bought = True
			# stop-loss	
				else:
					selling_price = bid
					selling_time = date
					profit = ((selling_price - buying_price)/buying_price)
					
					if bid <= stop_loss:
						trades[f'{selling_time}'] = {
							'buying time': buying_time,
							'result': 'Stop Loss',
							'buying price': buying_price,
							'selling price': selling_price,
							'profit': f'{profit: .2%}'
						}
						profits.append(profit)
						stop_losses += 1
						bought = False
			# selling
					if resistance <= buying_price*1.003:
						if selling_price >= buying_price*1.0025:
							profits.append(profit)
							trades[f'{selling_time}'] = {
								'buying time': buying_time,
								'buying price': buying_price,
								'selling price': selling_price,
								'profit': f'{profit: .2%}',
								'result': 'success'
								}
							success += 1
							bought = False
					else:
						if candle_raise == False:
							if volume_raise == False:
								if selling_price > buying_price*1.002:
									profits.append(profit)
									trades[f'{selling_time}'] = {
										'buying time': buying_time,
										'buying price': buying_price,
										'selling price': selling_price,
										'profit': f'{profit: .2%}',
										'result': 'success'
										}
									success += 1
									bought = False

				if profits == []:
					average_profit = 0
					total_profit = 0
				else:
					average_profit = sum(profits)/len(profits)
					total_profit = sum(profits)
				if trades != {}:
					efficiency = success/(success + stop_losses)
				else:
					efficiency = 0
				
				file = open(f'data/{date_day}.txt', 'w')
				file.write(f'\
PENNY_TAKER\n\n\
Success: {success} times.\n\
Fails: {stop_losses} times\n\
total profit: {total_profit: .2%}\n\
average profit: {average_profit: .2%}\n\
efficiency: {efficiency: .2%}\n\n\
TRADES:\n\n\
{trades}')
			file.close()

			if sys.platform == 'win32':
				system('cls') or None
			else:
				system('clear') or None
			
			print(date)
			if bought == False:
				print(f'\ncurrent price: {ask}\n')
			else:
				print(f'\ncurrent price: {bid}\n')
				print(f'Bought for: {buying_price: .2f}')
				print(f'Operation profit: {profit: .2%}\n')
				print(f'lower selling price: {buying_price*1.002: .2f}')
			print(f'resistance: {resistance: .2f}')
			print(f'Buying zone end: {buying_zone_end: .2f}')
			print(f'Buying zone start: {buying_zone_start: .2f}')
			print(f'stop loss: {stop_loss: .2f}')
			print('\nSTATUS:\n')
			
			if bought == True:
				print('BOUGHT')
			else:
				print('SOLD')
			if candle_raise == False:
				print('price is reducing')
			else:
				print('price is raising')
			if volume_raise == False:
				print('buying volume is lower')
			else:
				print('buying volume is higher')
			if selling_price < buying_price*1.002:
				print('Price is lower than selling threshold')
			if bought == False:
				if ask < buying_zone_start:
					print('price is lower than buying threshold')
				elif ask > buying_zone_end:
					print('price is higher than buying threshold')

			print(f'\nsuccess: {success} times')
			print(f'stop losses: {stop_losses} times')
			print(f'total profit: {total_profit: .2%}')
			print(f'average profit: {average_profit: .2%}')
			print(f'efficiency: {efficiency: .2%}\n')

			save = open('save/save_module.py', 'w')
			save.write(f"\
def save():\n\
	from datetime import datetime, timedelta\n\
	date_time=datetime.now() - timedelta(seconds = 5)\n\
	today=date_time.strftime('%d-%m-%Y')\n\
	saved_date='{date_day}'\n\
	bought={bought}\n\
	buying_price={buying_price}\n\
	buying_time='{buying_time}'\n\
	if today == saved_date:\n\
		success={success}\n\
		stop_losses={stop_losses}\n\
		profits={profits}\n\
		trades={trades}\n\
	else:\n\
		bought={bought}\n\
		success=0\n\
		stop_losses=0\n\
		buying_time=''\n\
		profits=[]\n\
		trades={save_dic}\n\
	return bought, success, stop_losses, buying_price, buying_time, profits, trades")
			save.close()

		except Exception as exc:
			print(exc)
