import os
import requests
import setuptools
from get_pypi_latest_version import GetPyPiLatestVersion

os.environ["PYTHONIOENCODING"] = "utf-8"
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

MODULE_NAME = "ok-script-kes"

obtainer = GetPyPiLatestVersion()
VERSION_NUM = os.environ.get('OK_SCRIPT_BUILD_VERSION')
latest_version = None
if VERSION_NUM is None:
    try:
        latest_version = obtainer(MODULE_NAME)
        VERSION_NUM = obtainer.version_add_one(latest_version, add_patch=True)
    except requests.HTTPError as error:
        if error.response.status_code != 404:
            raise
        VERSION_NUM = "1.0.0"
print(f'latest_version is {latest_version} new version is {VERSION_NUM}')

setuptools.setup(
    name=MODULE_NAME,
    version=VERSION_NUM,
    author="baoxin1100",
    author_email="879278510@qq.com",
    description="Modified ok-script automation framework based on ok-script 1.0.181",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/baoxin1100/ok-script-kes",
    packages=setuptools.find_packages(exclude=['tests', 'docs']),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    install_requires=[
        'pywin32>=306',
        'pyappify>=1.0.6',
        'PySide6-Fluent-Widgets>=1.8.3',
        'typing-extensions>=4.11.0',
        'requests>=2.32.3',
        'psutil>=6.0.0',
        'pydirectinput==1.0.4',
        'pycaw==20240210',
        'mouse==0.7.1'
    ],
    entry_points={
        'console_scripts': [
            'ok=ok.cli:main',
        ],
    },
    python_requires='>=3.11',
    zip_safe=False,
)
