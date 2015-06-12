from audio.models import Address, Item, Bid, Invoice, Payment, Consignor, Consignment, User, UserProfile, Auction, PrintedCatalog
from django.db import connection
from django.db.models import Sum, Q
from django.conf import settings
from decimal import Decimal

from datetime import datetime, date
from django.db import transaction


import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def saveImg(fileData):
	with open(settings.IMAGES_ROOT +'items/'+fileData.name, 'wb+') as destination:
		for chunk in fileData.chunks():
			destination.write(chunk)
@transaction.commit_manually
def adjustLotIdsUtil(auctionId, index, increment = True):
	if increment:
		order = "-lot_id"
		op = "+"
	else:
		order = "lot_id"
		op = "-"

	#NEW
	items = Item.objects.filter(lot_id__gte=index, auction=auctionId).order_by(order)

	for entry in items:
		if increment:
			entry.lot_id += 1
		else:
			entry.lot_id -= 1
		entry.save()
	transaction.commit()

#auctions for a user where they won something.
def getWonAuctions(userId):
	#a = Item.objects.values_list("auction").filter(bidItem__winner=True, bidItem__user=5).distinct()
	#auctions = Auction.objects.filter(id__in=a)
	auctions = list(Auction.objects.raw('select distinct a.* from audio_auction a, audio_bid b, audio_item i where a.id = i.auction_id and b.item_id = i.id and b.user_id='+str(userId)+' and b.winner=true'))
	return auctions

def test():
	bidDict = {}
	bids = Bid.objects.filter(user = 1, item__auction = 3)
			
	for bid in bids:
		bidDict[str(bid.item.id)] = str(bid.amount)
	return bidDict


def getCurrentAuction():
	now = datetime.today()
	# where date is after start date and before second_end date
	auctions = Auction.objects.filter(start_date__lte = now, second_chance_end_date__gte = now)
	if len(auctions) == 1:
		return auctions[0]
	else:
		#TODO throw error
		return None

def getPreviousAuction():
	return 0

def isBetweenSegments():
	now =  datetime.now()
	currentAuction = getCurrentAuction()
	if not currentAuction:
		return False
	currentAuctionId = currentAuction.id
	auction = Auction.objects.get(id = currentAuctionId)
	if auction.end_date < now and auction.second_chance_start_date > now:
		return True
	return False


def isSecondChance():
	now =  datetime.now()
	#TODO current auction
	currentAuction = getCurrentAuction()
	if not currentAuction:
		return False
	currentAuctionId = currentAuction.id
	auction = Auction.objects.get(id = currentAuctionId)
	if auction.end_date < now and auction.second_chance_end_date > now and auction.second_chance_start_date < now:
		return True
	return False

#user utils

def itemSearch(items, search):
	return items.filter(Q(name__icontains=search) | Q(label__name__icontains=search) \
				| Q(artist__icontains=search) | Q(record_number__icontains=search) | \
				Q(name_two__icontains=search)  | Q(label__abbreviation__icontains=search)  \
				| Q(category__name__icontains=search) | Q(category__description__icontains=search) \
				| Q(notes__icontains=search) | Q(notes_two__icontains=search) \
				| Q(artist_two__icontains=search) | Q(record_number_two__icontains=search)) 

def usersWithoutAddress():
	return User.objects.filter(address=None)

def excludeFromEmails():
	return User.objects.filter(Q(is_staff=True) | Q(upUser__quiet=True) | Q(upUser__deadBeat=True))

#users with no bids	
def getNewUsers(auction, emailOnly = False, excludeEbay = True):
	users = User.objects.filter(bidUser__isnull=True, is_staff = False, date_joined__gt = auction.end_date)
	if excludeEbay:
		admin = User.objects.filter(Q(is_staff=True) | Q(upUser__quiet=True)| Q(upUser__ebay=True) | Q(upUser__deadBeat=True))
	
	else:
		admin = excludeFromEmails()

	all = set(users) - set(admin)


	#exlude = User.objects.
	#users = User.objects.raw('select a.id from auth_user a where a.id not in (select b.user_id from audio_bid b);')

	return UserProfile.objects.filter(user__in=all)

