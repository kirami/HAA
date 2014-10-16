from audio.models import Address, Item, Bid, Invoice, Payment
from django.db import connection
from django.db.models import Sum


#Bid utils

def getNoBidItems():
	auctionId = 1
	#todo auctionid
	return list(Item.objects.raw('SELECT * from audio_item where id not in (select item_id from audio_bid)'))

def resetWinners():
	return Bid.objects.filter(auction_id = 1).update(winner=False)

def getBidItems():
	return Bid.objects.values('item').distinct()

def getWinners():
	#todo auction id
	auctionId = 1
	winners = Bid.objects.filter(winner = True, auction_id = auctionId)
	return winners

def getWinBidsByUser(userId):
	auctionId = 1
	return Bid.objects.filter(auction_id = auctionId, user_id = userId, winner = True)

def getLosers():
	#add auctoinId
	auctionId = 1
	return list(Bid.objects.raw('SELECT * FROM audio_bid group by user_id '+
							'HAVING COUNT(CASE WHEN winner=1 THEN 1 ELSE NULL END) <1'))

def getMaxBids():
	#tooo auction id
	return list(Bid.objects.raw('select * from audio_bid where id in (select a.id from(select yt.id, yt.date, yt.item_id,  yt.amount from audio_bid yt inner join( select id, max(amount) amount,item_id  from audio_bid group by item_id ) ss on yt.item_id= ss.item_id and yt.amount = ss.amount order by date) as a group by item_id)'))

def getSumWinners():
	winners = getWinners()
	if len(winners) > 0:
		return winners.aggregate(Sum('amount'))["amount__sum"] 
	else:
		return 0

def getDuplicateItems():
	auctionId = 1
	return Item.objects.filter(quantity__gte=2)

def getTopDupeBids(itemId, quantity):
	#tooo auction id
	auctionId = 1
	return list(Bid.objects.raw('select *  from audio_bid  where auction_id='+str(auctionId)+' and item_id = '+str(itemId)+
		'  order by amount desc limit ' + str(quantity)))

def getDuplicateTopBids():
	return ""

def getCosignedWinners():
	auctionId = 1
	return list(Bid.objects.raw('select * from audio_bid b, audio_consignment c where b.winner = true and b.item_id = c.item_id;'))

def getConsignedItemsByConsignor():
	return "select * from audio_item b, audio_consignment c where b.id = c.item_id;"

#--------------------------


def getUnbalancedUsers():
	auctionId = 1
	cursor = connection.cursor()
	cursor.execute("select user_id, coalesce(payments,0) as payments, invoiced, invoiced - coalesce(payments,0) as balance "+
		"from(select sum(amount) as payments, it.user_id, invoiced from audio_payment p "+
		"right join (select sum(invoiced_amount) as invoiced, user_id from audio_invoice group by user_id) "+
		"as it on it.user_id = p.user_id group by user_id) as joined "+
		"where joined.payments != joined.invoiced or joined.payments is NULL")
	row = dictfetchall(cursor)
	return row



def getAlphaWinners():
	auctionId = 1
	cursor = connection.cursor()
	cursor.execute("SELECT distinct au.id, au.last_name, au.first_name, a.zipcode from audio_bid b, audio_address a, auth_user au "+
		"WHERE b.winner = true and b.user_id = a.user_id and au.id = a.user_id and b.auction_id = "+str(auctionId)+" order by last_name")
	row = dictfetchall(cursor)
	return row



def getInvoicesByAuction():
	auctionId = 1
	return Invoice.objects.filter(auction_id = auctionId)
	
def getTotalInvoiceAmountByAuction():
	invoices = getInvoicesByAuction()
	if len(invoices) > 0:
		return invoices.aggregate(Sum('invoiced_amount'))["invoiced_amount__sum"] 
	else:
		return 0

def getInvoiceInfoByUser(userId):
	invoices = Invoice.objects.filter(user_id = userId)
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