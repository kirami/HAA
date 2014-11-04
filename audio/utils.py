from audio.models import Address, Item, Bid, Invoice, Payment, Consignor
from django.db import connection
from django.db.models import Sum

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

#Bid utils

#returns ALL items in db with no bids ever.
def getNoBidItems(auctionId, orderByName = False):
	query = 'SELECT * from audio_item where id not in (select item_id from audio_bid) and auction_id=' + str(auctionId)
	if orderByName:
		query+= " order by name"
	return list(Item.objects.raw(query))

def resetWinners(auctionId):
	return Bid.objects.filter(item__auction = auctionId).update(winner=False)

def getBidItems(auctionId, orderByName = False):
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


def getSumWinners(auctionId):
	winners = getWinningBids(auctionId)
	if len(winners) > 0:
		return winners.aggregate(Sum('amount'))["amount__sum"] 
	else:
		return 0

def getDuplicateItems(auctionId):
	auctionId = 1
	return Item.objects.filter(quantity__gte=2, auction_id = auctionId)


def getOrderedBids(auctionId):
	return list(Bid.objects.raw('SELECT b.* FROM audio_bid b, audio_item i WHERE b.item_id = i.id and i.auction_id = '+str(auctionId)+'  ORDER BY item_id ASC, amount DESC, date ASC;'))




#get consigned items won in certain auction by consignor
def getConsignmentWinners(consignorId = None, auctionId = None):
	cursor = connection.cursor()
	sql = "select * from audio_bid b, audio_consignment c, audio_item i where b.winner = true and b.item_id = c.item_id and c.item_id = i.id"
	if auctionId != None:
		sql +=" and i.auction_id = "+str(auctionId)

	if consignorId != None:
		sql += " and c.consignor_id = "+str(consignorId)

	cursor.execute(sql)
	row = dictfetchall(cursor)
	return row
'''
#get consignors with winning items
def getConsignorBidSums(auctionId):
	cursor = connection.cursor()
	cursor.execute("select consignor_id, cc.first_name, cc.last_name, sum(b.amount) from audio_bid b, audio_consignment c, audio_consignor cc, audio_item i where b.winner = true and b.item_id = c.item_id and cc.id = c.consignor_id and i.auction_id = "+str(auctionId)+" and i.id = b.item_id group by consignor_id;") 
	row = dictfetchall(cursor)
	return row
'''

#get consigment which was not won in this auction
def getConsignedLosers(auctionId, consignorId):
	cursor = connection.cursor()
	cursor.execute("select * from audio_consignment  c, audio_item i where auction_id = "+ str(auctionId)+" and item_id not in(select distinct b.item_id "+
	"from audio_bid b where b.winner = true) and c.item_id = i.id")
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
	cursor.execute("SELECT distinct au.id, au.last_name, au.first_name from audio_bid b, "+
		" auth_user au, audio_item i WHERE b.winner = true and b.item_id = i.id and b.user_id = au.id and i.auction_id="+
		str(auctionId) + " order by last_name")
	row = dictfetchall(cursor)
	return row



def getInvoices(auctionId = None):
	if auctionId == None:
		return Invoice.objects.all() 
	else:
		return Invoice.objects.filter(auction_id = auctionId)
	
def getTotalInvoiceAmount(auctionId = None):
	invoices = getInvoices(auctionId)
	if len(invoices) > 0:
		return invoices.aggregate(Sum('invoiced_amount'))["invoiced_amount__sum"] 
	else:
		return 0

def getInvoiceInfoByUser(userId, auctionId = None):
	if auctionId == None:
		invoices = Invoice.objects.filter(user_id = userId)
	else:
		invoices = Invoice.objects.filter(user_id = userId, auction_id = auctionId)
	
	if len(invoices) > 0:
		return { "sum": invoices.aggregate(Sum('invoiced_amount'))["invoiced_amount__sum"], "invoices":invoices} 
	else:
		return { "sum": 0, "invoices":None} 

def getPaymentInfoByUser(userId, auctionId = None):
	
	if auctionId == None:
		payments = Payment.objects.filter(user_id = userId)
	else:
		payments = Payment.objects.filter(user_id = userId, auction_id = auctionId)
	
	if len(payments) > 0:
		return { "sum": payments.aggregate(Sum('amount'))["amount__sum"], "payments":payments} 
	else:
		return { "sum": 0, "payments":None} 

def getPayments(auctionId = None, userId = None):
	return Payment.objects.filter()

	
def getTotalPaymentAmount(auctionId = None):
	Payments = getPayments(auctionId)
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

	notWon = getConsignedLosers(consignorId, auctionId)
	consignedItems = getConsignmentWinners(consignorId, auctionId)
	
	consignTotal = 0
	haaTotal = 0
	total = 0
	gross = 0
	used = []

	for item in consignedItems:
		money = 0
		itemCost = item["amount"]
		min = item["minimum"]
		max = item["maximum"]
		percent = item["percentage"]
		item["inRange"] = 0
		
		if max == None and itemCost > min:
			money = (itemCost - min) * (percent/100)
			item["inRange"] = (itemCost - min)

		if itemCost >= max:
			money = (max - min) * (percent/100)
			item["inRange"] = (max - min)
		
		if itemCost <= max and itemCost > min:
			money = (itemCost - min) * (percent/100)
			item["inRange"] = (itemCost - min)

		if "consignorItemTotal" in item:
			item["consignorItemTotal"] += money
		else:
			item["consignorItemTotal"] = money;

		item["rangeAmount"] = money
		total += money

		if item["item_id"] not in used:
			gross += itemCost
			used.append(item["item_id"])
		
	data["gross"]=gross		
	data["consignedItems"] = consignedItems
	data["consignorTotal"] = total
	data["unsoldConsignorItems"] = notWon
	data["unsoldConsignorItemsCount"] = len(notWon)
	
	consignor = Consignor.objects.get(id = consignorId)
	data["firstName"] = consignor.first_name
	data["lastName"] =  consignor.last_name
	data["consignor"] = consignor.id
	return data


def getHeaderData(data, auctionId):
	winners = getWinningBids(auctionId)
 	noBids = getNoBidItems(auctionId)
 	losers = getLosingBids(auctionId)

 	data["auctionId"] = auctionId
 	data["winners"] = winners
 	data["losers"] = losers
 	data["loserCount"] = len(losers)
 	data["wonItems"] = getBidItems(auctionId)

 	data["wonItemsCount"] = len(data["wonItems"])
 	data["unsoldItems"] = noBids
 	data["noBidItemsCount"] = len(noBids)
 	data["total"] = getSumWinners(auctionId)	
 	return data