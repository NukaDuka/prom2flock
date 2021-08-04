from setuptools import setup

setup(
    name = 'prom2flock',
    version = '0.3.3',
    author = "Kartik Gokte",
    author_email = "ksgokte@gmail.com",
    description = "A web service that processes and routes Alertmanager alerts to any Flock channel",
    url = "https://github.com/NukaDuka/prom2flock",
    python_requires="~=3.8",
    package_dir={"": "src"},
    packages = ['prom2flock'],
    #scripts = ['src/prom2flock/__init__.py'],
    entry_points = {
        'console_scripts' : [
            'prom2flock = prom2flock:main [Flask, gunicorn, requests, PyYAML]'
        ]
    },
    install_requires = [
        "Flask==1.1.2",
        "gunicorn==20.0.4",
        "requests==2.25.1",
        "PyYAML==5.4.1"
    ]
)
