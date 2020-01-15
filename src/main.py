#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests, json
import os
import logging
from datetime import timedelta
import translate
import random


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

def decision(update, context):
    headers = {'Accept': 'text/plain '}
    resp = requests.get("https://yesno.wtf/api/", headers=headers)
    if not resp.ok:
        raise NotifyUserException("oof")
    data = json.loads(resp.text)

    return data["answer"]

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

    loenHandler = CommandHandler('loen', loen)
    updater.dispatcher.add_handler(loenHandler)

    maximeHandler = CommandHandler('maxime', maxime)
    updater.dispatcher.add_handler(maximeHandler)

    andreyHandler = CommandHandler('andrey', andrey)
    updater.dispatcher.add_handler(andreyHandler)

    xkcdHandler = CommandHandler('xkcd', xkcd)
    updater.dispatcher.add_handler(xkcdHandler)

    decisionHandler = CommandHandler('decision', decision)
    updater.dispatcher.add_handler(decisionHandler)

    echoHandlerText = MessageHandler(Filters.text, echoText)
    updater.dispatcher.add_handler(echoHandlerText)

    echoHandlerSticker = MessageHandler(Filters.sticker, echoSticker)
    updater.dispatcher.add_handler(echoHandlerSticker)

    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=API_TOKEN)
    updater.bot.set_webhook(APP_ADDR + API_TOKEN)
    updater.idle()


if __name__ == "__main__":
    main()
