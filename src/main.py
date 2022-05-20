#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
import telegram as tg
import requests
import json
import os
import io
import time
import logging
from datetime import timedelta
import translate
import random
from bs4 import BeautifulSoup
import praw
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

haes = ["HÄ?", "APEX?", "OVERWATCH?", "AMONG US?", "WIE", "WANN", "WO", "Geller muss erst noch zu Ende essen!", "???", "*Random Katzenbild*", "APEX JETZT!", "ZOCKEN JETZT!", "ICH HASSE EUCH ALLE", "HÄÄÄ", "ICH ARBEITE", "ICH HASSE DEN", "FUCK YOU", "WIRKLICH", "BITTE", "Natürlich ist das gelb!", "Es gibt Kuchen!", "Wir haben wieder viel zu viel Lasagne!", "Oke", "WAS", "WAS MEINST DU", "WAS WILLST DU DENN JETZT SCHON WIEDER", "Alter", "Wirst schon sehen", "Denk nach du Schwamm", "Stop", "NICHT COOL", "TROLL NICHT RUM", "Uff", "AAAAARGH", "Kann den jemand kicken?", "DU HAST NUR ANGST VOR MIR", "EKELHAFT", "ICH HASSE ALLES", "WOFÜR", "ICH BIN IMMER SO", "KUCHEN", "LASAGNE", "SCHANDE", "WARUM ICH", "ICH LIEBE ARBEITEN", "ICH HASSE UNPÜNKTLICHKEIT", "IDIOT", "HEY", "WO SEID IHR", "WAS SONST", "KIBA", "HAHA", "VERSTEHT IHR DAS NICHT", "SEID IHR DUMM ODER WAS", "WTF", "RED DEUTSCH MIT MIR", "OMG", "LOL", ":)", "MIR IST LANGWEILIG", "ALS OB IHR ALLE SCHON SCHLAFT", "HALLO", "WEIß ICH NICHT", "WER DENKT SICH DAS AUS", "ICH SPRING LIEBER AUS DEM FENSTER", "NE", "SCHEISS AUTOKORREKTUR", "ICH BIN NETT", "BONNIIIIIIIIIIIIIEEEE", "FICK DICH", "EINE KATZE", "ICH BIN DIE BESTE", "ICH BIN SO DUMM", "*Random Katzenvideo*", "ICH KANN EUCH DATINGTIPPS GEBEN", "EH FOREVER", "HENRY <3", "EINE NIELPFERD UWU"]


class NotifyUserException(Exception):
    """Raised whenever an error needs to be propagated to the user"""
    pass


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Reichenbach is never an option!")


def mensa(update, context, mensaId):
    params = context.args
    if len(params) < 1:
        days_to_add = 0
    else:
        try:
            days_to_add = int(params[0])
        except ValueError:
            context.bot.send_message(chat_id=update.message.chat_id, text="The first and only parameter has to be an integer value. Aborting.")
            return
    day = update.message.date.date() + timedelta(days=days_to_add)
    url = "https://api.studentenwerk-dresden.de/openmensa/v2/canteens/" + str(mensaId) + "/days/" + day.strftime("%Y-%m-%d") + "/meals"
    resp = requests.get(url)
    if not resp.ok:
        context.bot.send_message(chat_id=update.message.chat_id, text="I failed miserably. Disgrace!")
        return
    json_data = resp.json()
    if len(json_data) == 0:
        context.bot.send_message(chat_id=update.message.chat_id, text="No food today :(")
    for elem in json_data:
        meal_notes = elem["notes"]
        markdown_highlight_char = "_"
        for note in meal_notes:
            if "vegetarisch" in note or "vegan" in note:
                markdown_highlight_char = "*"

        img_url = elem["image"].lstrip("/") # For some reason, image URLs are prefixed with 2 leading slashes, but no protocol, remove them
        # Do not send placeholder images
        if img_url.endswith("studentenwerk-dresden-lieber-mensen-gehen.jpg"):
            context.bot.send_message(chat_id=update.message.chat_id, text=markdown_highlight_char + elem["name"] + markdown_highlight_char, parse_mode="Markdown")
        else:
            context.bot.send_photo(chat_id=update.message.chat_id, photo=img_url, caption=markdown_highlight_char + elem["name"] + markdown_highlight_char, parse_mode="Markdown")


