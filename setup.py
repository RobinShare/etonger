import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="etonger",
    version="1.1.8",
    author="RobinShare",
    author_email="robinshare@foxmail.com",
    description="trading api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/robinshare/etonger',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=["requests"],
    classifiers=[
    "Programming Language :: Python :: 3.9",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)

# python setup.py sdist bdist_wheel
# twine upload dist/*
