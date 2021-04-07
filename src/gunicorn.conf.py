import yaml
import sys, errno

reload = False
errorlog = '-'
accesslog = '-'

pidfile = '/var/run/prom2flock/prom2flock.pid'

def on_starting(server):
    # check if config file exists and is readable
    server.log.info('Checking config file')
    try:
        with open('/etc/prom2flock/config.yaml', 'r') as f:
            f.readline()
    except:
        server.log.error('Config file does not exist or is not accessible')
        sys.exit(errno.EINTR)

try:
    with open('/etc/prom2flock/config.yaml', 'r') as f:
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