def alte_mensa(update, context):
    mensa(update, context, 4)


def zelt_mensa(update, context):
    mensa(update, context, 35)


def siedepunkt_mensa(update, context):
    mensa(update, context, 9)


def reichenbach_mensa(update, context):
    mensa(update, context, 6)


def bio_mensa(update, context):
    mensa(update, context, 29)


def andre(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Höhöhö Reichenbach!")


def leon(update, context):
    joke = dad_joke()
    context.bot.send_message(chat_id=update.message.chat_id, text=joke)


def loen(update, context):
    joke = dad_joke()
    translator = translate.Translator(from_lang='en', to_lang='de')
    translated_joke = translator.translate(joke)
    context.bot.send_message(chat_id=update.message.chat_id, text=translated_joke)


def dad_joke():
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


def steffuu(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=random.choice(haes))

def thomas(update, context):
        sticker_set = context.bot.get_sticker_set("jason_funderburker")
        random_sticker = random.choice(sticker_set.stickers)
        context.bot.send_sticker(chat_id=update.message.chat_id, sticker=random_sticker)

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


def xkcd(update, context):
    params = context.args
    rand = False
    xkcd_id = 0
    if len(params) < 1:
        rand = True
    else:
        try:
            xkcd_id = int(params[0])
        except ValueError:
            context.bot.send_message(chat_id=update.message.chat_id, text="The first and only parameter has to be a positive integer value greater than 0. Aborting.")
            return
        if xkcd_id < 1:
            context.bot.send_message(chat_id=update.message.chat_id, text="The first and only parameter has to be a positive integer value greater than 0. Aborting.")
            return
    try:
        xkcd_data = get_xkcd(xkcd_id, rand)
    except NotifyUserException as error:
        context.bot.send_message(chat_id=update.message.chat_id, text=str(error))
        return
    context.bot.send_photo(chat_id=update.message.chat_id, photo=xkcd_data[1], caption=str(xkcd_data[0]) + " - " + xkcd_data[2])


def decision(update, context):
    headers = {'Accept': 'text/plain '}
    resp = requests.get("https://yesno.wtf/api/", headers=headers)
    if not resp.ok:
        raise NotifyUserException("oof")
    data = json.loads(resp.text)
    context.bot.send_animation(chat_id=update.message.chat_id, animation=data["image"], caption=data["answer"])


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


def get_subreddit_images(subreddit, offset=0, count=5):
    images = []
    reddit = praw.Reddit(client_id=REDDIT_BOT_ID, client_secret=REDDIT_BOT_SECRET, user_agent=REDDIT_USER_AGENT)
    for post in reddit.subreddit(subreddit).hot(limit=count):
        if get_post_type(post) == RedditPostTypes.image:
            images.append(post.url)
    return images


def send_subreddit_posts(subreddit, update, context, offset=0, count=5):
    reddit = praw.Reddit(client_id=REDDIT_BOT_ID, client_secret=REDDIT_BOT_SECRET, user_agent=REDDIT_USER_AGENT)
    posts_sent = False
    try:
        for post in reddit.subreddit(subreddit).hot(limit=count):
            if not post.stickied:
                post_type = get_post_type(post)
                if post_type == RedditPostTypes.text:
                    message = "*"+post.title+"* \n" + post.selftext
                    if len(message) > 1000:
                        message = message[:1000]
                        message = message + "*(...)* [" + post.url + "]"
                    context.bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=tg.ParseMode.MARKDOWN)
                    posts_sent = True
                elif post_type == RedditPostTypes.image:
                    context.bot.send_photo(chat_id=update.message.chat_id, photo=post.url, caption=post.title)
                    posts_sent = True
                elif post_type == RedditPostTypes.video:
                    context.bot.send_message(chat_id=update.message.chat_id, text=post.url)
                    posts_sent = True
                elif post_type == RedditPostTypes.animation:
                    for site in REDDIT_EXCLUDED_ANIMATION_SITES:
                        if site in post.url:
                            pass
                    context.bot.send_animation(chat_id=update.message.chat_id, animation=post.url, caption=post.title)
                    posts_sent = True

    except Exception as e:
        print(e)
        context.bot.send_message(chat_id=update.message.chat_id, text="Something went wrong internally. I am deeply sorry.")
        return

    if not posts_sent:
        context.bot.send_message(chat_id=update.message.chat_id, text="No compatible Posts were found.")


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

    send_subreddit_posts(subreddit, update, context)


