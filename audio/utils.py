from audio.models import Address, Item, Bid


def getNoBidItems():
	return Item.objects.raw('SELECT * from audio_item where id not in (select item_id from audio_bid)')

def getBidItems():
	return Bid.objects.values('item').distinct()

def getWinners():
	#todo auction id
	winners = Bid.objects.filter(winner = True)
	return winners

def getLosers():
	return Bid.objects.raw('SELECT * FROM audio_bid group by user_id HAVING COUNT(CASE WHEN winner=1 THEN 1 ELSE NULL END) <1')

def getMaxBids():
	#tooo auction id
	return Bid.objects.raw('SELECT tt.* FROM audio_bid tt INNER JOIN'    +
	 '(SELECT item_id, MAX(amount) AS MaxDateTime ' +
	 	'FROM audio_bid   where auction_id =1  GROUP BY item_id) groupedtt' +
	'  ON tt.item_id = groupedtt.item_id  AND tt.amount = groupedtt.MaxDateTime')