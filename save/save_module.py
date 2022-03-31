def save():
	from datetime import datetime
	date_time=datetime.now()
	today=date_time.strftime('%d-%m-%Y')
	saved_date='31-03-2022'
	bought=False
	buying_price=0
	buying_time=''
	if today == saved_date:
		success=0
		stop_losses=0
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