#users bid within last 3 auctions or printed list = true or paid for a catalog within 3 auctions
def getCurrentUsers(auctionId, excludeEmailOnly = False, excludePDF = False, excludeEbay = True, excludePrintedNotices = False):
	users = User.objects.filter(bidUser__item__auction__gt = int(auctionId)-4).distinct()
	printed = User.objects.filter(pcUser__auction__lte = auctionId, pcUser__auction__gt=(int(auctionId)-3))
	
	if excludeEbay:
		admin = User.objects.filter(Q(is_staff=True) | Q(upUser__quiet=True)| Q(upUser__ebay=True)| Q(upUser__deadBeat=True))
	
	else:
		admin = User.objects.filter(Q(is_staff=True) | Q(upUser__quiet=True)| Q(upUser__deadBeat=True))
	
	combined = set(users) | set(printed)
	
	#only those not on pdf list
	if excludePDF:
		nonPDF = User.objects.filter(upUser__pdf_list=False)
		combined = combined & set(nonPDF)

	#only printed notices	
	if excludeEmailOnly:
		nonEmailOnly = User.objects.filter(upUser__email_only=False)
		combined = combined & set(nonEmailOnly)

	#only email notices
	if excludePrintedNotices:
		emailOnly = User.objects.filter(upUser__email_only=True)
		combined = combined & set(emailOnly)


	all = combined - set(admin)

	#and is not quiet

	return UserProfile.objects.filter(user__in=all)

#users no bid last three auctions & not on keep me on list & no printed catalog bought
#reminder group
def getNonCurrentUsers(auctionId, emailOnly = False, printedOnly = False, excludeEbay = True):
	#not bids last 3 auctions, but bid in 4th

	users = User.objects.filter(bidUser__item__auction__gt = int(auctionId)-5 ).exclude(bidUser__item__auction__gt = int(auctionId)-4).distinct()
	if excludeEbay:
		admin = User.objects.filter(Q(is_staff=True) | Q(upUser__quiet=True)| Q(upUser__ebay=True)| Q(upUser__deadBeat=True))
	
	else:
		admin = User.objects.filter(Q(is_staff=True) | Q(upUser__quiet=True)| Q(upUser__deadBeat=True))
	
	printed = User.objects.filter(pcUser__auction__lte = auctionId, pcUser__auction__gt=(int(auctionId)-3))
	combined = set(users) - set(admin) - set(printed)
	
	if emailOnly:
		emailOnly = User.objects.filter(upUser__email_only=True)
		combined = combined & set(emailOnly)

	if printedOnly:
		printedOnly = User.objects.filter(upUser__email_only=False)
		combined = combined & set(emailOnly)

	return UserProfile.objects.filter(user__in=combined)

#take off
def getActiveUsers():
	return ""

#bidders are not current but have bid in the past
#TODO of all time or past # of auctions??
def getNonActiveUsers(auctionId, emailOnly = False, printedOnly = False, excludeEbay = True):
	
	#no bids since 4 or more
	users = User.objects.filter(bidUser__isnull=False).exclude(bidUser__item__auction__gt = int(auctionId)-5).distinct()
	
	if excludeEbay:
		admin = User.objects.filter(Q(is_staff=True) | Q(upUser__quiet=True)| Q(upUser__ebay=True)| Q(upUser__deadBeat=True))
	
	else:
		admin = User.objects.filter(Q(is_staff=True) | Q(upUser__quiet=True)| Q(upUser__deadBeat=True))

	printed = User.objects.filter(pcUser__auction__lte = auctionId, pcUser__auction__gt=(int(auctionId)-3))
	combined = set(users) - set(admin) - set(printed)

	if emailOnly:
		emailOnly = User.objects.filter(upUser__email_only=True)
		combined = combined & set(emailOnly)

	if printedOnly:
		printedOnly = User.objects.filter(upUser__email_only=False)
		combined = combined & set(emailOnly)
	
	return UserProfile.objects.filter(user__in=combined)

