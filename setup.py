from setuptools import setup, find_packages

import cartographi
import cartographi.dataloaders
import cartographi.mesh_generation

def get_content(filename):
    with open(filename, "r") as fh:
        return fh.read()


requirements = get_content("requirements.txt")

setup(
    name=cartographi.__name__,
    version=cartographi.__version__,
    description=cartographi.__description__,
    license=cartographi.__license__,
    long_description=get_content("README.md"),
    long_description_content_type="text/markdown",
    author=cartographi.__author__,
    author_email=cartographi.__email__,
    maintainer=cartographi.__author__,
    maintainer_email=cartographi.__email__,
    url="https://www.github.com/antarctica",
    project_urls={
    },
    classifiers=[el.lstrip() for el in """
        Development Status :: 3 - Alpha
        Intended Audience :: Science/Research
        Intended Audience :: System Administrators
        License :: OSI Approved :: MIT License
        Natural Language :: English
        Operating System :: OS Independent
        Programming Language :: Python
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.7
        Topic :: Scientific/Engineering
    """.split('\n')],
    entry_points={
        'console_scripts': [
            "create_mesh=cartographi.cli:create_mesh_cli",
            "export_mesh=cartographi.cli:export_mesh_cli",
            "rebuild_mesh=cartographi.cli:rebuild_mesh_cli"],
    },
    keywords=[],
    packages=find_packages(),
    install_requires=requirements,
    tests_require=["pytest"],
    extras_require={
        "tests": get_content("tests/requirements.txt"),
    },
    zip_safe=False,
    include_package_data=True)
