from setuptools import setup, find_packages

import meshiphi
import meshiphi.dataloaders
import meshiphi.mesh_generation
import tests

def get_content(filename):
    with open(filename, "r") as fh:
        return fh.read()


requirements = get_content("requirements.txt")

setup(
    name=meshiphi.__name__,
    version=meshiphi.__version__,
    description=meshiphi.__description__,
    license=meshiphi.__license__,
    long_description=get_content("README.md"),
    long_description_content_type="text/markdown",
    author=meshiphi.__author__,
    author_email=meshiphi.__email__,
    maintainer=meshiphi.__author__,
    maintainer_email=meshiphi.__email__,
    url="https://www.github.com/antarctica",
    project_urls={
    },
    classifiers=[el.lstrip() for el in """Development Status :: 3 - Alpha
        Intended Audience :: Science/Research
        Intended Audience :: System Administrators
        License :: OSI Approved :: MIT License
        Natural Language :: English
        Operating System :: OS Independent
        Programming Language :: Python
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.7
        Topic :: Scientific/Engineering""".split('\n')],
    entry_points={
        'console_scripts': [
            "create_mesh=meshiphi.cli:create_mesh_cli",
            "export_mesh=meshiphi.cli:export_mesh_cli",
            "rebuild_mesh=meshiphi.cli:rebuild_mesh_cli",
            "merge_mesh=meshiphi.cli:merge_mesh_cli",
            "meshiphi_test=meshiphi.cli:meshiphi_test_cli"]
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
