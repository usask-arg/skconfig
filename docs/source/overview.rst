..  _overview:

Overview
========
The :class:`~.Configuration` class provides access to YAML based configuration files. It has three elements built in

#.  The ability to load and save configuration files in standard locations on the computer.
#.  A *dot* or *slash* notation to index nested keys
#.  A simple macro scheme which allows the value of one key or environment variables to be used when fetching another value.

We shall be showing some examples below and in all cases we will be loading a yaml file whose contents are given below::

    MYINSTRUMENT_DATABASE_FOLDER: './Users/nickl/Documents/Work/software/data_storage/myinstrument'
    folders:
        l1pp_datafiles: $( MYINSTRUMENT_DATABASE_FOLDER )$/l1pp_datafiles          # Use the environment variable MYINSTRUMENT_DATABASE_FOLDER for location of  database files etc.
        sdo_hmii_data: $( MYINSTRUMENT_DATABASE_FOLDER )$/sdo_hmii_data             # Location where we store the Solar Dynamics Observatory HMI continuum images,

    vis:
        front_aperture_area: 25.0                                                  # front aperture area in cm2.
        spectral:
            wavelength_range: [400.0, 800.0]

        window:
            native_size:           [2000,1504]                                  # Y,X dimensions of the native CMOS detector
            science_native_size:   [501,  501]                                  # Y,X dimensions of the scienmce window in  native pixels
            science_native_origin: [0,0]                                        # Y,X Origin of bottom left corner of science window in native pixel
            science_binning:       [3,3]                                        # Y,X native pixel binning to make sceince window
            fov_degrees:           [2.5917959198092038, 1.948056503444799]      # Y,X field of view in degrees across the native size window
        spatial_psf:
            data_file: $(folders/l1pp_datafiles)$/vis/vispsf.mat                # Visible channel point spread function extracted from SPS.


Macro Syntax $(...)$
---------------------
If you examine the YAML example above file you will see that it is a standard YAML file. But if you look a little closer
you will see some of the values, e.g. folders/l1pp_datafiles, are using a macro syntax of the form ``$(....)$``. The parameter
enclosed between the dollar-braces is the name of another key within the yaml file or an environment variable. The value of
the key or environment variable is looked up and substituted for the dollar-braced value. The system, by default, will
search all the internal keys of the YAML file first and then search the environment variable name space.

Here is an example that looks up a key with macro exapansion if we assume the contents of file ``myinstrument.yaml`` are as given above::

    import skconfig

    locator_info = skconfig.ConfigurationLocatorInfo(packagename='myinstrument', groupname='usask-arg', yamlname='myinstrument.yaml', location='user')
    config = skconfig.Configuration(file_locator=self.locator_info )
    data_file = config['vis.spatial_psf.datafile']
    print(data_file)

    >>> ./Users/nickl/Documents/Work/software/data_storage/myinstrument/l1pp_datafiles/vis/vispsf.mat

In this example we fetch the value of key ``vis.spatial_psf.datafile``. This key is looked up and it is found that it contains a macro,
``$(folders/l1pp_datafiles)$``, that needs to be expanded. The value of this new key is looked up and found to be
``$(MYINSTRUMENT_DATABASE_FOLDER)$/l1pp_datafiles``. It also contains a macro which is looked up. The process repeats
until all references are found and relaced. In the example given here it stops when key ``MYINSTRUMENT_DATABASE_FOLDER`` is
looked up and found at the top of the file.

Precedence Order
~~~~~~~~~~~~~~~~
In another example, we want to use the same YAML file but we no longer want to use the value of ``MYINSTRUMENT_DATABASE_FOLDER``
stored in the file. We could edit the file, which will work, but we can also create an environment variable called
``MYINSTRUMENT_DATABASE_FOLDER`` and set its value to the new, desired value. We then instruct the configuration to
look up macros from environment variables first and then from internal keys::

    import os
    import skconfig

    os.environ[ALTIUS_DATABASE_FOLDER] = r'E:\altius_data'
    config = skconfig.Configuration(file_locator='./testconfig.yaml', macro_precedence_oder=('env', 'int'))
    data_file = config.as_pathname('vis.spatial_psf.datafile')

     >>> E:\altius_data\l1pp_datafiles\vis\vispsf.mat