def getCourtesyBidders():
	
	ids = UserProfile.objects.values_list("user", flat=True).filter(courtesy_list = True)
	users = User.objects.filter(pk__in=set(ids))
	return UserProfile.objects.filter(user__in=set(users))


#Bid utils

def getBidders(auctionId):
	ids = Bid.objects.values_list("user", flat=True).filter(item__auction = auctionId)
	users = User.objects.filter(pk__in=set(ids))
	return users
	


def getLosers(auctionId):
	
	losers = Bid.objects.filter(item__auction=auctionId, winner = False).distinct().values_list("user", flat=True)
	winners = Bid.objects.filter(item__auction=auctionId, winner = True).distinct().values_list("user", flat=True)
	return UserProfile.objects.filter(user__in=set(losers) - set(winners))
	

#returns ALL items in db with no bids ever.
def getNoBidItems(auctionId, orderBy=None):
	if orderBy:
		return Item.objects.filter(bidItem=None, auction=auctionId).order_by(orderBy)
	else:
		return Item.objects.filter(bidItem=None, auction=auctionId)
	

def resetWinners(auctionId):
	#todo check lock here?
	return Bid.objects.filter(item__auction = auctionId).update(winner=False)

def getBidItems(auctionId, orderByName = False):
	if orderByName:
		return Item.objects.filter(bidItem__isnull=False, auction=auctionId).order_by("name")
	else:
		return Item.objects.filter(bidItem__isnull=False, auction=auctionId)

#get winning flat bids after blind auction end date
def getWinningFlatBids(auctionId, date, userId = None, onlyNonInvoiced = False):
	
	if onlyNonInvoiced:
		if userId == None:
			return Bid.objects.filter(winner=True, item__auction=auctionId, date__gte=date, invoice = None )
		else:
			return Bid.objects.filter(winner=True, item__auction=auctionId, user=userId, date__gte=date, invoice = None)
	else:
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


def getWinningBidsFromLosers(auctionId, userId):
	items = Item.objects.filter(bidItem__winner = False, auction=auctionId, bidItem__user = userId)
	return  Bid.objects.filter(winner=True, item__in=set(items))

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
		return { "sum": 0 , "wonItems":None} 

#date is end of blind auction
def getWinnerFlatSum(auctionId, userId, date = None):
	winners = getWinningFlatBids(auctionId, userId=userId, date = date)
	if len(winners) > 0:
		return { "sum": winners.aggregate(Sum('amount'))["amount__sum"] , "wonItems":winners} 

	else:
		return { "sum": 0 , "wonItems":None} 

def getSumWinners(auctionId, userId = None, date = None):
	winners = getWinningBids(auctionId, userId = userId, date = date)
	if len(winners) > 0:
		return { "sum": winners.aggregate(Sum('amount'))["amount__sum"] , "wonItems":winners} 

	else:
		return { "sum": 0 , "wonItems":None} 

def getSumDiscount(auctionId):
	return Invoice.objects.filter(auction = auctionId).aggregate(Sum('discount'))["discount__sum"]

def getDuplicateItems(auctionId):
	auctionId = 1
	return Item.objects.filter(quantity__gte=2, auction_id = auctionId)


def getOrderedBids(auctionId):
	return list(Bid.objects.raw('SELECT b.* FROM audio_bid b, audio_item i WHERE b.item_id = i.id and i.auction_id = '+str(auctionId)+'  ORDER BY item_id ASC, amount DESC, date ASC;'))


def getNonConsignedItems():
	return Item.objects.filter(consignedItem=None)


#get consigned items won in certain auction by consignor
def getConsignmentWinners(consignorId = None, auctionId = None):
	
	cursor = connection.cursor()
	sql = "select * from audio_bid b, audio_consignment c, audio_item i, audio_invoice ii where b.winner = true \
	and b.item_id = c.item_id and c.item_id = i.id and ii.id=b.invoice_id"
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

