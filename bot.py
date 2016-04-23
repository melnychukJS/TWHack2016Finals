from random import getrandbits

import re

from telegram import InlineQueryResultArticle, ParseMode
from telegram.ext import Updater
import logging

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


WELCOME_MESSAGE = """Hi!
I'm transferbot and I'm here to help you.
You can call me anywhere and issue a transfer :)

/pay to issue a payment.
/quote to check the quote offer.


With /help you can see more info."""


HELP_MESSAGE = """Help
"""

PAY_MESSAGE = """Cool!
{}{} sent to {}!
"""

FEE_MESSAGE = """The fee will be
{}{}"""

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text=WELCOME_MESSAGE)


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text=HELP_MESSAGE)


def pay(bot, update):
    text = update['message']['text']

    money = re.findall('[0-9]+', text)[0]
    currency = re.findall('\$|€', text)[0]
    to = re.findall('@[a-zA-Z]+', text)[0]
    bot.sendMessage(update.message.chat_id, text=PAY_MESSAGE.format(money, currency, to))


def fee(bot, update):
    bot.sendMessage(update.message.chat_id, text=FEE_MESSAGE.format(0.5, '€'))


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
                title="Caps",
                message_text=query.upper()))

        results.append(InlineQueryResultArticle(
                id=hex(getrandbits(64))[2:],
                title="Bold",
                message_text="*%s*" % escape_markdown(query),
                parse_mode=ParseMode.MARKDOWN))

        results.append(InlineQueryResultArticle(
                id=hex(getrandbits(64))[2:],
                title="Italic",
                message_text="_%s_" % escape_markdown(query),
                parse_mode=ParseMode.MARKDOWN))

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