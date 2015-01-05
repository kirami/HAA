from audio.models import Address, Item, Bid, Invoice, Payment, Consignor, User, UserProfile, Auction
from django.db import connection
from django.db.models import Sum
from django.conf import settings

from datetime import datetime, date

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def saveImg(fileData):
	with open(settings.IMAGES_ROOT +'items/'+fileData.name, 'wb+') as destination:
		for chunk in fileData.chunks():
			destination.write(chunk)

def test():
	bidDict = {}
	bids = Bid.objects.filter(user = 1, item__auction = 3)
			
	for bid in bids:
		bidDict[str(bid.item.id)] = str(bid.amount)
	return bidDict

def getCurrentAuction():
	now = date.today()
	# where date is after start date and before second_end date
	auctions = Auction.objects.filter(start_date__lte = now, second_chance_end_date__gte = now)
	if len(auctions) == 1:
		return auctions[0]
	else:
		#TODO throw error
		return None

def isSecondChance():
	now =  datetime.now()
	#TODO current auction
	currentAuction = getCurrentAuction()
	currentAuctionId = currentAuction.id
	auction = Auction.objects.get(id = currentAuctionId)
	if auction.end_date < now and auction.second_chance_end_date > now:
		return True
	return False

#user utils

def usersWithoutAddress():
	return User.objects.filter(address=None)


#users with no bids	
def getNewUsers():
	users = User.objects.raw('select a.id from auth_user a where a.id not in (select b.user_id from audio_bid b);')
	return list( users), Address.objects.filter(user__in=set(users))

#users bid within last 3 auctions
def getCurrentUsers(auctionId):
	users = list(User.objects.raw('select a.* from auth_user a, audio_bid b, audio_item i where a.id = b.user_id and b.item_id = i.id and i.auction_id > '+str(auctionId)+' group by b.user_id'))
	ids = UserProfile.objects.values_list("user", flat=True).filter(printed_list = True)
	two = User.objects.filter(pk__in=set(ids))
	combined = set(users) | set(two)
	return list(combined), Address.objects.filter(user__in=set(combined))

#users no bid last three auctions & not on keep me on list
def getNonCurrentUsers(auctionId):
	users = list(User.objects.raw('select a.* from auth_user a where id not in(select a.id from auth_user a, audio_bid b, audio_item i where a.id = b.user_id and b.item_id = i.id and i.auction_id > '+ str(auctionId) +' group by b.user_id)'))
	ids = UserProfile.objects.values_list("user", flat=True).filter(printed_list = False)
	two = User.objects.filter(pk__in=set(ids))
	combined = set(users) & set(two)
	return list(combined), Address.objects.filter(user__in=set(combined))

def getActiveUsers():
	return ""

#bidders are not current but have bid in the past
def getNonActiveUsers(auctionId):
	nonCurrent = getNonCurrentUsers(auctionId)[0]
	pastBidders = list(User.objects.raw('select distinct a.id from audio_bid b, auth_user a where a.id=b.user_id'))
	combined = set(nonCurrent) & set(pastBidders)
	return list(combined), Address.objects.filter(user__in=set(combined))


def getCourtesyBidders():
	ids = UserProfile.objects.values_list("user", flat=True).filter(courtesy_list = True)
	users = User.objects.filter(pk__in=set(ids))
	return users, Address.objects.filter(user__in=set(users))


#Bid utils

def getLosers(auctionId):
	return list(Bid.objects.raw('select b.* from audio_bid b, audio_item i where i.id = b.item_id and i.auction_id = '+str(auctionId)+' group by user_id HAVING COUNT(CASE WHEN winner=1 THEN 1 ELSE NULL END) <1;'))

#returns ALL items in db with no bids ever.
def getNoBidItems(auctionId, orderByName = False):
	query = 'SELECT * from audio_item where id not in (select item_id from audio_bid) and auction_id=' + str(auctionId)
	if orderByName:
		query+= " order by name"
	return list(Item.objects.raw(query))

def resetWinners(auctionId):
	#todo check lock here?
	return Bid.objects.filter(item__auction = auctionId).update(winner=False)

def getBidItems(auctionId, orderByName = False):
	query = 'SELECT * from audio_item where id in (select item_id from audio_bid) and auction_id =' + str(auctionId)
	if orderByName:
		query+= " order by name"
	return list(Item.objects.raw(query))

#get winning flat bids after blind auction end date
def getWinningFlatBids(auctionId, date, userId = None):
	if userId == None:
		return Bid.objects.filter(winner=True, item__auction=auctionId, date__gte=date )
	else:
		return Bid.objects.filter(winner=True, item__auction=auctionId, user=userId, date__gte=date)
	

#if date - get bids before said date
def getWinningBids(auctionId, userId = None, date = None, onlyNonInvoiced = False):

	if onlyNonInvoiced:

		if userId == None:
			if date == None:
				return Bid.objects.filter(winner=True, item__auction=auctionId, invoice = None)
			else:
				return Bid.objects.filter(winner=True, item__auction=auctionId, date__lte=date , invoice = None)
		else:
			if date == None:
				return Bid.objects.filter(winner=True, item__auction=auctionId, user=userId, date__lte=date, invoice = None)
			else:
				return Bid.objects.filter(winner=True, item__auction=auctionId, user=userId, invoice = None)
	else:
		if userId == None:
			if date == None:
				return Bid.objects.filter(winner=True, item__auction=auctionId)
			else:
				return Bid.objects.filter(winner=True, item__auction=auctionId, date__lte=date)
		else:
			if date == None:
				return Bid.objects.filter(winner=True, item__auction=auctionId, user=userId)
				
			else:
				return Bid.objects.filter(winner=True, item__auction=auctionId, user=userId, date__lte=date)


