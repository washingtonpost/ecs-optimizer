import os
from setuptools import setup, find_packages
import warnings

setup(
    name='ecs-optimizer',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'boto3>=1.4.4',
        'retrying>=1.3.3',
        'click>=6.7'
    ],
    entry_points={
        "console_scripts": [
            "ecs-optimizer=optimizer.cli:cli",
        ]
    },
    namespace_packages = ['optimizer'],
    author="Patrick Cullen and the WaPo platform tools team",
    author_email="opensource@washingtonpost.com",
    url="https://github.com/WPMedia/ecs-optimizer",
    download_url = "https://github.com/WPMedia/ecs-optimizer/tarball/v0.1.0",
    keywords = ['ecs', 'aws', 'optimizer'],
    classifiers = []
)