#get consigment which was has no BIDS in this auction
def getConsignmentLosers(auctionId, consignorId = None):
	if not consignorId:
		return Item.objects.filter(bidItem=None, auction=auctionId, consignedItem__isnull=False).distinct()
	else:
		return Item.objects.filter(bidItem=None, auction=auctionId, consignedItem__isnull=False, consignedItem__consignor=consignorId).distinct()

#get all consingors who had no won items
def getLoserConsignors(auctionId):
	ids = getWinnerConsignors(auctionId)
	all = Consignor.objects.filter(consignmentConsignor__item__auction = auctionId).distinct()
	return set(ids) ^ set(all)
	
#returns consignor (id only) with won item
def getWinnerConsignors(auctionId):
	ids = Item.objects.filter(bidItem__isnull=False, auction=auctionId, consignedItem__isnull=False).distinct()
	
	return Consignment.objects.filter(item__in=set(ids)).distinct().values_list("consignor", flat=True)

	"""
	return list(Consignor.objects.raw('select cc.* from audio_consignment  c, audio_consignor cc, audio_bid b, audio_item i \
		where i.id = b.item_id and i.auction_id = '+str(auctionId)+ \
	' and c.item_id = i.id and c.consignor_id = cc.id group by consignor_id'))
	
	"""
#--------------------------

def getUnbalancedUsersByAuction(auctionId = None, userId = None):
	"""
	cursor = connection.cursor()
	sql = "SELECT user_id, invoiced, sum(invoiced) as iSum, auction_id, payments, sum(payments) as pSum, invoiced - payments AS balance \
	FROM \
	(   SELECT it.id AS invoice_id, it.user_id, it.auction_id, \
	it.invoiced_amount  + it.second_chance_invoice_amount + it.tax + it.second_chance_tax + it.shipping + it.second_chance_shipping - COALESCE(it.discount, 0) AS invoiced, \
	COALESCE(SUM(p.amount), 0) AS payments \
	    FROM audio_invoice AS it \
	    LEFT OUTER JOIN audio_payment AS p \
	    ON it.id = p.invoice_id \
	    AND it.user_id = p.user_id \
	    GROUP BY 1, 2, 3, 4 \
	) AS billing \
	WHERE invoiced != payments"
	if auctionId:
		sql = sql + " and auction_id = " + str(auctionId)

	if userId:
		sql = sql + " and user_id = " + str(userId)

	cursor.execute(sql)
	row = dictfetchall(cursor)
	return row
	"""
	return

def getUnbalancedUsers(userId = None):
	"""
	cursor = connection.cursor()
	sql = "SELECT user_id, coalesce(payments,0) as payments, invoiced, invoiced - coalesce(payments,0) as balance, auction_id \
    FROM(select sum(amount) as payments, it.user_id, invoiced, auction_id from audio_payment p \
    RIGHT JOIN (SELECT sum(invoiced_amount)  + sum(second_chance_invoice_amount) + sum(tax) + \
    sum(second_chance_tax) + sum(shipping) + sum(second_chance_shipping) - coalesce(sum(discount),0)  as invoiced, user_id, auction_id \
    FROM audio_invoice group by user_id) as it on it.user_id = p.user_id group by user_id) as joined \
    where joined.invoiced != joined.payments or joined.payments is NULL"
	if userId:
		sql = sql + " and user_id = " + str(userId)

	cursor.execute(sql)
	row = dictfetchall(cursor)
	return row
	"""
	return

