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
        "setuptools==54.2.0",
        "certifi==2020.12.5",
        "chardet==4.0.0",
        "click==7.1.2",
        "Flask==1.1.2",
        "gunicorn==20.1.0",
        "idna==2.10",
        "itsdangerous==1.1.0",
        "Jinja2==2.11.3",
        "MarkupSafe==1.1.1",
        "pip==20.0.2",
        "PyYAML==5.4.1",
        "requests==2.25.1",
        "urllib3==1.26.4",
        "Werkzeug==1.0.1",
    ]
)