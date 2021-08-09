from flask import Flask, request
import yaml
import logging
import logging.handlers
import json
import re
import requests
import os

app = Flask(__name__)

if os.environ.get('CONFIG_FILE_LOCATION') is None:
    logging.basicConfig(format='%(asctime)s [%(funcName)s (%(name)s)]  %(levelname)s: %(message)s', level=logging.DEBUG)
    logging.error('CONFIG_FILE environment variable not found, exiting')
    exit(1)

CONFIG_FILE = os.environ.get('CONFIG_FILE_LOCATION')
if not os.path.isfile(CONFIG_FILE):
    logging.basicConfig(format='%(asctime)s [%(funcName)s (%(name)s)]  %(levelname)s: %(message)s', level=logging.DEBUG)
    logging.error(CONFIG_FILE + ' is unreadable or does not exist, exiting')
    exit(1)

# Load initial configuration
with open(CONFIG_FILE, 'r') as f:
    logging.basicConfig(format='%(asctime)s [%(funcName)s (%(name)s)]  %(levelname)s: %(message)s', level=logging.DEBUG)
    try:
        config = yaml.safe_load(f)
        app.config['SERVER_PORT'] = config['server']['port']
        app.config['SERVER_HOST']  = config['server']['host']
        app.config['LOGGER_RETENTION'] = config['server']['logging']['logger_retention_time']
        app.config['ERROR_LOGGER_RETENTION'] = config['server']['logging']['error_logger_retention_time']
        app.config['ACCESS_LOGGER_RETENTION'] = config['server']['logging']['access_logger_retention_time']
        app.config['LOGGER_VERBOSITY'] = config['server']['logging']['verbosity']
        app.config['TIMEOUT'] = config['server']['timeout']
        app.config['RETRIES'] = int(config['server']['retries'])
        app.config['FLOCK_CONFIG'] = config['flock']

        # Test flock config
        try:
            default_receiver = app.config['FLOCK_CONFIG']['default']['webhook_link']
            default_format = app.config['FLOCK_CONFIG']['default']['alert_format']
            if default_format.find('!{description}') == -1:
                logging.error('Alert format requires the following field: "!{description}"')
                raise ImportError

        except:
            logging.error('Bad flock config')
            raise
    except:
        raise

logger = logging.getLogger('main_logger')
logger.setLevel(logging.DEBUG)

log_handler = logging.handlers.TimedRotatingFileHandler('/var/log/prom2flock/log/prom2flock_log.log', when='d', backupCount=app.config['LOGGER_RETENTION'])
error_handler = logging.handlers.TimedRotatingFileHandler('/var/log/prom2flock/error/error_log.log', when='d', backupCount=app.config['ERROR_LOGGER_RETENTION'])

formatter = logging.Formatter('%(asctime)s [%(funcName)s (%(name)s)]  %(levelname)s: %(message)s')

error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)
log_handler.setLevel(app.config['LOGGER_VERBOSITY'])
log_handler.setFormatter(formatter)

logger.addHandler(log_handler)
logger.addHandler(error_handler)

@app.route('/healthz', defaults={'message': 'OK'})
@app.route('/healthz/<string:message>')
def healthcheck(message):
    return message

