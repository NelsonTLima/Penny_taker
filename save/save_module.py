def save():
	from datetime import datetime
	date_time=datetime.now()
	today=date_time.strftime('%d-%m-%Y')
	saved_date='2022-03-31 01:49:07.079371'
	bought=False
	if today == saved_date:
		success=0
		stop_losses=0
		if bought == True:
			buying_price=0
			buying_time=''
		else:
			buying_time=''
		profits=[]
		trades={}
	else:
		bought=False
		success=0
		stop_losses=0
		buying_time=''
		profits=[]
		trades={}
	return bought, success, stop_losses, buying_price, buying_time, profits, trades