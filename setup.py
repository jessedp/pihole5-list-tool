import io
import ast
from setuptools import setup, find_packages


def version():
    """Return version string."""
    with io.open('src/ph5lt.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


with io.open("README.md") as readme:
    setup(
        name="pihole5-list-tool",
        version=version(),
        author="jessedp",
        author_email="jessedp@gmail.com",
        description="A tool for quickly and easily bulk adding block lists to a Pi-hole 5 installation",
        long_description=readme.read(),
        long_description_content_type="text/markdown",
        packages_dir="src",
        package_dir={'': 'src'},
        packages=find_packages(where=('src'), exclude=('tests', 'tests.*')),
        include_package_data=True,
        url="https://github.com/jessedp/pihole5-list-tool",
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Topic :: Utilities",
            "Topic :: Internet :: Name Service (DNS)",
        ],
        keywords='pihole, pi-hole, blacklist, blocklist, adlist',
        python_requires='>=3.6',
        install_requires=[
            'PyInquirer',
            'ansicolors',
            'requests'
        ],
        py_modules=['ph5lt', 'constants'],
        entry_points={
            'console_scripts': ['pihole5-list-tool = ph5lt:main']
        },
    )
