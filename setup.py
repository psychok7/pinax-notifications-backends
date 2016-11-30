import codecs

from os import path
from setuptools import find_packages, setup


def read(*parts):
    filename = path.join(path.dirname(__file__), *parts)
    with codecs.open(filename, encoding="utf-8") as fp:
        return fp.read()


setup(
    author="Nuno Khan",
    author_email="nunok7@gmail.com",
    description=(
        "Django application that implements a few backends for "
        "pinax-notifications"
    ),
    name="pinax-notifications-backends",
    long_description=read("README.rst"),
    version="0.1",
    url="https://github.com/psychok7/pinax-notifications-backends",
    license="MIT",
    packages=find_packages(),
    package_data={
        "notifications": []
    },
    install_requires=[
        "pinax-notifications>=4.0.0", "django-sendsms>=0.2.3",
        "django-push-notifications>=1.4.1"
    ],
    dependency_links=[
        'http://github.com/Ubiwhere/pinax-notifications/tarball/notice_model'
        '#egg=pinax-notifications-4.0.0',
    ],
    test_suite="runtests.runtests",
    tests_require=[
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False
)
