import configparser
import sys


def config_parser(full_path_config):
    config = configparser.ConfigParser()
    file = full_path_config
    config.read(file)
    try:
        translate_url = config.get('urls', 'translate_url')
        bot_token = config.get('tokens', 'bot_token')
        translate_token = config.get('tokens', 'translate_token')
        db = config.get('address', 'db_address')
        return translate_url, bot_token, translate_token, db
    except (TypeError, configparser.NoSectionError, configparser.NoOptionError):
        print('Config file is not correct or not found')
        sys.exit(1)