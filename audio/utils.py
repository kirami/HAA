from audio.models import Address, Item, Bid


def getNoBidItems():
	return list(Item.objects.raw('SELECT * from audio_item where id not in (select item_id from audio_bid)'))

def getBidItems():
	return Bid.objects.values('item').distinct()

def getWinners():
	#todo auction id
	winners = Bid.objects.filter(winner = True)
	return winners

def getLosers():
	return list(Bid.objects.raw('SELECT * FROM audio_bid group by user_id '+
							'HAVING COUNT(CASE WHEN winner=1 THEN 1 ELSE NULL END) <1'))

def getMaxBids():
	#tooo auction id
	return list(Bid.objects.raw('select yt.* from audio_bid yt inner join( '+
		'select id, max(amount) amount,item_id '+
		'from audio_bid group by item_id ) '+
		'ss on yt.item_id= ss.item_id and yt.amount = ss.amount;'))