def rr(update, context):
    reddit = praw.Reddit(client_id=REDDIT_BOT_ID, client_secret=REDDIT_BOT_SECRET, user_agent=REDDIT_USER_AGENT)
    sub = reddit.random_subreddit(nsfw=False)
    sub_name = sub.display_name
    context.bot.send_message(chat_id=update.message.chat_id, text="Random subreddit: \"" + sub_name + "\"")
    send_subreddit_posts(sub_name, update, context)


def cat(update, context):
    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo="https://thiscatdoesnotexist.com?time=" + str(time.time()) + str(random.randint(1, 1024))
    )


def snack(update, context):
    snack_data = requests.get("https://thissnackdoesnotexist.com/?time=" + str(time.time()) + str(random.randint(1, 1024)), headers={'User-Agent': 'USER_AGENT_BROWSER'})
    if not snack_data.ok:
        context.bot.send_message(chat_id=update.message.chat_id, text="Something went wrong internally. I am deeply sorry.")
        return

    soup = BeautifulSoup(snack_data.text,'html.parser')
    text = soup.find('h1').text
    picture_url = soup.find('div').attrs.get('style').split("(", 1)[1].split(")")[0]
    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=picture_url,
        caption=text
    )


def horse(update, context):
    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo="https://thishorsedoesnotexist.com?time=" + str(time.time()) + str(random.randint(1, 1024))
    )


def person(update, context):
    resp = requests.get("https://thispersondoesnotexist.com/image?time=" + str(time.time()) + str(random.randint(1, 1024)), headers={'User-Agent': 'USER_AGENT_BROWSER'})

    if not resp.ok:
        context.bot.send_message(chat_id=update.message.chat_id, text="Something went wrong internally. I am deeply sorry.")
        return

    with io.BytesIO(resp.content) as buf:
        context.bot.send_photo(chat_id=update.message.chat_id, photo=buf)


def wisdom(update, context):
    wisdom_string = create_wisdom_string()
    context.bot.send_message(chat_id=update.message.chat_id, text=wisdom_string)


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


def choose(update, context):
    params = context.args

    if len(params) < 1:
        context.bot.send_message(chat_id=update.message.chat_id, text="You know, I can't choose if there is nothing to choose from. Wise words!")
        return
    elif len(params) == 1:
        context.bot.send_message(chat_id=update.message.chat_id, text="How the hell am I supposed to choose when only value is entered? Gosh.")
        return
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=random.choice(params) + " shall be my answer!")


def inspiroBot(update, context):
    quote = inspirobot.generate()
    context.bot.send_photo(chat_id=update.message.chat_id, photo=quote.url)


