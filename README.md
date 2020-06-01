
# Unofficial TikTok API in Python

[mmakeev]: It's fork with fully async support


## Important Information
* If this API stops working for any reason open an issue.

## Getting Started

To get started using this api follow the instructions below.

### Installing

If you need help installing or run into some error, please open an issue. I will try to help out as much as I can.

```
pip install TikTokApi
pyppeteer-install
```

## Quick Start Guide

Here's a quick bit of code to get the most recent trending on TikTok. There's more example in the examples directory.


```
from TikTokApi import TikTokApi
async with aiohttp.ClientSession() as session:
    api =  TikTokApi(session)
    videos = await api.byUsername(username, count=9)
    print(json.dumps(videos, indent=2))
```
