#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from telegram.ext import Application, CommandHandler, InlineQueryHandler, ContextTypes
from telegram import Update
import telegram as tg
import requests
import json
import os
import io
import logging
from datetime import timedelta
from deep_translator import GoogleTranslator
import random
import asyncpraw
import sys
import enum
import inspirobot

REDDIT_BOT_ID = ''
REDDIT_BOT_SECRET = ''
REDDIT_USER_AGENT = ''
USER_AGENT_BROWSER = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'

REDDIT_IMAGE_FILE_ENDINGS = [".png", ".jpg", ".jpeg", ".webp"]
REDDIT_VIDEO_SITES = ["youtu.be", "youtube.com", "v.redd.it"]
REDDIT_ANIMATION_FILE_ENDINGS = [".gif"]
REDDIT_EXCLUDED_ANIMATION_SITES = ["imgur.com", "giphy.com"]


class RedditPostTypes(enum.Enum):
    text = 1
    image = 2
    animation = 3
    video = 4
    undefined = 5


royal_titles = ["Lé", "Baron", "König", "Archlord", "Genius", "Ritter", "Curry", "Burger", "Mc", "Doktor", "Gentoomaster", "Chef", "Lead Developer", "Sensei"]
first_frag = ["Schm", "J", "Hans-J", "K", "G", "Gr", "B", "Str", "Kr", "Rask", "Sch"]
second_frag = ["oerg", "öck", "öhhhrk", "öhrp", "egor", "oeg", "ock", "uck", "orsch"]
third_frag = ["inger", "erino", "aroni", "us", "sell", "topus", "thulu", "tain", "rid", "odil", "ette", "nikov", "inus", "iborschi"]
noble_annex = ["I.", "II.", "III.", "Royale", "dem Allmächtigen", "dem Weisen", "dem hochgradig Intelligenten", "dem Unendlichen", "dem Allwissenden", "dem Gentoobändiger", "dem Meisterinformatiker", "dem Meisterkoch", "dem Hardwareexperten", "dem Fahrradspitzensportler", "dem Besonnenen", "dem Ausdauernden"]

wisdoms = ["Linux ist voll doof!", "Ich stehe immer um 7.00 Uhr auf!", "Tut schön viel Frischkäse in die Nudelsoße!", "Mensen um 11.00 Uhr ist eine super Sache!", "Ich habe WinRar gekauft!", "Für einen längeren XP-Supportzeitraum!", "Fasst meinen Laptopbildschirm an!", "Natürlich code ich dieses Feature für euch, ganz ohne Pull Request!", "Maxime ist ein toller Papa!", "Hirtenkäsepizza ist die beste!", "Sauerkraut ist doch ekelhaft!", "Mein Lieblingsbrowser ist ja der Internet Explorer!", "Rechtschreibfehler in Kommentaren? Voll okay!", "Party? Warum nicht bei mir zu Hause?", "Irgendwas mit dynamisch Parameter injecten!", "Wie war das mit den Speisezeiten?", "Ich kaufe nur bei Nvidia!", "Wer braucht schon Open Source...", "KöckOS? Kommt noch diese Woche raus!", "Die besten Witze sind Deine-Mutter-Witze!", "Mein Lieblings-OS ist iOS!", "Ein Halloumiburger ist eine eigenständige Mahlzeit!", "Ich kaufe mir ein MacBook!", "Ich fange wieder mit Medieninformatik an!", "Ich liebe Ubuntu!", "Verschlüsselung ist doch Unsinn!", "Machen wir alle ne gemeinsame WG auf?", "Es ist voll in Ordnung, wenn ihr kein Arch Linux benutzt!", "Ich höre am liebsten K.I.Z!", "Für Ruhezeiten von 20.00 Uhr bis 5.00 Uhr!", "Ihr seid meine besten Freunde!", "Ich entwickele nur noch unter Windows!", "Ich finde Mangas und Animes toll! Schaut mehr Animes!", "Ich esse heimlich Schnitzel!"]


