from setuptools import setup

setup(
    name = 'prom2flock',
    version = '0.1.0',
    author = "Kartik Gokte",
    author_email = "ksgokte@gmail.com",
    description = "A web service that processes and routes Alertmanager alerts to any Flock channel",
    url = "https://github.com/NukaDuka/prom2flock",
    python_requires="==3.8",
    package_dir={"": "src"},
    packages = ['prom2flock'],
    install_requires = [
        "Flask==1.1.2",
        "gunicorn==20.0.4",
        "requests==2.25.1",
    ]
)