import asyncio
import discord
import commands

import requests
from datetime import datetime, timedelta
import tzlocal
import time

import itertools
import json

client = None

"""This is a plugin for dominating the warframe market for fun and plat"""

tz=tzlocal.get_localzone()

@commands.registerEventHander(name="getitems")
async def fetchItemInfo(triggerMessage):
    itemData = {}
    
    itemRequest = requests.get('https://api.warframe.market/v1/items')

    if itemRequest.status_code != 200:
        await client.send_message(triggerMessage.channel, "Item list request error, aborting item search")
        return
        
    items = [x for x in itemRequest.json()['payload']['items']['en'] if 'prime' in x['url_name'] and 'primed' not in x['url_name']]
    
    await client.send_message(triggerMessage.channel, "Beginning item data download with " + str(len(items)) + " items")
    progressMessage = await client.send_message(triggerMessage.channel, "Progress: 0%")
    nextEdit = 5
    for index,item in enumerate(items):
        itemInfoRequest = requests.get('https://api.warframe.market/v1/items/'+item['url_name'])
        if itemInfoRequest.status_code != 200:
            await client.send_message(triggerMessage.channel, "Item info request error, aborting further item search")
            break
        
        itemInfo = itemInfoRequest.json()['payload']['item']
        
        ducats = 0
        if 'set' not in item['url_name']:
            for setItem in itemInfo['items_in_set']:
                if 'ducats' in setItem and setItem['_id'] == itemInfo['_id']:
                    ducats = setItem['ducats']
        else:
            ducats = 0
            for setItem in itemInfo['items_in_set']:
                if 'ducats' in setItem:
                    ducats += setItem['ducats']
        
        itemData[item['url_name']] = {'name' : item['item_name'], 'ducats' : ducats}
        if nextEdit > index:
            await client.edit_message(progressMessage, "Progress: {:0.2f}%".format(100.0*index/len(items)))
            nextEdit = index + 5
            
        await asyncio.sleep(0.334)
        
    try:
        json.dumps(itemData, indent=4)
    except:
        raise
    else:
        if len(itemData) > 0:
            with open('WarframeItems.json', 'w') as datafile:
                datafile.write(json.dumps(itemData, indent=4, sort_keys=True))
                await client.send_message(triggerMessage.channel, "Got {} warframe items".format(len(itemData)))
onlineGPrimeOffers = []

@commands.registerEventHander(triggerType="\\timeTick", name="cheapGalatine")
async def checkGalatine():
    if datetime.now(tz).second == 0:
        itemRequest = requests.get('https://api.warframe.market/v1/items/galatine_prime_set/orders')

        if itemRequest.status_code != 200:
            return
            
        outString = ''
        for offer in itemRequest.json()['payload']['orders']:
            if offer['region'] =='en' and offer['order_type'] == 'sell' and offer['platform'] == 'pc' and offer['platinum'] <= 20:
                if offer['user']['status'] != 'offline' and not offer['user']['id'] in onlineGPrimeOffers:
                    outString += "/w {} Hi! I want to buy: Galatine Prime Set for {} platinum. (warframe.market)\n".format(offer['user']['ingame_name'], offer['platinum'])
                    onlineGPrimeOffers.append(offer['user']['id'])
                elif offer['user']['id'] in onlineGPrimeOffers and offer['user']['status'] == 'offline':
                    onlineGPrimeOffers.remove(offer['user']['id'])
        if len(outString) > 0:            
            await client.send_message(discord.Object('431299254418669570'), outString)
        
        #print(onlineGPrimeOffers)

nextTime = datetime.now(tz)

@commands.registerEventHander(triggerType="\\timeTick", name="duckhunt")
async def passiveDuckSearch():
    global nextTime
    if datetime.now(tz) < nextTime:
        return
    
    nextTime = datetime.now(tz)
    nextTime += timedelta(days=1)
    nextTime.replace(hour = 1, minute = 0, second = 0)
    
    print("Updating market overall data")
    
    itemsToBuy = {}
    items = None
    
    with open('WarframeItems.json', 'r') as itemfile:
        items = json.loads(itemfile.read())
    
    #await client.send_message(triggerMessage.channel, "Beginning ducat search with " + str(len(items)) + " items")
    #progressMessage = await client.send_message(triggerMessage.channel, "Progress: 0%")
    nextEdit = 20
    for index, item in enumerate(items):
        ducats = items[item]['ducats']
                    
        itemOrdersRequest = requests.get('https://api.warframe.market/v1/items/'+item+'/orders')
        
        if itemOrdersRequest.status_code != 200:
            #await client.send_message(triggerMessage.channel, "Item orders request error, aborting further ducat search")
            break
            
        itemOrders = itemOrdersRequest.json()['payload']['orders']
        
        prices = []
        for order in itemOrders:
            if order['order_type'] == 'sell' and order['user']['status'] == 'online' and order['platform'] == 'pc':
                prices.append(order['platinum'])
                
        prices.sort()
        if len(prices) > 0:
            itemsToBuy[item] = {'name' : items[item]['name'], 'best' : ducats/prices[0], 'median' : ducats/prices[int(len(prices)/2)]}
            
        if index > nextEdit:
            print("Passive update progress: {:0.2f}%".format(100.0*index/len(items)))
            nextEdit = index + 20
        await asyncio.sleep(0.334)
    
    try:
        json.dumps(itemsToBuy, indent=4)
    except:
        raise
    else:
        if len(itemsToBuy) > 0:
            with open('WarframePotentialDucks.json', 'w') as datafile:
                datafile.write(json.dumps(itemsToBuy, indent=4))
        
@commands.registerEventHander(name="ducks")
async def getDuckListings(triggerMessage):
    itemsToBuy = []
    items = None
    
    with open('WarframeItems.json', 'r') as itemfile:
        items = json.loads(itemfile.read())
    
    await client.send_message(triggerMessage.channel, "Beginning ducat search with " + str(len(items)) + " items")
    progressMessage = await client.send_message(triggerMessage.channel, "Progress: 0%")
    
    for index, item in enumerate(items):
        ducats = items[item]['ducats']
                    
        itemOrdersRequest = requests.get('https://api.warframe.market/v1/items/'+item+'/orders')
        
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
                itemsToBuy.append((items[item]['name'],ducats/prices[0],ducats/prices[int(len(prices)/2)]))
        
        await client.edit_message(progressMessage, "Progress: {:0.2f}%".format(100.0*index/len(items)))
        await asyncio.sleep(0.334)
    
    itemsToBuy.sort(key=lambda tup: tup[1])
    results = "Top 5 items to buy for ducats:\n"
    for item in itertools.islice(itemsToBuy, 0, 5):
        results += ("{} : {} ducats, best: {:0.2f} dc/pl, median: {:0.2f} dc/pl\n".format(item[0],items[item[0]]['ducats'],item[1],item[2]))
    
    await client.send_message(triggerMessage.channel, results)