def load_json_list_file(filename):
    try:
        f = open(filename + ".json", "r")
        json_list = json.load(f)
        f.close()
        return json_list
    except Exception as e:
        logging.exception(e)
        return ["amogus"]


haes = load_json_list_file("haes")
weather = load_json_list_file("weather")


class NotifyUserException(Exception):
    """Raised whenever an error needs to be propagated to the user"""
    pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id, text="Reichenbach is never an option!")


# Get the ID for your mensa from https://api.studentenwerk-dresden.de/openmensa/v2/canteens
async def mensa(update: Update, context: ContextTypes.DEFAULT_TYPE, mensaId):
    params = context.args
    if len(params) < 1:
        days_to_add = 0
    else:
        try:
            days_to_add = int(params[0])
        except ValueError:
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text="The first and only parameter has to be an integer value. Aborting.")
            return
    day = update.message.date.date() + timedelta(days=days_to_add)
    url = "https://api.studentenwerk-dresden.de/openmensa/v2/canteens/" + str(mensaId) + "/days/" + day.strftime(
        "%Y-%m-%d") + "/meals"
    resp = requests.get(url)
    if not resp.ok:
        await context.bot.send_message(chat_id=update.message.chat_id, text="I failed miserably. Disgrace!")
        return
    json_data = resp.json()
    if len(json_data) == 0:
        await context.bot.send_message(chat_id=update.message.chat_id, text="No food today :(")
    for elem in json_data:
        meal_notes = elem["notes"]
        markdown_highlight_char = "_"
        for note in meal_notes:
            if "vegetarisch" in note or "vegan" in note:
                markdown_highlight_char = "*"

        img_url = elem["image"].lstrip("/")  # For some reason, image URLs are prefixed with 2 leading slashes, but no protocol, remove them
        # Do not send placeholder images
        if img_url.endswith("studentenwerk-dresden-lieber-mensen-gehen.jpg"):
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text=markdown_highlight_char + elem["name"] + markdown_highlight_char,
                                           parse_mode="Markdown")
        else:
            await context.bot.send_photo(chat_id=update.message.chat_id, photo=img_url,
                                         caption=markdown_highlight_char + elem["name"] + markdown_highlight_char,
                                         parse_mode="Markdown")


async def alte_mensa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mensa(update, context, 4)


async def zelt_mensa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mensa(update, context, 35)


async def siedepunkt_mensa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mensa(update, context, 9)


async def reichenbach_mensa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mensa(update, context, 6)


async def bio_mensa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mensa(update, context, 29)


async def mensologie_mensa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mensa(update, context, 8)


async def andre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id, text="Höhöhö Reichenbach!")


async def leon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke = dad_joke()
    await context.bot.send_message(chat_id=update.message.chat_id, text=joke)


async def loen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke = dad_joke()
    translated_joke = GoogleTranslator(source='en', target='de').translate(joke)
    await context.bot.send_message(chat_id=update.message.chat_id, text=translated_joke)


def dad_joke():
    headers = {'Accept': 'application/json '}
    resp = requests.get("https://icanhazdadjoke.com/", headers=headers)
    if not resp.ok:
        return "I failed miserably. Disgrace!"
    resp_json = resp.json()
    return resp_json['joke']


async def georg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text="https://wiki.archlinux.org/index.php/Installation_guide")


async def maxime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_sticker(chat_id=update.message.chat_id, sticker="CAADBQADfAMAAukKyAPfAAFRgAuYdNoWBA")


async def andrey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id, text="11.00 Bois. Yeef!")


async def steffuu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id, text=random.choice(haes))


async def wetter(update, context):
    await context.bot.send_message(chat_id=update.message.chat_id, text=random.choice(weather))


async def thomas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker_set = await context.bot.get_sticker_set("jason_funderburker")
    random_sticker = random.choice(sticker_set.stickers)
    await context.bot.send_sticker(chat_id=update.message.chat_id, sticker=random_sticker)


