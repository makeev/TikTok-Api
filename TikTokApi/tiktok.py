import aiohttp
import asyncio
import pyppeteer
import random
import requests
from .browser import browser
from bs4 import BeautifulSoup
import time
import json
from selenium import webdriver


class TikTokApi:
    #
    # The TikTokapi class constructor
    #
    def __init__(self, aiohttp_session, debug=False, executable_path=None):
        if debug:
            print("Class initialized")

        self.referrer = "https://www.tiktok.com/tag/jakefromstate?lang=en"
        self.session = aiohttp_session
        self.executable_path = executable_path  # headless-chromium executable

    def init_browser(self, url):
        return browser(url, executable_path=self.executable_path)

    #
    # Method that retrives data from the api
    #
    async def getData(self, api_url, signature, userAgent):
        url = api_url + \
            "&_signature=" + signature
        r = await self.session.get(url, headers={
            "method": "GET",
            "accept-encoding": "gzip, deflate, br",
            "referrer": self.referrer,
            "user-agent": userAgent,
        })

        try:
            return await r.json()
        except:
            print("Converting response to JSON failed response is below (probably empty)")
            text = await r.text()
            print(text)
            raise Exception('Invalid Response')


    #
    # Method that retrives data from the api
    #

    async def getBytes(self, api_url, signature, userAgent):
        url = api_url + \
            "&_signature=" + signature
        r = await self.session.get(url, headers={
            "method": "GET",
            "accept-encoding": "gzip, deflate, br",
            "referrer": self.referrer,
            "user-agent": userAgent,
        })
        return await r.read()

    #
    # Gets trending Tiktoks
    #

    async def trending(self, count=30):
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            api_url = "https://m.tiktok.com/api/item_list/?count={}&id=1&type=5&secUid=&maxCursor={}&minCursor=0&sourceType=12&appId=1233&verifyFp=".format(
            str(realCount), str(maxCursor))
            b = self.init_browser(api_url)
            await b.start()
            res = await self.getData(api_url, b.signature, b.userAgent)

            for t in res['items']:
                response.append(t)

            if not res['hasMore']:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count-len(response)
            maxCursor = res['maxCursor']


        return response[:count]

    #
    # Gets a specific user's tiktoks
    #
    async def userPosts(self, userID, secUID, count=30):
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            api_url = "https://m.tiktok.com/api/item_list/?count={}&id={}&type=1&secUid={}&maxCursor={}&minCursor=0&sourceType=8&appId=1233&region=US&language=en&verifyFp=".format(
            str(realCount), str(userID), str(secUID), str(maxCursor))
            b = self.init_browser(api_url)
            await b.start()
            res = await self.getData(api_url, b.signature, b.userAgent)

            for t in res['items']:
                response.append(t)

            if not res['hasMore']:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count-len(response)
            maxCursor = res['maxCursor']


        return response[:count]

    #
    # Gets a specific user's tiktoks by username
    #

    async def byUsername(self, username, count=30):
        data = await self.getUserObject(username)
        return await self.userPosts(data['id'], data['secUid'], count=count)

    #
    # Gets tiktoks by music ID
    #
    # id - the sound ID
    #

    async def bySound(self, id, count=30):
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            api_url = "https://m.tiktok.com/share/item/list?secUid=&id={}&type=4&count={}&minCursor=0&maxCursor={}&shareUid=&lang=en&verifyFp=".format(
            str(id), str(realCount), str(maxCursor))
            b = self.init_browser(api_url)
            res = await self.getData(api_url, b.signature, b.userAgent)

            for t in res['body']['itemListData']:
                response.append(t)

            if not res['body']['hasMore']:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count-len(response)
            maxCursor = res['body']['maxCursor']

        return response[:count]

    #
    # Gets the music object
    #
    async def getMusicObject(self, id):
        api_url = "https://m.tiktok.com/api/music/detail/?musicId={}&language=en&verifyFp=".format(
            str(id))
        b = self.init_browser(api_url)
        await b.start()
        return await self.getData(api_url, b.signature, b.userAgent)

    #
    # Gets tiktoks by hashtag
    #

    async def byHashtag(self, hashtag, count=30):
        id = self.getHashtagObject(hashtag)['challengeInfo']['challenge']['id']
        response = []
        maxCount = 99
        maxCursor = 0

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            api_url = "https://m.tiktok.com/share/item/list?secUid=&id={}&type=3&count={}&minCursor=0&maxCursor={}&shareUid=&lang=en&verifyFp=".format(
                str(id), str(realCount), str(maxCursor))
            b = self.init_browser(api_url)
            res = await self.getData(api_url, b.signature, b.userAgent)

            for t in res['body']['itemListData']:
                response.append(t)

            if not res['body']['hasMore']:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count-len(response)
            maxCursor = res['body']['maxCursor']

        return response[:count]

    #
    # Gets tiktoks by hashtag (for use in byHashtag)
    #

    async def getHashtagObject(self, hashtag):
        api_url = "https://m.tiktok.com/api/challenge/detail/?verifyFP=&challengeName={}&language=en".format(
            str(hashtag))
        b = self.init_browser(api_url)
        await b.start()
        return await self.getData(api_url, b.signature, b.userAgent)

    #
    # Discover page, consists challenges (hashtags)
    #

    async def discoverHashtags(self):
        api_url = "https://m.tiktok.com/node/share/discover?noUser=1&userCount=30&scene=0&verifyFp="
        b = self.init_browser(api_url)
        await b.start()
        data = await self.getData(api_url, b.signature, b.userAgent)
        return data['body'][1]['exploreList']

    #
    # Discover page, consists of music
    #

    async def discoverMusic(self):
        api_url = "https://m.tiktok.com/node/share/discover?noUser=1&userCount=30&scene=0&verifyFp="
        b = self.init_browser(api_url)
        await b.start()
        data = await self.getData(api_url, b.signature, b.userAgent)
        return data['body'][2]['exploreList']
    #
    # Gets a user object for id and secUid
    #

    async def getUserObject(self, username):
        api_url = "https://m.tiktok.com/api/user/detail/?uniqueId={}&language=en&verifyFp=".format(
            username)
        b = self.init_browser(api_url)
        await b.start()
        data = await self.getData(api_url, b.signature, b.userAgent)
        return data['userInfo']['user']

    #
    # Downloads video from TikTok using a TikTok object
    #

    async def get_Video_By_TikTok(self, data):
        api_url = data['video']['downloadAddr']
        return await self.get_Video_By_DownloadURL(api_url)

    #
    # Downloads video from TikTok using download url in a tiktok object
    #
    async def get_Video_By_DownloadURL(self, download_url):
        b = self.init_browser(download_url)
        await b.start()
        return await self.getBytes(download_url, b.signature, b.userAgent)

    #
    # Gets the source url of a given url for a tiktok
    #
    # video_url - the url of the video
    # return_bytes - 0 is just the url, 1 is the actual video bytes
    # chromedriver_path - path to your chrome driver executible
    #

    async def get_Video_By_Url(self, video_url, return_bytes=0, chromedriver_path=None):
        if chromedriver_path != None:
            driver = webdriver.Chrome(executable_path=chromedriver_path)
        else:
            driver = webdriver.Chrome()
        driver.get(video_url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        data = json.loads(soup.find_all(
            'script', attrs={"id": "videoObject"})[0].text)

        if return_bytes == 0:
            return data['contentUrl']
        else:
            r = await self.session.get(data['contentUrl'])
            return await r.read()