def inline_r(update, context):
    query = update.inline_query.query
    results = []
    try:
        images = get_subreddit_images(query, count=40)
    except Exception:
        results.append(tg.InlineQueryResultArticle(0, "No", tg.InputTextMessageContent("No!")))
    else:
        if len(images) == 0:
            results.append(tg.InlineQueryResultArticle(0, "No", "No!", ))
        else:
            for img in images:
                results.append(tg.InlineQueryResultPhoto(img, img, img))
    finally:
        update.inline_query.answer(results)


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
    updater = Updater(token=api_token, use_context=True)

    start_handler = CommandHandler('start', start)
    updater.dispatcher.add_handler(start_handler)

    mensa_handler = CommandHandler('mensa', alte_mensa)
    updater.dispatcher.add_handler(mensa_handler)

    alte_mensa_handler = CommandHandler('alte', alte_mensa)
    updater.dispatcher.add_handler(alte_mensa_handler)

    zelt_mensa_handler = CommandHandler('zelt', zelt_mensa)
    updater.dispatcher.add_handler(zelt_mensa_handler)

    siedepunkt_mensa_handler = CommandHandler('siede', siedepunkt_mensa)
    updater.dispatcher.add_handler(siedepunkt_mensa_handler)

    reichenbach_mensa_handler = CommandHandler('reichenbach', reichenbach_mensa)
    updater.dispatcher.add_handler(reichenbach_mensa_handler)

    bio_mensa_handler = CommandHandler('bio', bio_mensa)
    updater.dispatcher.add_handler(bio_mensa_handler)

    andre_handler = CommandHandler('andre', andre)
    updater.dispatcher.add_handler(andre_handler)

    leon_handler = CommandHandler('leon', leon)
    updater.dispatcher.add_handler(leon_handler)

    georg_handler = CommandHandler('georg', georg)
    updater.dispatcher.add_handler(georg_handler)

    loen_handler = CommandHandler('loen', loen)
    updater.dispatcher.add_handler(loen_handler)

    maxime_handler = CommandHandler('maxime', maxime)
    updater.dispatcher.add_handler(maxime_handler)

    andrey_handler = CommandHandler('andrey', andrey)
    updater.dispatcher.add_handler(andrey_handler)

    steffuu_handler = CommandHandler('steffuu', steffuu)
    updater.dispatcher.add_handler(steffuu_handler)

    thomas_handler = CommandHandler('thomas', thomas)
    updater.dispatcher.add_handler(thomas_handler)

    xkcd_handler = CommandHandler('xkcd', xkcd)
    updater.dispatcher.add_handler(xkcd_handler)

    decision_handler = CommandHandler('decision', decision)
    updater.dispatcher.add_handler(decision_handler)

    cat_handler = CommandHandler('cat', cat)
    updater.dispatcher.add_handler(cat_handler)

    snack_handler = CommandHandler('snack', snack)
    updater.dispatcher.add_handler(snack_handler)

    horse_handler = CommandHandler('horse', horse)
    updater.dispatcher.add_handler(horse_handler)

    person_handler = CommandHandler('person', person)
    updater.dispatcher.add_handler(person_handler)

    wisdom_handler = CommandHandler('wisdom', wisdom)
    updater.dispatcher.add_handler(wisdom_handler)

    choose_handler = CommandHandler('choose', choose)
    updater.dispatcher.add_handler(choose_handler)

    inspirationHandler = CommandHandler('inspiration', inspiroBot)
    updater.dispatcher.add_handler(inspirationHandler)

    if reddit_enable:
        global REDDIT_BOT_ID
        REDDIT_BOT_ID = os.environ['REDDIT_BOT_ID']

        global REDDIT_BOT_SECRET
        REDDIT_BOT_SECRET = os.environ['REDDIT_BOT_SECRET']

        global REDDIT_USER_AGENT
        REDDIT_USER_AGENT = os.environ['REDDIT_USER_AGENT']

        reddit_img_handler = CommandHandler('r', r)
        updater.dispatcher.add_handler(reddit_img_handler)

        reddit_random_handler = CommandHandler('rr', rr)
        updater.dispatcher.add_handler(reddit_random_handler)

        inline_reddit_handler = InlineQueryHandler(inline_r)
        updater.dispatcher.add_handler(inline_reddit_handler)

    if polling_enable:
        updater.start_polling()
        updater.idle()

    else:
        app_addr = os.environ['APP_ADDRESS']
        port = int(os.environ.get('PORT', '8443'))
        updater.start_webhook(listen="0.0.0.0", port=port, url_path=api_token)
        updater.bot.set_webhook(app_addr + api_token)
        updater.idle()


if __name__ == "__main__":
    main()