def get_xkcd(xkcd_id, rand):
    resp = requests.get("https://xkcd.com/info.0.json")
    if not resp.ok:
        raise NotifyUserException("I failed miserably. Disgrace!")
    json_data = json.loads(resp.content)
    upper_limit = json_data["num"]

    if rand:
        xkcd_id = random.randint(1, upper_limit)
    elif xkcd_id > upper_limit:
        raise NotifyUserException("Id not in range. Maximum id currently is " + str(upper_limit) + ".")

    resp = requests.get("https://xkcd.com/" + str(xkcd_id) + "/info.0.json")
    if not resp.ok:
        raise NotifyUserException("I failed miserably. Disgrace!")

    json_data = json.loads(resp.content)
    return xkcd_id, json_data["img"], json_data["title"]


async def xkcd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    params = context.args
    rand = False
    xkcd_id = 0
    if len(params) < 1:
        rand = True
    else:
        try:
            xkcd_id = int(params[0])
        except ValueError:
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text="The first and only parameter has to be a positive integer value greater than 0. Aborting.")
            return
        if xkcd_id < 1:
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text="The first and only parameter has to be a positive integer value greater than 0. Aborting.")
            return
    try:
        xkcd_data = get_xkcd(xkcd_id, rand)
    except NotifyUserException as error:
        await context.bot.send_message(chat_id=update.message.chat_id, text=str(error))
        return
    await context.bot.send_photo(chat_id=update.message.chat_id, photo=xkcd_data[1],
                                 caption=str(xkcd_data[0]) + " - " + xkcd_data[2])


async def decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {'Accept': 'text/plain '}
    resp = requests.get("https://yesno.wtf/api/", headers=headers)
    if not resp.ok:
        raise NotifyUserException("oof")
    data = json.loads(resp.text)
    await context.bot.send_animation(chat_id=update.message.chat_id, animation=data["image"], caption=data["answer"])


def get_post_type(post):
    post_type = RedditPostTypes.undefined
    if post.selftext != "":
        post_type = RedditPostTypes.text
    else:
        for ending in REDDIT_IMAGE_FILE_ENDINGS:
            if post.url.endswith(ending):
                post_type = RedditPostTypes.image
                break
        for ending in REDDIT_ANIMATION_FILE_ENDINGS:
            if post.url.endswith(ending):
                post_type = RedditPostTypes.animation
                break
        for video_site in REDDIT_VIDEO_SITES:
            if video_site in post.url:
                post_type = RedditPostTypes.video
                break
    return post_type


async def get_subreddit_images(subreddit, offset=0, count=5):
    images = []
    reddit = asyncpraw.Reddit(client_id=REDDIT_BOT_ID, client_secret=REDDIT_BOT_SECRET, user_agent=REDDIT_USER_AGENT)
    sub = await reddit.subreddit(subreddit)
    async for post in sub.hot(limit=count):
        if get_post_type(post) == RedditPostTypes.image:
            images.append(post.url)
    return images


async def send_subreddit_posts(subreddit, update: Update, context: ContextTypes.DEFAULT_TYPE, offset=0, count=5):
    reddit = asyncpraw.Reddit(client_id=REDDIT_BOT_ID, client_secret=REDDIT_BOT_SECRET, user_agent=REDDIT_USER_AGENT)
    posts_sent = False
    content = await reddit.subreddit(subreddit)
    try:
        async for post in content.hot(limit=count):
            if not post.stickied:
                post_type = get_post_type(post)
                if post_type == RedditPostTypes.text:
                    message = "*" + post.title + "* \n" + post.selftext
                    if len(message) > 1000:
                        message = message[:1000]
                        message = message + "*(...)* [" + post.url + "]"
                    await context.bot.send_message(chat_id=update.message.chat_id, text=message,
                                                   parse_mode=tg.ParseMode.MARKDOWN)
                    posts_sent = True
                elif post_type == RedditPostTypes.image:
                    # The telegram API apparently does not accept progressive JPEGs
                    # If this is the case, skip this post and continue
                    try:
                        await context.bot.send_photo(chat_id=update.message.chat_id, photo=post.url, caption=post.title)
                        posts_sent = True
                    except tg.error.BadRequest:
                        continue
                elif post_type == RedditPostTypes.video:
                    await context.bot.send_message(chat_id=update.message.chat_id, text=post.url)
                    posts_sent = True
                elif post_type == RedditPostTypes.animation:
                    for site in REDDIT_EXCLUDED_ANIMATION_SITES:
                        if site in post.url:
                            pass
                    await context.bot.send_animation(chat_id=update.message.chat_id, animation=post.url,
                                                     caption=post.title)
                    posts_sent = True

    except Exception as ex:
        print(ex)
        await context.bot.send_message(chat_id=update.message.chat_id,
                                       text="Something went wrong internally. I am deeply sorry.")
        return

    if not posts_sent:
        await context.bot.send_message(chat_id=update.message.chat_id, text="No compatible Posts were found.")