@app.route('/', methods=['POST'])
def main():
    if request.json is None:
        return "Invalid request, please check the request payload and headers", 400
    logger.debug('Request received')
    try:
        req = request.json
        alerts = req['alerts']
        for alert in alerts:
            # Get info from alert field
            try:
                logger.debug(json.dumps(alert))
                status = alert['status']
                '''
                Default alert format:

                1) Firing: "<b>[AlertName]</b> *description*"
                1) Resolved: "<b>[RESOLVED] [AlertName]</b>"
                '''
                labels = alert['labels']
                annotations = alert['annotations']
                prometheus_url = alert['generatorURL']

                default_alert_format = app.config['FLOCK_CONFIG']['default']['alert_format']
                default_resolve_format = app.config['FLOCK_CONFIG']['default']['resolve_format']

                # Receiver info should be a string in the 'annotations' field
                # TODO: Add more request-specific configuration options here
                receiver = annotations.get('receiver')
                description = annotations['description']
                format = annotations.get('alert_format', default_alert_format)

                if format.find('!{description}') == -1:
                    logger.warning('Format string "' + format + '" does not have a field for the annotation "description", switching to default format string')
                    format = default_alert_format

                status = alert['status']
                logger.debug('Alert status: ' + status)
                if status == 'resolved':
                    format = annotations.get('resolve_format', default_resolve_format)

                format = format.replace('!{description}', description)
                format = format.replace('!{generatorURL}', prometheus_url)

                pattern = '!\{([a-zA-Z0-9_-]*)\}'
                needed_labels = re.findall(pattern, format)
                cleaned_format = re.split('!\{(%)\}', re.sub(pattern, '!{%}', format))
                substitution_data = [labels.get(l, '') for l in needed_labels]
                for i in range(len(substitution_data)):
                    try:
                        idx = cleaned_format.index('%')
                    except:
                        break
                    cleaned_format[idx] = substitution_data[i]

                alert_message = ''.join(cleaned_format)

                payload_json = {}
                payload_json['flockml'] = alert_message
                logger.debug(json.dumps(payload_json))
                url = app.config['FLOCK_CONFIG']['webhooks'].get(receiver, 'empty')
                if url == 'empty':
                    if receiver is None:
                        receiver = '[none]'
                    logger.debug('Receiver "' + receiver + '" does not exist!')
                    url = app.config['FLOCK_CONFIG']['default']['webhook_link']

                i = 0
                while i < app.config['RETRIES']:
                    r = requests.post(url, data=json.dumps(payload_json), timeout=app.config['TIMEOUT'])
                    logger.debug(r.status_code)
                    if r.status_code == 200:
                        break
                    i = i+1
                if i == app.config['RETRIES']:
                    logger.warning('Flock may be down or endpoint may be invalid. Receiver: ' + receiver)
                    return 'Flock request timed out', 503

            except Exception as e:
                logger.exception('Bad request')
                logger.debug(json.dumps(alert))
                raise
    except Exception as e:
        return 'Invalid request format', 400
    return 'OK'

# This function can only change the flock routing config, a server restart is needed to change any of it's variables
@app.route('/reload')
def reload():
    logger.info('Starting config reload')
    # Save old config in case of rollback
    old_config = {}
    old_config['LOGGER_VERBOSITY'] = app.config['LOGGER_VERBOSITY']
    old_config['FLOCK_CONFIG'] = app.config['FLOCK_CONFIG']
    old_config['TIMEOUT'] = app.config['TIMEOUT']
    old_config['RETRIES'] = app.config['RETRIES']

    with open(CONFIG_FILE, 'r') as f:
        try:
            config = yaml.safe_load(f)
            app.config['LOGGER_VERBOSITY'] = config['server']['logging']['verbosity']
            app.config['FLOCK_CONFIG'] = config['flock']
            app.config['TIMEOUT'] = int(config['server']['timeout'])
            app.config['RETRIES'] = int(config['server']['retries'])

            # Test existance of flock config
            default_receiver = app.config['FLOCK_CONFIG']['default']['webhook_link']
            default_format = app.config['FLOCK_CONFIG']['default']['alert_format']
            if default_format.find('!{description}') == -1:
                raise ImportError
            log_handler.setLevel(app.config['LOGGER_VERBOSITY'])
        except Exception as exc:
            logger.exception('Error while loading config')
            # Rollback
            app.config['LOGGER_VERBOSITY'] = old_config['LOGGER_VERBOSITY']
            app.config['FLOCK_CONFIG'] = old_config['FLOCK_CONFIG']
            app.config['TIMEOUT'] = old_config['TIMEOUT']
            app.config['RETRIES'] = old_config['RETRIES']
            return 'An error has occurred. Please check the logs.', 500


    return 'OK'
# For testing
if __name__ == "__main__":
    app.run(port=app.config['SERVER_PORT'], host=app.config['SERVER_HOST'])
