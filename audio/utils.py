from audio.models import Address, Item, Bid
from django.db import connection


def getNoBidItems():
	return list(Item.objects.raw('SELECT * from audio_item where id not in (select item_id from audio_bid)'))

def getBidItems():
	return Bid.objects.values('item').distinct()

def getWinners():
	#todo auction id
	winners = Bid.objects.filter(winner = True)
	return winners

def getAlphaWinners():
	auctionId = 1
	cursor = connection.cursor()
	cursor.execute("SELECT distinct au.id, au.last_name, au.first_name, a.zipcode from audio_bid b, audio_address a, auth_user au "+
		"WHERE b.winner = true and b.user_id = a.user_id and au.id = a.user_id and b.auction_id = "+str(auctionId)+" order by last_name")
	row = dictfetchall(cursor)
	return row


def getLosers():
	return list(Bid.objects.raw('SELECT * FROM audio_bid group by user_id '+
							'HAVING COUNT(CASE WHEN winner=1 THEN 1 ELSE NULL END) <1'))

def getMaxBids():
	#tooo auction id
	return list(Bid.objects.raw('select yt.* from audio_bid yt inner join( '+
		'select id, max(amount) amount,item_id '+
		'from audio_bid group by item_id ) '+
		'ss on yt.item_id= ss.item_id and yt.amount = ss.amount;'))

def getDuplicateItems():
	return Item.objects.filter(quantity__gte=2)

def getTopDupeBids(itemId, quantity):
	#tooo auction id
	return list(Bid.objects.raw('select *  from audio_bid  where item_id = '+str(itemId)+
		'  order by amount desc limit ' + str(quantity)))

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]