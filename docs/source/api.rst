..  _api:

*****
API
*****

Configuration Class
===================

.. autoclass:: skconfig.Configuration
    :members:
    :special-members: __init__

..  _configurationlocatorinfo:

ConfigurationLocatorInfo
=========================
The :ref:`configurationlocatorinfo` object is a ``namedtuple`` that describes where a yaml configuration file is stored on
the system. The configuratiuon code currently considers two locations where yaml files can be stored,

#. The ``user`` option specifies a folder specific to the current user that stores configuration for all software executed
   by the current user. This location is shared by all python environments. On Windows, this is typically the folder
   ``C:\Users\<xxxx>\AppData\Local``. This location is useful for configuration information that can be shared between
   different python environments. We use the ``appdirs`` package to specify this folder.
#. The ``python`` option specifies a folder specific to the current python environment. For example, on windows this might be
   folder``C:\Users\<xxxx>\anaconda3\envs\<python_env>``. This is useful when configuration information is specific to a
   python environment. We use the python folder returned by ``sys.exec_prefix/share'``./

The configuration software does not implement, multi-user, machine wide configuration.



..  function:: ConfigurationLocatorInfo(packagename=packagename, groupname=groupname, yamlname=filename, location=locationval)

    The namedtuple used to create a filename as ``<location>/<groupname>/<packagename>/yamlname``

    :param str packagename:
        The ``<packagename>`` component used in the filename generation. This is typically the name of the python package that owns the Configuration information, e.g. ``altius_l1pp``

    :param str groupname:
        The ``<groupname>`` component used in the filename generation. This is typically the name of the company or group. e.g. ``usask-arg``

    :param str yamlname:
        The ``<yamlname>`` component used in the filename generation. This is the name of the yaml file and typically does not include any directory information, e.g. ``settings.yaml``.

    :param str location:
        Specifies how the the ``<location>`` component of the filename is generated. The currently supported values are ``user`` and ``python``, which are described above.


