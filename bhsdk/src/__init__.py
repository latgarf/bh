import configparser
import logging
import logging.config

CONFIG_FILE='/etc/bhsite/bhsite.conf'
config = configparser.SafeConfigParser()
config.read(CONFIG_FILE)

logging.config.fileConfig(CONFIG_FILE, disable_existing_loggers=True)
logger_access = logging.getLogger('access')
logger_payments = logging.getLogger('payments')