import subprocess
import logging
import sys
import os

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s [%(funcName)s (%(name)s)]  %(levelname)s: %(message)s', level=logging.DEBUG)
    # Import environment from os
    os_env = os.environ.copy()
    # Check if gunicorn exists
    output = subprocess.run(['gunicorn', '-h'], shell=True, env=os_env)
    if output.returncode != 0:
        logging.error('Gunicorn cannot be found in $PATH, exiting')
        sys.exit(1)
    output = subprocess.run(['gunicorn', '-c', './gunicorn.conf.py', 'wsgi:app'], shell=True, env=os_env)
