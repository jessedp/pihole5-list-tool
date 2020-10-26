import io
import ast
from setuptools import setup, find_packages


def version():
    """Return version string."""
    with io.open("ph5lt/banner.py") as input_file:
        for line in input_file:
            if line.startswith("__version__"):
                return ast.parse(line).body[0].value.s


with io.open("README.md") as readme:
    setup(
        name="pihole5-list-tool",
        version=version(),
        author="jessedp",
        author_email="jessedp@gmail.com",
        description="A tool for quickly and easily bulk adding allowlists and ad/blocklists to a Pi-hole 5 installation",
        long_description=readme.read(),
        long_description_content_type="text/markdown",
        package_dir="",
        packages1=find_packages(exclude=("tests", "tests.*")),
        packages=["ph5lt"],
        url="https://github.com/jessedp/pihole5-list-tool",
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Topic :: Utilities",
            "Topic :: Internet :: Name Service (DNS)",
        ],
        project_urls={
            "Bug Tracker": "https://github.com/jessedp/pihole5-list-tool/issues",
            "Source Code": "https://github.com/jessedp/pihole5-list-tool",
        },
        keywords="pihole, pi-hole, blacklist, blocklist, whitelist, allowlist, adlist",
        python_requires=">=3.6",
        install_requires=["PyInquirer", "ansicolors", "requests", "terminaltables"],
        packages2=["ph5lt"],
        py_modules2=[
            "ph5lt",
            "prompts",
            "constants",
            "utils",
            "banner",
            "allowlists",
            "blocklists",
            "stats",
        ],
        entry_points={"console_scripts": ["pihole5-list-tool = ph5lt.app:main"]},
    )
