import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pihole5-list-tool",
    version="0.1.0",
    author="jesse",
    author_email="jessedp@gmail.com",
    description="Tool to add block/ad/ignore lists to pi-hole5",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jessedp/pihole5-list-tool",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'PyInquirer',
        'ansicolors'
    ]
)