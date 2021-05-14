from bs4 import BeautifulSoup
from datetime import datetime
from config import config
import feedparser
import telebot
import json
import os


def get_timestamp(dt):
    return datetime.strptime(dt, '%a, %d %b %Y %H:%M:%S %z').timestamp()


bot = telebot.TeleBot(config.get('token'))

newsFeed = list()

if type(config.get('newsFeed')) == str:
    newsFeed.append(feedparser.parse(config.get('newsFeed')))
else:
    for feed in config.get('newsFeed'):
        newsFeed.append(feedparser.parse(feed))

newPosts = []

if not os.path.exists('news.json'):
    with open('news.json', 'w') as f:
        json.dump([], f)
        f.close()

with open('news.json') as f:
    guids = json.load(f)
    f.close()

for feed in newsFeed:
    for entry in feed.entries:
        content = entry['description']
        post = {}
        soup = BeautifulSoup(content, 'html.parser')
        if soup.img:
            post['image'] = soup.img['src']
        post['text'] = '\n'.join(soup.stripped_strings)
        post['text'] += '\n\n{}'.format(entry['link'])
        post['date'] = get_timestamp(entry['published'])

        if entry['guid'] not in guids:
            newPosts.append(post)
            guids.append(entry['guid'])

newPosts.sort(key=lambda x: x['date'])

for post in newPosts:
    bot.send_message(config.get('channelid'), post.get('text'))

with open('news.json', 'w') as f:
    json.dump(guids, f)
    f.close()
