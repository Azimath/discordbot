import asyncio
import discord
import commands

import requests
import time

import itertools

client = None

"""This is a plugin for dominating the warframe market for fun and plat"""

@commands.registerEventHander(name="ducks")
async def getDuckListings(triggerMessage):
    itemRequest = requests.get('https://api.warframe.market/v1/items')

    if itemRequest.status_code != 200:
        await client.send_message(triggerMessage.channel, "Item request error, aborting ducat search")
        return
        
    count = 0
    itemsToBuy = []
    items = [i for i in itemRequest.json()['payload']['items']['en'] if 'prime' in i['url_name'] and 'primed' not in i['url_name']]
    
    await client.send_message(triggerMessage.channel, "Beginning ducat search with " + str(len(items)) + " items")
    progressMessage = await client.send_message(triggerMessage.channel, "Progress: 0%")
    
    lastProgressUpdate = 0
    
    for index, item in enumerate(items):
        itemInfoRequest = requests.get('https://api.warframe.market/v1/items/'+item['url_name'])
        if itemInfoRequest.status_code != 200:
            await client.send_message(triggerMessage.channel, "Item info request error, aborting further ducat search")
            break
        
        itemInfo = itemInfoRequest.json()['payload']['item']
        
        ducats = 0
        if 'set' not in item['url_name']:
            for setItem in itemInfo['items_in_set']:
                if 'ducats' in setItem and setItem['_id'] == itemInfo['_id']:
                    ducats = setItem['ducats']
        else:
            for setItem in itemInfo['items_in_set']:
                if 'ducats' in setItem:
                    ducats += setItem['ducats']
                    
        itemOrdersRequest = requests.get('https://api.warframe.market/v1/items/'+item['url_name']+'/orders')
        
        if itemOrdersRequest.status_code != 200:
            await client.send_message(triggerMessage.channel, "Item orders request error, aborting further ducat search")
            break
            
        itemOrders = itemOrdersRequest.json()['payload']['orders']
        
        prices = []
        for order in itemOrders:
            if order['order_type'] == 'sell' and order['user']['status'] == 'online' and order['platform'] == 'pc':
                prices.append(order['platinum'])
                
        prices.sort()
        
        if len(prices) > 0:
            if ducats/prices[0] > 8:
                #print(item['item_name'] + " : " + str(ducats) + " ducats, best: " + str(ducats/prices[0]) + " ducats per plat, median: " + str(ducats/prices[int(len(prices)/2)]) + " ducats per plat")
                itemsToBuy.append((item['item_name'],ducats,ducats/prices[0],ducats/prices[int(len(prices)/2)]))
        
        if index > lastProgressUpdate+5:
            await client.edit_message(progressMessage, "Progress: {:0.2f}%".format(100.0*index/len(items)))
            lastProgressUpdate = index
            
        time.sleep(0.67)
    
    await client.edit_message(progressMessage, "Progress: complete!")
    
    itemsToBuy.sort(key=lambda tup: (tup[2],tup[3]), reverse=True)
    results = triggerMessage.author.mention + "\nTop 5 items to buy for ducats:\n"
    for item in itertools.islice(itemsToBuy, 0, 5):
        results += ("{} : {:0.2f} ducats, best: {:0.2f} dc/pl, median: {:0.2f} dc/pl\n".format(item[0],item[1],item[2],item[3]))
        
    await client.send_message(triggerMessage.channel, results)
    