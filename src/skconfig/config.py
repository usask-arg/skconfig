from typing import Union, Dict, List, Any, Tuple
from collections import namedtuple
from collections.abc import Sequence
from datetime import date, datetime
import copy
import sys
import os
import os.path
import yaml
import appdirs
from packaging import version
import numpy as np

ConfigurationLocatorInfo = namedtuple('ConfigurationLocatorInfo', ['packagename', 'groupname', 'yamlname', 'location'])


# ------------------------------------------------------------------------------
#           class CustomLoader
# ------------------------------------------------------------------------------
class CustomLoader(yaml.SafeLoader):
    """
    This is a custom loader for the YAML. it allows a !include directive to be used. Usage of this directive means the yaml
    files are not yaml conforming, but it does simplify the organization

    It follows the answer to a question on stackoverflow: https://stackoverflow.com/questions/528281/how-can-i-include-a-yaml-file-inside-another
    """

    def __init__(self, stream):

        if type(stream) is str:
            self._root = os.curdir
        else:
            self._root = os.path.split(stream.name)[0]
        super(CustomLoader, self).__init__(stream)

    def include(self, node):

        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return yaml.load(f, CustomLoader)


CustomLoader.add_constructor('!include', CustomLoader.include)


# ------------------------------------------------------------------------------
#           Configuration
# ------------------------------------------------------------------------------
class Configuration:
    """
    Class used to provide configuration settings using yaml-based text files.

    The configuration extends the yaml syntax so macro values can be encoded in the YAML file. The macro values can either
    reference other keys elsewhere in the file or environment variables. The intent is to allow users to reference
    common configuration elements, such as base directories, in one key entry or environment variable.
    """

    def __init__(self,
                 file_locator: Union[str, ConfigurationLocatorInfo, None]=None,
                 subkey=None,
                 macro_precedence_order=('env', 'int'),
                 key_delimiters=('/'),
                 yaml_text: str=None):
        """
        Initializes and loads yaml based configuration

        Parameters
        ----------
        file_locator:  str, :ref:`configurationlocatorinfo`
            The information required to locate the yaml file. If it is a string then it is assumed to be the pathname
            of the file. If it is an instance of :ref:`configurationlocatorinfo` then it is expanded to form a filename. The default
            value is None, which is useful for creating empty configurations that can be used to save user defined dictionaries.
            This value should be None if option ``yamL_text`` is used.

        subkey: str
            This is used to load a top-level subkey of the YAML file, if it is loaded. Default is None in which all levels are loaded.

        macro_precedence_order: Sequence[str]
            The one or two element tuple that describes the order of processing keys during macro expanison. See :meth:`~.set_macros_precedence_order`
            for a complete description. Default is ``('env', 'int')``

        key_delimiters: Sequence[str]
            The list of delimiters used to delimit keys when indexing variables in the yaml file. See :meth:`~.set_key_delimiters`
            for a complete description. The default is ``('/')``

        yaml_text: str
            [Optional]. If set to a string then this value is passed to method :meth:`load_from_text`.
        """

        self._filename: str = None
        self._registry: Dict[str, Any] = None
        self._full_registry: Dict[str, Any] = None
        self._macro_expand_order = macro_precedence_order                  # Precedence order when expanding macros, 'int' = internal keys in yaml file, 'env' = environment variables give precedence to
        self._key_delimiters = key_delimiters                               # Key delimiters when expanding keys like 'uv_detector.pixels.fov' or 'folders/uv/level_0'

        if (file_locator is not None):
            assert (yaml_text is None)
            self.load(file_locator, subkey=subkey)

        if yaml_text is not None:
            self.load_from_text(yaml_text)

    # ------------------------------------------------------------------------------
    #           set_values
    # ------------------------------------------------------------------------------
    def set_values(self, values: Dict[str, Any]):
        """
        Sets the internal configuration values to the dictionary passed in by the user. This dictionary does not have to
        be compliant with YAML requirements but cannot be written to a yaml file if it is not.

        Parameters
        ----------
        values: Dict[str, Any]
            The dictionary of configuration values. This is typically derived from a YAML based system but is not strictly required,
            all keys of the dictionary and any enclosed dictionaries must be strings.
        """
        self._filename: str = None
        self._registry: Dict[str, Any] = values
        self._full_registry: Dict[str, Any] = values

    # ------------------------------------------------------------------------------
    #           set_macros_precedence_order
    # ------------------------------------------------------------------------------
    def set_macros_precedence_order(self, precedence: Tuple[str, str]):
        """
        Lets the user set the precedence order for processing the expansion of macros. The default value set in the constructor is
        ('int', 'env'), which instructs the class to first look for macro definitions within the keys of the internal ('int')
        yaml file and if unsuccessful, look for definitions in environment ('env') variables.

        It is sometimes convenient to change the order to ('env', 'int') so environment variables can be used to override
        key settings within the yaml file when expanding macros.

        It is also possible, but less common, to set precedence to ('int',) to disable all checking of environment variables when expanding macros or
        to ('env',) to disable all checking of internal yaml keys when expanding macros.

        Parameters
        ----------
        precedence: Seqauence[str]
            A one or two element sequence of strings. Each string must be one of 'int' or 'env'
        """

        assert (len(precedence) == 1) or (len(precedence) == 2), ValueError("The length of the macro processing precedence order {} must be only 1 or 2.".format(len(precedence)))
        for value in precedence:
            assert (value == 'int') or (value == 'env'), ValueError("The macro processing precedence value {} must be either 'int' for internal or 'env' for environment".format(value))
        self._macro_expand_order = precedence

    # ------------------------------------------------------------------------------
    #           set_key_delimiters
    # ------------------------------------------------------------------------------
    def set_key_delimiters(self, delimiters: Tuple[str, str]):
        """
        Sets the list of one character, delimiters used when splitting strings into lists of keys. The default set in the
        constructor is ``('.','/')``. This option is provided for users who need to use the default delimiters in their keys
        stored in the yaml file. We recommend users only use this option as a last resort and should be aware that we do
        not test this option extensively.

        Parameters
        ----------
        delimiters: Lits or Tuple of str
            The array of characters used as delimiters within keys. The default value is ``('.','/')``. These delimiter values
            cannot be used in any of the key names stored in the YAML file as they will be improperly parsed and delimited.
            Note that the delimiters can be used without issue in the values associated with the keys.
        """
        self._key_delimiters = delimiters

    # ------------------------------------------------------------------------------
    #           filename
    # ------------------------------------------------------------------------------
    @property
    def filename(self) -> str:
        """
        Returns the filename of the last file read in or written to. It will be None if the user supplied the values with
        a call to :meth:`~.set_values`.
        """
        return self._filename

    # ------------------------------------------------------------------------------
    #           values
    # ------------------------------------------------------------------------------
    @property
    def values(self) -> Dict[str, Any]:
        """
        Returns direct access to the dictionary of current values used for the configuration settings. This value may
        be None if no values have been successfully set.
        """

        return self._registry

    # ------------------------------------------------------------------------------
    #           user_data_dir
    # ------------------------------------------------------------------------------
    def _user_data_dir(self, locator: ConfigurationLocatorInfo) -> str:
        """
        The location of the user folder
        """
        dirs = appdirs.AppDirs(locator.packagename, locator.groupname)
        return dirs.user_data_dir

    # ------------------------------------------------------------------------------
    #           _python_environment_dir
    # ------------------------------------------------------------------------------
    def _python_environment_dir(self, locator: ConfigurationLocatorInfo) -> str:
        """
        The location of the python share directory
        """
        dirname = os.path.join(sys.exec_prefix, 'share', locator.groupname, locator.packagename)
        return dirname

    # ------------------------------------------------------------------------------
    #           locatorinfo_to_filename
    # ------------------------------------------------------------------------------
    def locatorinfo_to_filename(self, file_locator: Union[str, ConfigurationLocatorInfo]) -> str:
        """
        Finds the filename given by the locator.
        """

        if isinstance(file_locator, str):
            full_filename = file_locator
        else:
            if file_locator.location == 'user':
                basedir = self._user_data_dir(file_locator)
            elif file_locator.location == 'python':
                basedir = self._python_environment_dir(file_locator)
            else:
                raise ValueError("The <location> field of the ConfigurationLocatorInfo {} must be either 'user' or 'python'".format(file_locator.location))

            full_filename = os.path.join(basedir, file_locator.yamlname)
        return os.path.normpath(full_filename)

    # ------------------------------------------------------------------------------
    #           _verify_keytypes
    # ------------------------------------------------------------------------------
    def _verify_keytypes(self, data: Union[Dict[Any, Any], List[Any]]) -> bool:
        """
        Verifies that the key types at any given level are identical.
        """

        ok = True
        if isinstance(data, dict):
            firstkey = next(iter(data))
            keytype = type(firstkey)
            if (keytype is date):                                                                                       # Convert date entries inside dictionary keys to datetime objects
                keys = list(data.keys())
                for key in keys:
                    if type(key) is date:
                        newkey = datetime(key.year, key.month, key.day)
                        data[newkey] = data[key]
                        data.pop(key)
                keytype = datetime
            for key in data:
                ok = ok and (type(key) is keytype)
                if (not ok):
                    print('Configuration key type error. Key {} is of data type {} is not the same type {} as other keys in the dictionary at this level'.format(key, type(key), keytype))

                    ok = ok and (type(key) is keytype)
                if (not ok):
                    print('Configuration key type error. Key {} is of data type {} is not the same type {} as other keys in the dictionary at this level'.format(key, type(key), keytype))

            for key in data:
                ok = ok and (type(key) is keytype)
                if (not ok):
                    print('Configuration key type error. Key {} is of data type {} is not the same type {} as other keys in the dictionary at this level'.format(key, type(key), keytype))

        if isinstance(data, dict):
            for key in data.keys():
                ok = ok and self._verify_keytypes(data[key])
        elif isinstance(data, Sequence) and (type(data) is not str):
                for entry in data:
                    ok = ok and self._verify_keytypes(entry)
        if (not ok):
            raise Exception('Configuration key type errors occurred.')
        return ok

    # ------------------------------------------------------------------------------
    #           load
    # ------------------------------------------------------------------------------
    def load(self, file_locator: Union[str, ConfigurationLocatorInfo], subkey=None) -> Dict[str, Any]:
        """
        Loads the configuration from a yaml file. It will search all the given locations until it finds
        the requested yaml file.

        Parameters
        ----------
        file_locator: str, ConfigurationLocatorInfo
            The information required to locate the yaml file. If it is a string then it is assumed to be the pathname
            of the file. If it is an instance of ConfigurationLocatorInfo then that is expanded to a filename

        subkey: str
            An optional key that will select one value from the top level key entries in the yaml file.

        Returns
        -------
        Dict[str,Any]
            The dictionary of values read in from the YAML file. None if there was an error loading the YAML file.
        """

        filename = self.locatorinfo_to_filename(file_locator)
        if os.path.exists(filename):
            self._filename = filename
            with open(filename) as f:
                if version.parse(yaml.__version__) > version.parse('5'):
                    self._full_registry = yaml.load(f, Loader=CustomLoader)
                else:
                    raise Exception('Configuration requires pyyaml version 5 or higher')
                    self._full_registry = yaml.load(f)
            self._registry = self._full_registry
            self._verify_keytypes(self._registry)
            if subkey is not None:
                self._registry = self._value(subkey, self._registry)
        else:
            self._full_registry = None
            self._registry = None
            self._filename = None
            raise Exception('Error finding or loading YAML file {}'.format(filename))
        return self._registry

    # ------------------------------------------------------------------------------
    #           load
    # ------------------------------------------------------------------------------
    def load_from_text(self, yaml_text: str, subkey=None) -> Dict[str, Any]:
        """
        Loads the yaml configuration from the given text.  The text should be formatted as standard yaml.  This method complements
        :meth:`load` which loads the contents of a file.

        Parameters
        ----------
        yaml_text: str,
            The input text encode in standard yaml format.

        subkey: str
            An optional key that will select one value from the top level key entries in the yaml text.

        Returns
        -------
        Dict[str,Any]
            The dictionary of values read in from the YAML file. None if there was an error loading the YAML file.
        """

        self._full_registry = yaml.load(yaml_text, Loader=CustomLoader)
        self._registry = self._full_registry
        self._verify_keytypes(self._registry)
        if subkey is not None:
            self._registry = self._value(subkey, self._registry)
        return self._registry

    # ------------------------------------------------------------------------------
    #          subkey
    # ------------------------------------------------------------------------------
    def subkey(self, subkeyname: str) -> 'Configuration':
        """
        Loads a subkey configuration from the current configuration. This mechanism preserves the capability to resolve
        macro variables.

        Parameters
        ----------
        subkey: str
            An string that selects a child dictionary and preserves the capability to expand macros

        Returns
        -------
        Configuration
            The new configuration/dictionary of values.
        """

        subkey = Configuration()
        subkey._full_registry = self._full_registry
        subkey._registry = self._value(subkeyname, self._registry)
        subkey._filename = self._filename
        assert isinstance(subkey._registry, dict) or isinstance(subkey._registry, Sequence)
        return subkey

    # ------------------------------------------------------------------------------
    #           save_registry
    # ------------------------------------------------------------------------------
    def save_registry(self,
                      file_locator: Union[str, ConfigurationLocatorInfo],
                      values: Dict[str, Any] = None,
                      make_directories: bool = True):
        """
        Writes the current configuration (or values) to the yaml file given by the file locator parameter. This will always erase any existing
        file but it will not create a new file if the configuration (or values) is empty. It will also create any sub-directories
        if option ``make_directories`` is True.

        Parameters
        ----------
        file_locator: str, ConfigurationLocatorInfo
            The information required to locate the yaml file. If it is a string then it is assumed to be the pathname
            of the file. If it is an instance of ConfigurationLocatorInfo then that is expanded to a filename

        subkey: str
            An optional key that will select one value from the top level key entries in the yaml file.
        """
        filename = self.locatorinfo_to_filename(file_locator)
        if os.path.exists(filename):
            os.unlink(filename)

        if (values is not None):
            self.set_values(values)

        if (self._registry is not None) and len(self._registry) > 0:
            basedir, name = os.path.split(filename)
            if not os.path.exists(basedir):
                if make_directories:
                    os.makedirs(basedir)
                else:
                    raise Exception('Cannot write the configuration file {} as the directory {} does not exist. Perhaps, use option <make_directories>'.format(name, basedir))
            with open(filename, 'w') as f:
                yaml.dump(self._registry, f, default_flow_style=False)
            self._filename = filename
        return True

    # ------------------------------------------------------------------------------
    #           _substitute_macros
    # ------------------------------------------------------------------------------
    def _substitute_macros(self, fullkey: str):
        """
        A simple Macro substitution. Macros refer to other keys elsewhere in the configuration dictionary.
        This code does not support macros within macros (ie no nesting). Circular references (this will loop indefinitely)
        """
        more = type(fullkey) is str
        while more:
            startidx = fullkey.find('$(')
            more = (startidx >= 0)
            if more:
                endidx = fullkey.find(')$', startidx + 1)
                if endidx < 0:
                    raise Exception(
                        "Error processing macro variable. Could not find ending }} in key {}".format(fullkey))
                else:
                    macrostr = fullkey[startidx:endidx + 2]
                    macrokey = fullkey[startidx + 2:endidx].strip()
                    macro = None
                    for source in self._macro_expand_order:
                        if source == 'int':
                            macro = self._value(macrokey, self._full_registry)
                        elif source == 'env':
                            macro = os.environ.get(macrokey)
                        else:
                            raise ValueError('Unrecognized macro expansion order term {}. Only "int" or "env" are supported'.format(source))
                        if macro is not None:
                            break
                    if macro is None:
                        raise Exception('Cannot find a macro or environment variable substitution for macro {:s} while getting value for {:s}'.format(macrokey, fullkey))
                    fullkey = fullkey.replace(macrostr, str(macro), 1)
        return fullkey

    # ------------------------------------------------------------------------------
    #           _locate_entry
    # ------------------------------------------------------------------------------
    def _locate_sub_entry(self, key: str, base: Union[Dict[Any, Any], List[Any]]):

        keybase = None
        if (base is not None):
            if (isinstance(base, dict)):                                            # if we have a dictionary
                firstkey = next(iter(base))                                         # Then get one of the keys, to get type information, all keys at one level are assumed to be the same type
                if isinstance(firstkey, str):
                    indexkey = key
                elif isinstance(firstkey, float):
                    indexkey = float(key)
                elif isinstance(firstkey, int):
                    indexkey = int(key)
                elif isinstance(firstkey, datetime):
                    indexkey = key if isinstance(key, datetime) else datetime.fromisoformat(key)
                elif isinstance(firstkey, date):
                    indexkey = date.fromisoformat(key)
                else:
                    raise Exception('The type {} of key value {} in the dictionary is unsupported'.format(type(firstkey), firstkey))
                keybase = base.get(indexkey)
            else:                                                               # otherwise we have a list, so look up the integer value
                indexkey = int(key)
                keybase = base[indexkey]
        return keybase

    # ------------------------------------------------------------------------------
    #           _value
    # ------------------------------------------------------------------------------
    def _value(self, key: Union[str, List[str], int], full_registry: Dict[str, Any]):
        is_one_key = False
        if type(key) is str:                                                # if the key index is a string, it may have delimiters eg uv_detector.data.pixel_bounds
            delim = self._key_delimiters[-1]                                # get the last delimiter in our list of delimiters used for keys
            for c in self._key_delimiters[0:-1]:                            # no loop through all the other delimiters
                key = key.replace(c, delim)                                 # and replace their value with the global delimiter
            keys = key.split(delim)                                         # and then split using the global delimiter
            if (len(keys)) < 2:
                keys = keys[0]
                is_one_key = True
        else:
            keys = key
            is_one_key = True
        base = full_registry                                                # Get the registry setting
        if is_one_key:                                                      # if we are just processing one key
            user_val = self._locate_sub_entry(keys, base)
        else:
            keybase = base
            for m in keys[:-1]:                                             # and step through the list of keyed values.
                keybase = self._locate_sub_entry(m, keybase)
            user_val = self._locate_sub_entry(keys[-1], keybase) if keybase is not None else None                            # Assign the last entry to the user value
        user_val = self._substitute_macros(user_val)
        return user_val

    # ------------------------------------------------------------------------------
    #           __getitem__
    # ------------------------------------------------------------------------------
    def __getitem__(self, key: Union[str, int]):
        """
        Overloads the indexing functions
        """
        return self._value(key, self._registry)

    # ------------------------------------------------------------------------------
    #           get_array
    # ------------------------------------------------------------------------------
    def as_array(self, keyname: Union[str, int], **kwargs) -> np.ndarray:
        """
        Returns the key value as a numpy array. This option only makes sense for configuration values that are
        sequences or some form.

        Parameters
        ----------
        keyname: str
            The configuration key to be looked up.

        **kwargs: Dict[str,Any]
            any keyword arguments are passed into the call to np.array() and can be used to control the type of array created.

        Returns
        -------
        np.ndarray
            The sequence is converted to a numpy array
        """
        entry = self._value(keyname, self._registry)
        assert (isinstance(entry, Sequence) or isinstance(entry, np.ndarray)), ValueError('The configuration key {} did not generate a sequence or array. Its type was {}.'.format(keyname, type(entry)))
        return np.array(entry, **kwargs)

    # ------------------------------------------------------------------------------
    #           as_string
    # ------------------------------------------------------------------------------
    def as_string(self, keyname: Union[str, int]) -> str:
        """
        Returns the key value as a string
        """
        return str(self._value(keyname, self._registry))

    # ------------------------------------------------------------------------------
    #           as_float
    # ------------------------------------------------------------------------------

    def as_float(self, keyname: Union[str, int]) -> float:
        """
        Returns the key value as a floating point number
        """
        return float(self._value(keyname, self._registry))

    # ------------------------------------------------------------------------------
    #           as_int
    # ------------------------------------------------------------------------------
    def as_int(self, keyname: Union[str, int]) -> int:
        """
        Returns the key value as an integer
        """
        return int(self._value(keyname, self._registry))

    # ------------------------------------------------------------------------------
    #           as_pathname
    # ------------------------------------------------------------------------------
    def as_pathname(self, keyname: Union[str, int]) -> str:
        """
        Returns the key value as a pathname. The string returned from the yaml file is passed through a call to ``os.path.normpath``.
        """
        name = self.as_string(keyname)
        path = os.path.normpath(name)
        return path
