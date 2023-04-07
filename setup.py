# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 13:56:42 2023

@author: Diego
"""

from setuptools import setup, find_packages

setup(
      name = "gerber",
      version = "0.1",
      description = "Package for using the gerber statistic for various statistical techniques",
      author = "Diego Alvarez",
      author_email = ["diego.alvarez@colorado.edu", "diegoalvarez3800@gmail.com"],
      packages = find_packages(),
      install_requires = [
          "pandas >= 1.0.0",
          "numpy >= 1.18.0",
          "itertools >= 1.0.0"],
      classifiers = [
          "Development Status :: 3 - Alpha",
          "Intended Audiance :: Developers, Finance / Insurance, Science / Research",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.6",
          "Programming Langauge :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9"])