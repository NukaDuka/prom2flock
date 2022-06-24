from setuptools import setup

setup(
    name = 'prom2flock',
    version = '0.5.4',
    author = "Kartik Gokte",
    author_email = "ksgokte@gmail.com",
    description = "A web service that processes and routes Alertmanager alerts to any Flock channel",
    url = "https://github.com/NukaDuka/prom2flock",
    python_requires="~=3.9",
    package_dir={"": "src"},
    packages = ['prom2flock'],
    #scripts = ['src/scripts/prom2flock'],
    entry_points = {
        'console_scripts' : [
	        'prom2flock = prom2flock.main:main [Flask, gunicorn, requests, PyYAML]'
        ]
    },
    install_requires = [
        "Flask~=2.1",
        "gunicorn~=20.1",
        "requests~=2.28",
        "PyYAML~=6.0",
    ]
)
