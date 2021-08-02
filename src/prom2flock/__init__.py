import subprocess
import logging
import sys
import os
import argparse
from . import gunicorn_conf

def main():
    # Get and parse command line arguments
    argparser = argparse.ArgumentParser(description='A web service that processes and routes alertmanager alerts to Flock')
    argparser.add_argument('-c', '--config', default='/etc/prom2flock/config.yaml', help='prom2flock config file location')
    args = argparser.parse_args()

    config_file_location = args.config

    logging.basicConfig(format='%(asctime)s [%(funcName)s (%(name)s)]  %(levelname)s: %(message)s', level=logging.DEBUG)
    # Import environment from os
    os_env = os.environ.copy()
    os_env['CONFIG_FILE_LOCATION'] = config_file_location
    # Check if gunicorn exists
    output = subprocess.run(['gunicorn', '-v'], env=os_env)
    if output.returncode != 0:
        logging.error('Gunicorn cannot be found in $PATH, exiting')
        sys.exit(1)
    output = subprocess.run(['gunicorn', '-c', gunicorn_conf.__file__, 'wsgi:app'], env=os_env, cwd=os.path.dirname(gunicorn_conf.__file__))
if __name__ == "__main__":
    main()