def getLosingBids(auctionId, userId = None):

	if userId == None:
		return Bid.objects.filter(winner=False, item__auction=auctionId)
	else:
		return Bid.objects.filter(winner=False, item__auction=auctionId, user=userId)


def getWinnerSum(auctionId, userId, date = None, onlyNonInvoiced = False):
	winners = getWinningBids(auctionId, userId, date = date, onlyNonInvoiced = onlyNonInvoiced)
	if len(winners) > 0:
		return { "sum": winners.aggregate(Sum('amount'))["amount__sum"] , "wonItems":winners} 

	else:
		return 0

#date is end of blind auction
def getWinnerFlatSum(auctionId, userId, date = None):
	winners = getWinningFlatBids(auctionId, userId=userId, date = date)
	if len(winners) > 0:
		return { "sum": winners.aggregate(Sum('amount'))["amount__sum"] , "wonItems":winners} 

	else:
		return 0

def getSumWinners(auctionId, userId = None, date = None):
	winners = getWinningBids(auctionId, userId = userId, date = date)
	if len(winners) > 0:
		return { "sum": winners.aggregate(Sum('amount'))["amount__sum"] , "wonItems":winners} 

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
	sql = "select * from audio_consignment  c, audio_item i where auction_id = "+ str(auctionId)+" and item_id not in(select distinct b.item_id from audio_bid b where b.winner = true) and c.item_id = i.id"
	if consignorId != None:
		sql = sql + " and c.consignor_id = " + str(consignorId)
	cursor.execute(sql)
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
		sum1 = invoices.aggregate(Sum('invoiced_amount'))["invoiced_amount__sum"] or 0
		sum2 = invoices.aggregate(Sum('second_chance_invoice_amount'))["second_chance_invoice_amount__sum"] or 0
		tax1 = invoices.aggregate(Sum('tax'))["tax__sum"] or 0
		tax2 = invoices.aggregate(Sum('second_chance_tax'))["second_chance_tax__sum"] or 0
		shipping1 = invoices.aggregate(Sum('shipping'))["shipping__sum"] or 0
		shipping2 = invoices.aggregate(Sum('second_chance_shipping'))["second_chance_shipping__sum"] or 0
		discount = invoices.aggregate(Sum('discount'))["discount__sum"] or 0

		return sum1 + sum2 + tax1 + tax2 + shipping1 + shipping2 - discount
	else:
		return 0

def getInvoiceInfoByUser(userId, auctionId = None):
	if auctionId == None:
		invoices = Invoice.objects.filter(user_id = userId)
	else:
		invoices = Invoice.objects.filter(user_id = userId, auction_id = auctionId)
	
	if len(invoices) > 0:
		
		sum1 = invoices.aggregate(Sum('invoiced_amount'))["invoiced_amount__sum"] or 0
		sum2 = invoices.aggregate(Sum('second_chance_invoice_amount'))["second_chance_invoice_amount__sum"] or 0
		tax1 = invoices.aggregate(Sum('tax'))["tax__sum"] or 0
		tax2 = invoices.aggregate(Sum('second_chance_tax'))["second_chance_tax__sum"] or 0
		shipping1 = invoices.aggregate(Sum('shipping'))["shipping__sum"] or 0
		shipping2 = invoices.aggregate(Sum('second_chance_shipping'))["second_chance_shipping__sum"] or 0
		discount = invoices.aggregate(Sum('discount'))["discount__sum"] or 0

		sum = sum1 + sum2 + tax1 + tax2 + shipping1 + shipping2 - discount

		return { "sum": sum, "invoices":invoices} 
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

	notWon = getConsignedLosers(consignorId = consignorId, auctionId = auctionId)
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
		'''
		logger.error("cost: %s" % itemCost)
		logger.error("min: %s" % min)
		logger.error("max: %s" % max)		
		logger.error("percent: %s" % percent)
		'''
		
		if max == None and itemCost > min:
			money = (itemCost - min) * (percent/100)
			item["inRange"] = (itemCost - min)

		if itemCost >= max and max != None:
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


def getInvoiceData(auctionId, userId):
	data = {}
	data["info"]=getSumWinners(auctionId, userId)
	invoices = Invoice.objects.filter(auction = auctionId, user = userId)
	if len(invoices) > 0:
		invoice = invoices[0]
		data["invoice"] = invoice
		shipping = invoice.shipping or 0
		tax = invoice.tax or 0
		secondAmount = invoice.second_chance_invoice_amount or 0
		secondShipping = invoice.second_chance_shipping or 0
		secondTax = invoice.second_chance_tax or 0
		discount = invoice.discount or 0
		data["discount"] = discount
		data["taxTotal"] = tax + secondTax
		data["shippingTotal"] = shipping + secondShipping
		data["orderTotal"] = invoice.invoiced_amount + tax + shipping + secondTax + secondShipping + secondAmount - discount
	return data



def getHeaderData(data, auctionId):
	winningBids = getWinningBids(auctionId)
 	noBids = getNoBidItems(auctionId)
 	losers = getLosingBids(auctionId)
 	winners = getAlphaWinners(auctionId)

 	data["auctionId"] = auctionId
 	data["winners"] = winningBids

 	data["winnersCount"] = len(winners)
 	data["losers"] = losers
 	data["loserCount"] = len(losers)
 	data["wonItems"] = getBidItems(auctionId)

 	data["wonItemsCount"] = len(data["wonItems"])
 	data["unsoldItems"] = noBids
 	data["noBidItemsCount"] = len(noBids)
 	sums = getSumWinners(auctionId)
 	if len(sums) > 0:
 		data["total"] = sums["sum"]	
 	else:
 		data["total"] = 0
 	return data