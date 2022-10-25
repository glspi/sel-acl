"""pan_deduper"""
import setuptools

__version__ = "0.0.91"
__author__ = "Ryan Gillespie"

setuptools.setup(
    name="sel_acl",
    version=__version__,
    packages=["sel_acl", "sel_aci"],
    include_package_data=True,
    install_requires=[
        "typer==0.6.1",
        "openpyxl==3.0.10",
        "ciscoconfparse==1.6.40",
        "rich==12.5.1",
        "httpx==0.23.0",
        "jinja2==3.1.2",
    ],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": ["sel-acl = sel_acl.cli:app", "sel-aci = sel_aci.cli:app"]
    },
)
