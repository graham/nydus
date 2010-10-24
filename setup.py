import setuptools
from setuptools import setup, find_packages, Extension, Feature

setup(
        name="nydus",
        version=0.1,
        description="Nydus API framework.",
        long_description="Nydus API Framework.",
        author="Graham Abbott",
        author_email="graham.abbott@gmail.com",
        packages=find_packages(),
        platforms=['any'],
        zip_safe=True,
    )
