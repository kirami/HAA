from audio.models import Address, Item, Bid, Invoice, Payment
from django.db import connection
from django.db.models import Sum


#Bid utils

#returns ALL items in db with no bids ever.
def getNoBidItems(orderByName = False):
	auctionId = 1
	#todo auctionid
	query = 'SELECT * from audio_item where id not in (select item_id from audio_bid)'
	if orderByName:
		query+= " order by name"
	return list(Item.objects.raw(query))

def resetWinners(auctionId):
	return Bid.objects.filter(item__auction = auctionId).update(winner=False)

def getBidItems(orderByName = False):
	auctionId = 1
	#todo auctionid
	query = 'SELECT * from audio_item where id in (select item_id from audio_bid) and auction_id =' + str(auctionId)
	if orderByName:
		query+= " order by name"
	return list(Item.objects.raw(query))

def getWinningBids(auctionId, userId = None):
	#todo auction id
	if userId == None:
		return Bid.objects.filter(winner=True, item__auction=auctionId)
	else:
		return Bid.objects.filter(winner=True, item__auction=auctionId, user=userId)


def getLosingBids(auctionId, userId = None):
	#todo auction id
	if userId == None:
		return Bid.objects.filter(winner=False, item__auction=auctionId)
	else:
		return Bid.objects.filter(winner=False, item__auction=auctionId, user=userId)


def getSumWinners():
	winners = getWinners()
	if len(winners) > 0:
		return winners.aggregate(Sum('amount'))["amount__sum"] 
	else:
		return 0

def getDuplicateItems(auctionId):
	auctionId = 1
	return Item.objects.filter(quantity__gte=2, auction_id = auctionId)


def getOrderedBids(auctionId):
	return list(Bid.objects.raw('SELECT b.* FROM audio_bid b, audio_item i WHERE b.item_id = i.id and i.auction_id = '+str(auctionId)+'  ORDER BY item_id ASC, amount DESC, date ASC;'))


#get consigned items won in certain auction
def getConsignmentWinners(auctionId):
	cursor = connection.cursor()
	cursor.execute("select * from audio_bid b, audio_consignment c where b.auction_id = "+str(auctionId)+
		" and b.winner = true and b.item_id = c.item_id;")
	row = dictfetchall(cursor)
	return row


#get consignors with winning items
def getConsignorBidSums(auctionId):
	cursor = connection.cursor()
	auctionId = 1
	cursor.execute("select consignor_id, cc.first_name, cc.last_name, sum(b.amount) from audio_bid b, audio_consignment c, audio_consignor cc where "+
		"b.winner = true and b.item_id = c.item_id and cc.id = c.consignor_id and b.auction_id = "+ str(auctionId)+" group by consignor_id;") 
	row = dictfetchall(cursor)
	return row

#get consigment which was not won in this auction
def getConsignedLosers(auctionId):
	auctionId = 1
	return ("select * from audio_consignment  c, audio_item i where auction_id = "+ str(auctionId)+" and item_id not in(select distinct b.item_id "+
	"from audio_bid b where b.winner = true) and c.item_id = i.id")

#get consigned items won in certain auction by consignor
def getConsignmentWinnersById(consignorId, auctionId):
	cursor = connection.cursor()
	cursor.execute("select * from audio_bid b, audio_consignment c, audio_item i where b.auction_id = "+str(auctionId)+
		" and b.winner = true and b.item_id = c.item_id and c.item_id = i.id and c.consignor_id = "+str(consignorId)+";")
	row = dictfetchall(cursor)
	return row

#--------------------------

def getUnbalancedUsers():
	cursor = connection.cursor()
	cursor.execute("select user_id, coalesce(payments,0) as payments, invoiced, invoiced - coalesce(payments,0) as balance "+
		"from(select sum(amount) as payments, it.user_id, invoiced from audio_payment p "+
		"right join (select sum(invoiced_amount) as invoiced, user_id from audio_invoice group by user_id) "+
		"as it on it.user_id = p.user_id group by user_id) as joined "+
		"where joined.payments != joined.invoiced or joined.payments is NULL")
	row = dictfetchall(cursor)
	return row

def getAlphaWinners(auctionId):
	cursor = connection.cursor()
	cursor.execute("SELECT distinct au.id, au.last_name, au.first_name, a.zipcode from audio_bid b, audio_address a, auth_user au "+
		"WHERE b.winner = true and b.user_id = a.user_id and au.id = a.user_id and b.auction_id = "+str(auctionId)+" order by last_name")
	row = dictfetchall(cursor)
	return row



def getInvoicesByAuction(auctionId):
	return Invoice.objects.filter(auction_id = auctionId)
	
def getTotalInvoiceAmountByAuction(auctionId):
	invoices = getInvoicesByAuction(auctionId)
	if len(invoices) > 0:
		return invoices.aggregate(Sum('invoiced_amount'))["invoiced_amount__sum"] 
	else:
		return 0

def getInvoiceInfoByUser(userId):
	invoices = Invoice.objects.filter(user_id = userId, auction_id = auctionId)
	if len(invoices) > 0:
		return { "sum": invoices.aggregate(Sum('invoiced_amount'))["invoiced_amount__sum"], "invoices":invoices} 
	else:
		return { "sum": 0, "invoices":None} 

def getPaymentInfoByUser(userId):
	payments = Payment.objects.filter(user_id = userId)
	if len(payments) > 0:
		return { "sum": payments.aggregate(Sum('amount'))["amount__sum"], "payments":payments} 
	else:
		return { "sum": 0, "payments":None} 

def getPaymentsByAuction():
	auctionId = 1
	return Payment.objects.filter()

	
def getTotalPaymentAmountByAuction():
	Payments = getPaymentsByAuction()
	if len(Payments) > 0:
		return Payments.aggregate(Sum('amount'))["amount__sum"] 
	else:
		return 0


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def getAllConsignmentInfo(consignorId, auctionId):
	data = {}
	#get all consigned won items with 
	#get all consigned lost items
	#description / bidder/ win amount/ consign amount / haa amount

	'''
	get all won items 
	for each item, get consignors, group by consignor id.
	'''

	notWon = getConsignedLosersById(consignorId, auctionId)
	consignedItems = getConsignmentWinnersById(consignorId, auctionId)
	
	consignTotal = 0
	haaTotal = 0
	total = 0
	gross = 0

	for item in consignedItems:
		money = 0
		itemCost = item["amount"]
		min = item["minimum"]
		max = item["maximum"]
		percent = item["percentage"]
		item["inRange"] = 0
		
		if max == None and itemCost >= min:
			money = (itemCost - min) * (percent/100)
			item["inRange"] = (itemCost - min)

		if itemCost >= max:
			money = (max - min) * (percent/100)
			item["inRange"] = (max - min)
		if itemCost <= max and itemCost >= min:
			money = (itemCost - min) * (percent/100)
			item["inRange"] = (itemCost - min)

		if "consignorItemTotal" in item:
			item["consignorItemTotal"] += money
		else:
			item["consignorItemTotal"] = money;

		item["rangeAmount"] = money
		total += money
		gross += itemCost

	data["consignedItems"] = consignedItems
	data["consignorTotal"] = total
	data["unsoldItems"] = notWon
	data["gross"] = gross
	return data