async def r(update: Update, context: ContextTypes.DEFAULT_TYPE):
    params = context.args
    offset = 0
    if len(params) < 1:
        await context.bot.send_message(chat_id=update.message.chat_id,
                                       text="The first parameter has to be a string identifying the requested subreddit. Aborting.")
        return
    subreddit = params[0]
    if len(params) > 1:
        try:
            offset = int(params[1])
        except ValueError:
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text="The second parameter has to be a positive integer value. Aborting.")
            return
        if offset < 0:
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text="The second parameter has to be a positive integer value. Aborting.")
            return

    await send_subreddit_posts(subreddit, update, context)


async def rr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reddit = asyncpraw.Reddit(client_id=REDDIT_BOT_ID, client_secret=REDDIT_BOT_SECRET, user_agent=REDDIT_USER_AGENT)
    sub = await reddit.random_subreddit(nsfw=False)
    sub_name = sub.display_name
    await context.bot.send_message(chat_id=update.message.chat_id, text="Random subreddit: \"" + sub_name + "\"")
    await send_subreddit_posts(sub_name, update, context)


async def wisdom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wisdom_string = create_wisdom_string()
    await context.bot.send_message(chat_id=update.message.chat_id, text=wisdom_string)


def create_wisdom_string():
    optional_noble = None
    optional_third = None
    optional_annex = None

    if bool(random.getrandbits(1)):
        optional_noble = random.choice(royal_titles)
    if bool(random.getrandbits(1)):
        optional_third = random.choice(third_frag)
    if bool(random.getrandbits(1)):
        optional_annex = random.choice(noble_annex)

    main_body = random.choice(first_frag) + random.choice(second_frag)
    output = "Die heutige Weisheit von "

    if optional_noble:
        output += optional_noble + " " + main_body
    else:
        output += main_body
    if optional_third:
        output += optional_third
    if optional_annex:
        output += " " + optional_annex
    output += ": " + random.choice(wisdoms)
    return output


async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    params = context.args

    if len(params) < 1:
        await context.bot.send_message(chat_id=update.message.chat_id,
                                       text="You know, I can't choose if there is nothing to choose from. Wise words!")
        return
    elif len(params) == 1:
        await context.bot.send_message(chat_id=update.message.chat_id,
                                       text="How the hell am I supposed to choose when only value is entered? Gosh.")
        return
    else:
        await context.bot.send_message(chat_id=update.message.chat_id,
                                       text=random.choice(params) + " shall be my answer!")


async def inspiro_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = inspirobot.generate()
    await context.bot.send_photo(chat_id=update.message.chat_id, photo=quote.url)


async def get_pepe(update, context):
    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo="http://www.thispepedoesnotexist.co.uk/out/pepe (" + str(random.randint(1, 9760)) + ").png"
    )


