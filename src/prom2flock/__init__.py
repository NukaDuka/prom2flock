import logging
import re
import sys
import os
import argparse
from gunicorn.app.wsgiapp import run
import gunicorn_conf

def main():
    # Get and parse command line arguments
    print(gunicorn_conf)
    argparser = argparse.ArgumentParser(description='A web service that processes and routes alertmanager alerts to Flock')
    argparser.add_argument('-c', '--config', default='/etc/prom2flock/config.yaml', help='prom2flock config file location')
    args = argparser.parse_args()

    config_file_location = args.config

    logging.basicConfig(format='%(asctime)s [%(funcName)s (%(name)s)]  %(levelname)s: %(message)s', level=logging.DEBUG)
    # Add prom2flock config location to environment variables
    os.environ['CONFIG_FILE_LOCATION'] = config_file_location
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    
    os.chdir(os.path.dirname(gunicorn_conf.__file__))
    
    # This argv will be passed along to gunicorn
    sys.argv = [sys.argv[0], '-c', gunicorn_conf.__file__, 'wsgi:app']
    
    # Run gunicorn and pass along exit code
    sys.exit(run())
    
if __name__ == "__main__":
    main()