def getAlphaWinners(auctionId, printOnly = False, emailOnly = False):
	if printOnly:
		return User.objects.filter(bidUser__item__auction = auctionId, bidUser__winner=True, upUser__email_only = False).distinct().order_by("last_name")
	if emailOnly:	
		return User.objects.filter(bidUser__item__auction = auctionId, bidUser__winner=True, upUser__email_only = True).distinct().order_by("last_name")
	if not emailOnly and not printOnly:
		return User.objects.filter(bidUser__item__auction = auctionId, bidUser__winner=True).distinct().order_by("last_name")



	'''
	cursor = connection.cursor()
	cursor.execute("SELECT distinct au.id, au.last_name, au.first_name from audio_bid b, "+
		" auth_user au, audio_item i WHERE b.winner = true and b.item_id = i.id and b.user_id = au.id and i.auction_id="+
		str(auctionId) + " order by last_name")
	row = dictfetchall(cursor)
	
	return row
	'''


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
		payments = Payment.objects.filter(user_id = userId, invoice__auction = auctionId)
	
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

	notWon = getConsignmentLosers(consignorId = consignorId, auctionId = auctionId)
	consignedItems = getConsignmentWinners(consignorId, auctionId)
	
	consignTotal = 0
	haaTotal = 0
	total = 0
	gross = 0
	used = []
	ordered = {}

	

	for item in consignedItems:
		money = 0
		itemCost = item["amount"]
		discount = item["discount_percent"]
		if discount:
			discount = Decimal(discount)
		if discount > 0:
			itemCost = itemCost * ((100-discount)/100)
			item["amount"] = itemCost
		
		
		min = item["minimum"]
		max = item["maximum"]	
		percent = item["percentage"]
		item["inRange"] = 0
	
		if max == None and itemCost > min:
			money = (itemCost - min) * (percent/100)
			item["inRange"] = (itemCost - min)

		if itemCost >= max and max != None:
			money = (max - min) * (percent/100)
			item["inRange"] = (max - min)
		
		if itemCost <= max and itemCost > min:
			money = (itemCost - min) * (percent/100)
			item["inRange"] = (itemCost - min)

		
		money = round(money,2)	

		if "consignorItemTotal" in item:
			item["consignorItemTotal"] += money
		else:
			item["consignorItemTotal"] = money;

		item["rangeAmount"] = money
		total += money

		if item["item_id"] not in used:
			gross = gross + itemCost
			used.append(item["item_id"])
		
		if str(item["item_id"]) not in ordered:
			ordered[str(item["item_id"])]= []
			ordered[str(item["item_id"])].append(item)
		else:
			ordered[str(item["item_id"])].append(item)
		
		
	data["ordered"] = ordered	
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

def gatherInfoFromInvoice(data, invoice, balance = None):
	
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
	data["orderTotal"] = balance
	#TODO discount on here or off of each amount already???
	data["previousBalance"] = balance - (invoice.invoiced_amount + tax + shipping + secondTax + secondShipping + secondAmount - discount)
	data["balanceDate"] = date.today() 
	return data

def getInvoiceData(auctionId, userId):
	data = {}
	#balances = getUnbalancedUsers(userId = userId)
	#balances = getUnbalancedUsersByAuction(userId = userId)
	balance = getInvoiceInfoByUser(userId)["sum"] - getPaymentInfoByUser(userId)["sum"]

		
	data["info"]=getSumWinners(auctionId, userId)
	invoices = Invoice.objects.filter(auction = auctionId, user = userId)
	data["auction"] = Auction.objects.get(pk=auctionId)
	data["user"]= User.objects.get(pk=userId)
	
	if len(invoices) > 0:
		invoice = invoices[0]
		gatherInfoFromInvoice(data, invoice, balance)
	return data



def getHeaderData(data, auctionId):
	winningBids = getWinningBids(auctionId)
	noBids = getNoBidItems(auctionId)
	losers = getLosers(auctionId)
	winners = getAlphaWinners(auctionId)

	data["auctionId"] = auctionId
	data['auction'] = Auction.objects.get(pk=auctionId)
	data["winners"] = winningBids

	data["winnersCount"] = len(winners)
	data["losers"] = losers
	data["loserCount"] = len(losers)
	data["wonItems"] = getBidItems(auctionId)

	data["wonItemsCount"] = len(data["wonItems"])
	data["unsoldItems"] = noBids
	data["noBidItemsCount"] = len(noBids)
	sums = getSumWinners(auctionId)
	data["discount"] = getSumDiscount(auctionId)
	data ["preDiscount"] = sums["sum"]
	data["today"] = date.today()
	if len(sums) > 0:
		if data["discount"]:
			data["total"] = sums["sum"]	- data["discount"]
		else:
			data["total"] = sums["sum"]	
	else:
		data["total"] = 0
	return data