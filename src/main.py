#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests, json
import os
import logging
from datetime import timedelta
import translate
import random
import praw


REDDIT_BOT_ID = os.environ['REDDIT_BOT_ID']
REDDIT_BOT_SECRET = os.environ['REDDIT_BOT_SECRET']
REDDIT_USER_AGENT = os.environ['REDDIT_USER_AGENT']


class NotifyUserException(Exception):
    """Raised whenever an error needs to be propagated to the user"""
    pass


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Reichenbach is never an option!")


def echoText(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


def echoSticker(update, context):
    sticker = update.message.sticker
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker=sticker)


def mensa(update, context):
    params = context.args
    if len(params) < 1:
        daysToAdd = 0
    else:
        try:
            daysToAdd = int(params[0])
        except ValueError:
            context.bot.send_message(chat_id=update.message.chat_id, text="The first and only parameter has to be an integer value. Aborting.")
            return
    day = update.message.date.date() + timedelta(days=daysToAdd)
    url = "https://openmensa.org/api/v2/canteens/79/days/" + day.strftime("%Y-%m-%d") + "/meals"
    resp = requests.get(url)
    if not resp.ok:
        context.bot.send_message(chat_id=update.message.chat_id, text="I failed miserably. Disgrace!")
        return
    jsonData = json.loads(resp.content)
    for elem in jsonData:
        context.bot.send_message(chat_id=update.message.chat_id, text=elem["name"])


def andre(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Höhöhö Reichenbach!")


def leon(update, context):
    joke = dadJoke()
    context.bot.send_message(chat_id=update.message.chat_id, text=joke)


def loen(update, context):
    joke = dadJoke()
    translator = translate.Translator(from_lang='en', to_lang='de')
    translatedJoke = translator.translate(joke)
    context.bot.send_message(chat_id=update.message.chat_id, text=translatedJoke)


def dadJoke():
    headers = {'Accept': 'text/plain '}
    resp = requests.get("https://icanhazdadjoke.com/", headers=headers)
    if not resp.ok:
        return "I failed miserably. Disgrace!"
    return resp.text


def georg(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="https://wiki.archlinux.org/index.php/Installation_guide")


def maxime(update, context):
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker="CAADBQADfAMAAukKyAPfAAFRgAuYdNoWBA")


def andrey(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="11.00 Bois. Yeef!")


def getXkcd(id, rand):
    resp = requests.get("https://xkcd.com/info.0.json")
    if not resp.ok:
        raise NotifyUserException("I failed miserably. Disgrace!")
    jsonData = json.loads(resp.content)
    upperLimit = jsonData["num"]

    if rand:
        id = random.randint(1, upperLimit)
    elif id > upperLimit:
        raise NotifyUserException("Id not in range. Maximum id currently is " + str(upperLimit) + ".")

    resp = requests.get("https://xkcd.com/" + str(id) + "/info.0.json")
    if not resp.ok:
        raise NotifyUserException("I failed miserably. Disgrace!")

    jsonData = json.loads(resp.content)
    return (id, jsonData["img"], jsonData["title"])


def xkcd(update, context):
    params = context.args
    rand = False
    id = 0
    if len(params) < 1:
        rand = True
    else:
        try:
            id = int(params[0])
        except ValueError:
            context.bot.send_message(chat_id=update.message.chat_id, text="The first and only parameter has to be a positive integer value greater than 0. Aborting.")
            return
        if id < 1:
            context.bot.send_message(chat_id=update.message.chat_id, text="The first and only parameter has to be a positive integer value greater than 0. Aborting.")
            return
    try:
        xkcd = getXkcd(id, rand)
    except NotifyUserException as error:
        context.bot.send_message(chat_id=update.message.chat_id, text=str(error))
        return
    context.bot.send_photo(chat_id=update.message.chat_id, photo=xkcd[1], caption=str(xkcd[0]) + " - " + xkcd[2])


def subredditImg(subreddit, offset):

    imageFileEndings = [".png", ".jpg", ".jpeg", ".webp"]

    reddit = praw.Reddit(client_id=REDDIT_BOT_ID, client_secret=REDDIT_BOT_SECRET, user_agent=REDDIT_USER_AGENT)

    images = []

    for post in reddit.subreddit(subreddit).hot(limit=5):
        for ending in imageFileEndings:
            if str(post.url).endswith(ending):
                images.append(post.url)
    return images


def r(update, context):
    params = context.args
    offset = 0
    if len(params) < 1:
        context.bot.send_message(chat_id=update.message.chat_id, text="The first parameter has to be a string identifying the requested subreddit. Aborting.")
        return
    subreddit = params[0]
    if len(params) > 1:
        try:
            offset = int(params[1])
        except ValueError:
            context.bot.send_message(chat_id=update.message.chat_id, text="The second parameter has to be a positive integer value. Aborting.")
            return
        if offset < 0:
            context.bot.send_message(chat_id=update.message.chat_id, text="The second parameter has to be a positive integer value. Aborting.")
            return

    try:
        images = subredditImg(subreddit, offset)
    except Exception:
        context.bot.send_message(chat_id=update.message.chat_id, text="Something went wrong internally. I am deeply sorry.")
        return

    if len(images) == 0:
        context.bot.send_message(chat_id=update.message.chat_id, text="There are no images in the top 5 posts.")
        return
    for image in images:
        context.bot.send_photo(chat_id=update.message.chat_id, photo=image)


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    API_TOKEN = os.environ['TELEGRAM_APITOKEN']
    APP_ADDR = os.environ['APP_ADDRESS']
    PORT = int(os.environ.get('PORT', '8443'))

    updater = Updater(token=API_TOKEN, use_context=True)

    startHandler = CommandHandler('start', start)
    updater.dispatcher.add_handler(startHandler)

    mensaHandler = CommandHandler('mensa', mensa)
    updater.dispatcher.add_handler(mensaHandler)

    andreHandler = CommandHandler('andre', andre)
    updater.dispatcher.add_handler(andreHandler)

    leonHandler = CommandHandler('leon', leon)
    updater.dispatcher.add_handler(leonHandler)

    georgHandler = CommandHandler('georg', georg)
    updater.dispatcher.add_handler(georgHandler)

    loenHandler = CommandHandler('loen', loen)
    updater.dispatcher.add_handler(loenHandler)

    maximeHandler = CommandHandler('maxime', maxime)
    updater.dispatcher.add_handler(maximeHandler)

    andreyHandler = CommandHandler('andrey', andrey)
    updater.dispatcher.add_handler(andreyHandler)

    xkcdHandler = CommandHandler('xkcd', xkcd)
    updater.dispatcher.add_handler(xkcdHandler)

    redditImgHandler = CommandHandler('r', r)
    updater.dispatcher.add_handler(redditImgHandler)

    echoHandlerText = MessageHandler(Filters.text, echoText)
    updater.dispatcher.add_handler(echoHandlerText)

    echoHandlerSticker = MessageHandler(Filters.sticker, echoSticker)
    updater.dispatcher.add_handler(echoHandlerSticker)

    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=API_TOKEN)
    updater.bot.set_webhook(APP_ADDR + API_TOKEN)
    updater.idle()


if __name__ == "__main__":
    main()
