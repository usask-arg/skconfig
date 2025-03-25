# skconfig
THis package provides configuration information using YAML based files/text. We have added extensions that allow
MACROS and environment variables to be used. This functionality could be used for many applications, but we developed 
it to create a yaml based description of various instrument calibration files that was portable from one 
machine and location to another.

The location of the calibration files is defined in the YAML file using a combination of yaml-based macros, environment 
variables and regular yaml text. The package resolves the macros and environment variables and combines them with the regular 
yaml text to form the exact location of the filename. Other applications of the package are entirely possible.


## Installation
    
    pip install skconfig

We recommend running the unit tests, see below, after installation to download Earth rotation data files.

### Building a wheel
The python wheel can also be built from source code,

    conda install setuptools build
    python -m build --wheel

## Usage
Documentation can be found at ReadTheDocs [skconfig](https://skconfig-arg.readthedocs.io/en/latest/). Please note that 
we share the same name as the [scikit package](https://skconfig.readthedocs.io/en/latest/) but we are not related to each other.

## Unit Tests
It is useful to run the unit tests as the tests will automatically download leap-second files and earth rotation 
information. Needless to say you must have an internet connection to successfully run the unit tests 

    python -m unittest discover -s skconfig.tests

## License
This project is licensed under the MIT license.



