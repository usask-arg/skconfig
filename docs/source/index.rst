
##########
skconfig
##########
Package `skconfig <https://github.com/usask-arg/skconfig>`_ provides an interface for managing YAML based configuration files. The package provides a few
extensions to help ease access and usage of the configuration file,

#.  The ability to load and save configuration files in standard locations on the computer.
#.  A *dot* or *slash* notation to index nested keys
#.  A simple macro scheme which allows the value of one key or environment variables to be used when fetching another value.

If you are looking for the scikit-learn sampling and validation library then you are at the wrong place. You can find their
documentation here  `sckit-learn documentation <https://skconfig.readthedocs.io/en/latest/>`_

..  toctree::
    :maxdepth: 1

    installation
    overview
    api

History
-------
2026-01-22: Updated the code so macro expansion would include expansions from parent configurations.

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
