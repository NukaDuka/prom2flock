import yaml
import sys, errno
import os
reload = False
errorlog = '-'
accesslog = '-'

pidfile = '/var/run/prom2flock/prom2flock.pid'

def on_starting(server):
    # check if config file exists and is readable
    server.log.info('Checking config file')
    if os.environ.get('CONFIG_FILE_LOCATION') is None:
        server.log.error('CONFIG_FILE environment variable not found, exiting')
        sys.exit(errno.ENOENT)

    CONFIG_FILE = os.environ.get('CONFIG_FILE_LOCATION')
    if not os.path.isfile(CONFIG_FILE):
        server.log.error(CONFIG_FILE + ' is unreadable or does not exist, exiting')
        sys.exit(errno.ENOENT)

try:
    CONFIG_FILE = os.environ.get('CONFIG_FILE_LOCATION')
    with open(CONFIG_FILE, 'r') as f:
        config_file = yaml.safe_load(f)
        bind = config_file['server']['host'] + ':' + str(config_file['server']['port'])
        reload = config_file['server']['debug']
        port = config_file['server']['port']
        workers = config_file['server']['workers']
        loglevel = config_file['server']['logging']['verbosity']

except Exception as e:
    print('ERROR: config file invalid, more information below')
    print(e)
    sys.exit(errno.ENOENT)

try:
    with open('/var/run/prom2flock/prom2flock.port', 'w') as f:
        f.write(str(port))
except:
    print('ERROR: Can not open /var/run/prom2flock')

timeout = 0
keepalive = 10

if __name__ == "__main__":
    print('gunicorn config file')