Thus, we can override macros inside the yaml file by changing the precedence order so it searches environment variables first
and then internal keys. The technique only works for well for top level keys as the delimiters used for nested keys may not work
properly with environment variables.

Also note that we used the :meth:`~.as_pathname` technique to lookup the filename rather than the square bracket indexing operator
which simply includes a call to ``os.path.normpath`` to clean up the returned filename.

Dot Notation
------------
The :class:`~.Configuration` implements a *dot* and/or *slash* notation for indexing the YAML components. The YAML file is
loaded in by ``pyYAML`` as a regular python dictionary which include many nested dictionaries. For example if we are looking up
the value of ``vis.spatial_psf.datafile`` then the standard technique would be given by::

    config = skconfig.Configuration(file_locator='./testconfig.yaml')
    data_file = config[`vis`][`spatial_psf`][`datafile`]

There is nothing wrong with this format although the macro-expansion is disabled after the first element as the code is
no longer operating within the code belonging to :class:`~.Configuration`.

The :class:`~.Configuration` prefers users to use a *dot* or *slash* notation to index keys so macro expansion can be
properly applied. Some may even argue that it makes the code more legible so we have::

    config = skconfig.Configuration(file_locator='./testconfig.yaml')
    data_file = config['vis.spatial_psf.datafile']

 or with *slash* notation::

    config = skconfig.Configuration(file_locator='./testconfig.yaml')
    data_file = config['vis/spatial_psf/datafile']

The *dot* and *slash* are delimiters that can be changed in the constructor or by method :meth:`~.set_key_delimiters` although
we do not expect many users to need to change the values.  Note that the key delimiters must not occur in the name of the
key used in the yaml file but they can occur in the values of the keys.

File Locator
------------
The :class:`~.Configuration` works with the :ref:`configurationlocatorinfo` named tuple to allow users to access and store
yaml files in standard computer locations as well as regular file locations. Yaml files can be accessed in sub-folders
of the *User Data Directory* (or ``user_data_dir``) as defined by python package ``appdirs`` or in the *share* folder of
the current python environment.

For example, to access yaml files in the *User Data Directory*, first create the :ref:`configurationlocatorinfo` named tuple and
then construct the :class`~.Configuration` ::

    import skconfig

    locator_info = skconfig.ConfigurationLocatorInfo(packagename='myinstrument', groupname='usask-arg', yamlname='myinstrument.yaml', location='user')
    config = skconfig.Configuration(file_locator=locator_info )

Similarly, to access yaml files in the *Python share folder*, first create the :ref:`configurationlocatorinfo` named tuple and
then construct the :class`~.Configuration` ::

    import skconfig

    locator_info = skconfig.ConfigurationLocatorInfo(packagename='myinstrument', groupname='usask-arg', yamlname='myinstrument.yaml', location='python')
    config = skconfig.Configuration(file_locator=locator_info )

and finally to access a yaml file directly just use the full filename as  a string::

    import skconfig

    config = skconfig.Configuration(file_locator='E:/mysintrumet/config/myinstrument.yaml')

Subkeys
--------
It is possible to access just a section of the yaml file by specifying a top level subkey. This is useful in instruments
that may have several channels which have the same logical configuration::

    import skconfig

    config = skconfig.Configuration(file_locator='E:/mysintrumet/config/myinstrument.yaml', subkey='vis')

The entire yaml file is retained internally which allows for proper macro expansion but as far as the user is concerned
they will only access the subkey section. Sub-keying only works on the top level indexing.





