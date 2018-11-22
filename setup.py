# -*- coding: utf-8 -*-
import os
import shutil
from setuptools import setup, find_packages

def run():
    setup(
        name="Sagittarium",  # pypi中的名称，pip或者easy_install安装时使用的名称
        version="1.0",
        description=("A test suite for automatically running MTBF on different devices"),
        # 需要打包的目录列表
        packages=find_packages(),
        # 需要安装的依赖
        install_requires=[
            'Appium-Python-Client'
        ],
        author = "test",
        author_email = "test@thundersoft.com",
        # 此项需要，否则卸载时报windows error
        # zip_safe=False
    )

    if os.path.exists('Sagittarium.egg-info'):
        shutil.rmtree('Sagittarium.egg-info')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

if __name__ == '__main__':
    run()
