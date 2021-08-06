import yaml
import sys, errno
import os
reload = False
errorlog = '-'
accesslog = '-'

loglevel = 'debug'
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
except:
    # This shouldn't matter since the on_starting hook will (hopefully) stop the server before ever reaching here
    bind = '0.0.0.0:5009'
    port = 5009
    reload = False

try:
    with open('/var/run/prom2flock/prom2flock.port', 'w') as f:
        f.write(str(port))
except:
    print('Can not open /var/run/prom2flock')

timeout = 0
keepalive = 10

if __name__ == "__main__":
	print('gunicorn config file')
