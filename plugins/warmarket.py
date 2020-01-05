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

@commands.registerEventHandler(name="getitems")
async def fetchItemInfo(triggerMessage):
    itemData = {}
    
    itemRequest = requests.get('https://api.warframe.market/v1/items')

    if itemRequest.status_code != 200:
        await triggerMessage.channel.send( "Item list request error, aborting item search")
        return

    items = [x for x in itemRequest.json()['payload']['items'] if 'prime' in x['url_name'] and 'primed' not in x['url_name']]
    
    await triggerMessage.channel.send( "Beginning item data download with " + str(len(items)) + " items")
    progressMessage = await triggerMessage.channel.send( "Progress: 0%")
    nextEdit = 5
    for index,item in enumerate(items):
        itemInfoRequest = requests.get('https://api.warframe.market/v1/items/'+item['url_name'])
        if itemInfoRequest.status_code != 200:
            await triggerMessage.channel.send( "Item info request error, aborting further item search")
            break
        
        itemInfo = itemInfoRequest.json()['payload']['item']
        ducats = 0
        if 'set' not in item['url_name']:
            for setItem in itemInfo['items_in_set']:
                if 'ducats' in setItem and setItem['id'] == itemInfo['id']:
                    ducats = setItem['ducats']
        else:
            ducats = 0
            for setItem in itemInfo['items_in_set']:
                if 'ducats' in setItem:
                    ducats += setItem['ducats']
        
        itemData[item['url_name']] = {'name' : item['item_name'], 'ducats' : ducats}
        if nextEdit > index:
            await progressMessage.edit(content="Progress: {:0.2f}%".format(100.0*index/len(items)))
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
                await triggerMessage.channel.send( "Got {} warframe items".format(len(itemData)))
onlineGPrimeOffers = []

@commands.registerEventHandler(triggerType="\\timeTick", name="cheapGalatine")
async def checkGalatine():
    if datetime.now(tz).second == 0 and datetime.now(tz).minute % 10 == 0:
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
            await client.get_channel(431299254418669570).send(outString)
        
        #print(onlineGPrimeOffers)
        
@commands.registerEventHandler(name="ducks")
async def getDuckListings(triggerMessage):
    itemsToBuy = []
    items = None
    
    with open('WarframePotentialDucks.json', 'r') as itemfile:
        items = json.loads(itemfile.read())
    
    #interestingItems = {k: v for k, v in items.items() if v['best'] > 8}
    interestingItems = items
    await triggerMessage.channel.send( "Searching through " + str(len(interestingItems)) + " interesting items")
    progressMessage = await triggerMessage.channel.send( "Progress: 0%")
    
    for index, item in enumerate(interestingItems):
        startTime = time.time()
        ducats = interestingItems[item]['ducats']
                    
        itemOrdersRequest = requests.get('https://api.warframe.market/v1/items/'+item+'/orders')
        
        if itemOrdersRequest.status_code != 200:
            await triggerMessage.channel.send( "Item orders request error, aborting further ducat search")
            break
            
        itemOrders = itemOrdersRequest.json()['payload']['orders']
        
        prices = []
        for order in itemOrders:
            if order['order_type'] == 'sell' and order['user']['status'] == 'online' and order['platform'] == 'pc' and order['region'] == 'en':
                prices.append(order['platinum'])
                
        prices.sort()
        if len(prices) > 0:
            if ducats/prices[0] > 8:
                itemsToBuy.append((interestingItems[item]['name'],ducats,ducats/prices[0],ducats/prices[int(len(prices)/2)]))
        
            items[item] = {'name' : items[item]['name'], 'best' : ducats/prices[0], 'median' : ducats/prices[int(len(prices)/2)], 'ducats' : items[item]['ducats']}
        
        await progressMessage.edit(content="Progress: {:0.2f}%".format(100.0*index/len(interestingItems)))
        if (time.time() - startTime) < 0.33:
            await asyncio.sleep(0.34 - (time.time() - startTime))
            print("Waiting an extra " + str(time.time() - startTime))
    await progressMessage.edit(content="Progress: Done!")
    
    itemsToBuy.sort(key=lambda tup: tup[2], reverse=True)
    results = "Top 10 items to buy for ducats:\n"
    for item in itertools.islice(itemsToBuy, 0, 10):
        results += ("{} : {} ducats, best: {:0.2f} dc/pl, median: {:0.2f} dc/pl\n".format(item[0],item[1],item[2],item[3]))
    
    await triggerMessage.channel.send( results)
    
    try:
        json.dumps(items, indent=4)
    except:
        raise
    else:
        if len(itemsToBuy) > 0:
            with open('WarframePotentialDucks.json', 'w') as datafile:
                datafile.write(json.dumps(items, indent=4))