async def get_song(update, context):
    instruments = ['ukulele', 'piano', 'trumpet', 'rock_guitar']
    instrument = "piano" if len(context.args) == 0 else context.args[0]
    if instrument not in instruments:
        await context.bot.send_message(chat_id=update.message.chat_id,
                                       text='Instrument not supported, choose one of: ' + str(instruments))
        return
    resp_song = requests.get('https://this-voice-does-not-exist.com/api/get_song?&instrument=' + instrument)
    resp_cover = requests.get('https://this-voice-does-not-exist.com/api/get_song_cover?&instrument=' + instrument)

    if not resp_song.ok or not resp_cover.ok:
        await context.bot.send_message(chat_id=update.message.chat_id,
                                 text='Something went wrong internally. I am deeply sorry.')
        return

    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo='https://this-voice-does-not-exist.com/' + resp_cover.text
    )
    with io.BytesIO(resp_song.content) as buf:
        await context.bot.send_audio(
            chat_id=update.message.chat_id,
            audio=buf, performer='https://this-voice-does-not-exist.com/music',
            title=instrument + '.wav',
            duration=45
        )


async def inline_r(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    results = []
    try:
        images = await get_subreddit_images(query, count=40)
    except Exception as e:
        logging.exception(e)
        results.append(tg.InlineQueryResultArticle(0, "No", tg.InputTextMessageContent("No!")))
    else:
        if len(images) == 0:
            results.append(tg.InlineQueryResultArticle(0, "No", "No!", ))
        else:
            for img in images:
                results.append(tg.InlineQueryResultPhoto(img, img, img))
    finally:
        await update.inline_query.answer(results)


def main():
    polling_enable = False
    reddit_enable = True

    for i, arg in enumerate(sys.argv):
        if arg == "-p" or arg == "--poll":
            polling_enable = True
        if arg == "--no-reddit":
            reddit_enable = False

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    api_token = os.environ['TELEGRAM_APITOKEN']
    application = Application.builder().token(api_token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('mensa', alte_mensa))
    application.add_handler(CommandHandler('alte', alte_mensa))
    application.add_handler(CommandHandler('zelt', zelt_mensa))
    application.add_handler(CommandHandler('siede', siedepunkt_mensa))
    application.add_handler(CommandHandler('reichenbach', reichenbach_mensa))
    application.add_handler(CommandHandler('bio', bio_mensa))
    application.add_handler(CommandHandler('mensologie', mensologie_mensa))
    application.add_handler(CommandHandler('andre', andre))
    application.add_handler(CommandHandler('leon', leon))
    application.add_handler(CommandHandler('georg', georg))
    application.add_handler(CommandHandler('loen', loen))
    application.add_handler(CommandHandler('maxime', maxime))
    application.add_handler(CommandHandler('andrey', andrey))
    application.add_handler(CommandHandler('steffuu', steffuu))
    application.add_handler(CommandHandler('wetter', wetter))
    application.add_handler(CommandHandler('thomas', thomas))
    application.add_handler(CommandHandler('xkcd', xkcd))
    application.add_handler(CommandHandler('decision', decision))
    application.add_handler(CommandHandler('wisdom', wisdom))
    application.add_handler(CommandHandler('choose', choose))
    application.add_handler(CommandHandler('inspiration', inspiro_bot))
    application.add_handler(CommandHandler('pepe', get_pepe))
    application.add_handler(CommandHandler('song', get_song))

    if reddit_enable:
        global REDDIT_BOT_ID
        REDDIT_BOT_ID = os.environ['REDDIT_BOT_ID']

        global REDDIT_BOT_SECRET
        REDDIT_BOT_SECRET = os.environ['REDDIT_BOT_SECRET']

        global REDDIT_USER_AGENT
        REDDIT_USER_AGENT = os.environ['REDDIT_USER_AGENT']

        application.add_handler(CommandHandler('r', r))
        application.add_handler(CommandHandler('rr', rr))
        application.add_handler(InlineQueryHandler(inline_r))

    if polling_enable:
        application.run_polling()

    else:
        app_addr = os.environ['APP_ADDRESS']
        port = int(os.environ.get('PORT', '8443'))
        application.bot.set_webhook(app_addr + api_token)
        application.run_webhook(listen="0.0.0.0", port=port, url_path=api_token)


if __name__ == "__main__":
    main()
