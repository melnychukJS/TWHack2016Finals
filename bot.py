from random import getrandbits

import re

from telegram import InlineQueryResultArticle, ParseMode
from telegram.ext import Updater
import requests
import logging
import random

headers = {'Content-type': 'application/json'}

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)

REGEX = '\$|€|£|pound[s]|euro?s?|dollar[s]'

WELCOME_MESSAGE = """Hi!
Send money or exchange currency, right here.

Examples:
- Transfer/exchange money:
    /pay 50€ [to dollars] to @username
- Check the fee that you would be charged:
    /fee $20
- Show past transactions:
    /history
Powered by TransferWise™. 
(Disclaimer: This product is not created neither endorsed with TransferWise™ in any ways.)
"""


HELP_MESSAGE = """
Examples of useful commands:

- Transfer/exchange money:
    /pay 50€ [to dollars] to @username

- Check the fee that you would be charged:
    /fee $20

- Show past transactions:
    /history
"""


FEE_MESSAGE = """The fee will be
{}{}"""

HISTORY_MESSAGE = """Past transactions:

* 200.000€ to @melnychukJS yesterday noon
* $100 to @javierhonduco 2 days ago in the morning
* 300€ to pounds sent to @Nooregaardo a month ago
"""

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text=WELCOME_MESSAGE)


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text=HELP_MESSAGE)


def confirm(bot, update):
    bot.sendMessage(update.message.chat_id, text="""Cool!
Transaction reference number is `{}`.
All the details were sent to your email.
Cheers!""".format(random.randint(1, 99999999)))


def history(bot, update):
    bot.sendMessage(update.message.chat_id, text=HISTORY_MESSAGE)


def pay(bot, update):
    text = update['message']['text']

    money = re.findall('[0-9]+', text, re.IGNORECASE)
    currency = re.findall(REGEX, text, re.IGNORECASE)

    to = re.findall('@[a-zA-Z]+', text, re.IGNORECASE)
    if len(money) == 0:
        bot.sendMessage(update.message.chat_id, text="Please, input the amount. See /help for tips.")
    elif len(currency) == 0:
        bot.sendMessage(update.message.chat_id, text="Please, input the currency. See /help for tips.")
    elif(len(to)==0):
        bot.sendMessage(update.message.chat_id, text="Please, input the receiver. See /help for tips.")
    else:
        if len(currency)==1:
            response = requests.get('https://test-restgw.transferwise.com/v1/quotes?source={}&target={}&sourceAmount={}&rateType=FIXED'.format(
                to_iso(currency[0]),
                to_iso(currency[0]),
                money[0]
            ), 
            headers=headers,
            auth=('b909eac5-b567-4ca2-a55d-4cb2eeb74a79', '5cfe25e0-f322-404a-b0d3-537d262b2fd0')).json()

            bot.sendMessage(update.message.chat_id, text="""Total amount is {}.
Transaction fee is {}{}.
Type /confirm <passcode>. (the passcode will be sent to your other linked device.)
""".format(float(money[0])+response["fee"], response["fee"], currency[0]))
        else:
            response = requests.get('https://test-restgw.transferwise.com/v1/quotes?source={}&target={}&sourceAmount={}&rateType=FIXED'.format(
                to_iso(currency[0]),
                to_iso(currency[1]),
                money[0]
            ), 
            headers=headers,
            auth=('b909eac5-b567-4ca2-a55d-4cb2eeb74a79', '5cfe25e0-f322-404a-b0d3-537d262b2fd0')).json()

            bot.sendMessage(update.message.chat_id, text="""Total amount of conversion is {}.
Transaction fee is {}{}.
Type /confirm <passcode>. (the passcode will be sent to your other linked device.)
""".format(float(money[0])+response["fee"], response["fee"], currency[1]))


def to_iso(input):
    return {
        'eur': 'EUR',
        'euro': 'EUR',
        'euros': 'EUR',
        '€': 'EUR',
        'pound': 'GBP',
        'pounds': 'GBP',
        '£': 'GBP',
        'dollar': 'USD',
        'dollars': 'USD',
        '$': 'USD',
    }.get(input.lower(), 'EUR')


def fee(bot, update):
    text = update['message']['text']

    money = re.findall('[0-9]+', text, re.IGNORECASE)
    currency = re.findall(REGEX, text, re.IGNORECASE)

    if len(money)==0:
        bot.sendMessage(update.message.chat_id, text="Please, input the amount.")
    elif len(currency)==0:
        bot.sendMessage(update.message.chat_id, text="Please, input the currency.")
    else:

        currency = re.findall(REGEX, text, re.IGNORECASE)

    if len(money)==0:
        bot.sendMessage(update.message.chat_id, text="Please, input the amount.")
    elif len(currency)==0:
        bot.sendMessage(update.message.chat_id, text="Please, input the currency.")
    else:

        currency = re.findall(REGEX, text, re.IGNORECASE)
        if len(currency)>1:

            response = requests.get('https://test-restgw.transferwise.com/v1/quotes?source={}&target={}&sourceAmount={}&rateType=FIXED'.format(
                to_iso(currency[0]),
                to_iso(currency[1]),
                money[0]
            ), 
            headers=headers,
            auth=('b909eac5-b567-4ca2-a55d-4cb2eeb74a79', '5cfe25e0-f322-404a-b0d3-537d262b2fd0')).json()

            bot.sendMessage(update.message.chat_id, text=FEE_MESSAGE.format(response['fee'], currency[1]))
        else:
            response = requests.get('https://test-restgw.transferwise.com/v1/quotes?source={}&target={}&sourceAmount={}&rateType=FIXED'.format(
                to_iso(currency[0]),
                to_iso(currency[0]),
                money[0]
            ), 
            headers=headers,
            auth=('b909eac5-b567-4ca2-a55d-4cb2eeb74a79', '5cfe25e0-f322-404a-b0d3-537d262b2fd0')).json()
            bot.sendMessage(update.message.chat_id, text=FEE_MESSAGE.format(response['fee'], currency[0]))



def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def inlinequery(bot, update):
    if update.inline_query is not None and update.inline_query.query:
        query = update.inline_query.query
        results = list()

        results.append(InlineQueryResultArticle(
                id=hex(getrandbits(64))[2:],
                title="History",
                message_text=HISTORY_MESSAGE))

        bot.answerInlineQuery(update.inline_query.id, results=results)



def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main(): 
    # Create the Updater and pass it your bot's token.
    updater = Updater("181752127:AAFX10TTymBCbB4_0RKG5LxtoBJKgyYUulM")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.addTelegramCommandHandler("start", start)
    dp.addTelegramCommandHandler("help", help)
    dp.addTelegramCommandHandler("pay", pay)
    dp.addTelegramCommandHandler("fee", fee)
    dp.addTelegramCommandHandler("history", history)
    dp.addTelegramCommandHandler("confirm", confirm)

    # on noncommand i.e message - echo the message on Telegram
    dp.addTelegramInlineHandler(inlinequery)

    # log all errors
    dp.addErrorHandler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()