from chat_bot.bot import Bot
from utilities.config_parser import config_parser


config_path = 'utilities/config.ini'

if __name__ == '__main__':
    translate_url, bot_token, translate_token, address = config_parser(config_path)
    try:
        Bot(translate_url, translate_token, bot_token, address)
    except KeyboardInterrupt:
        pass