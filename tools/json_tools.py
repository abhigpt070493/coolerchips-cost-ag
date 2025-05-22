import json
import jsonpickle
from pathlib import Path

from tools.dict_tools import from_dict


def _strip_comments(d):
    """
    Removes comments from json files when converting to Python.

    Parameters
    ----------
    d: dict
        Dictionary loaded from a json file

    Returns
    -------
    Dictionary with any file comments (designated by '#') removed.

    """

    return {k: v for k, v in d.items() if not k.startswith("#")}


def object_from_json_gen(fpath, clazz):
    """
    Creates a generic object of a specified class with attributes specified in a json file.

    Parameters
    ----------
    fpath: str
        Filepath for json file containing data to be converted to objected

    clazz: class
        Class name for object to be created

    Returns
    -------
    An object with the specified class.

    Notes
    _____
    This function does NOT call the specified class's __init__ method and therefore does NOT create an error
    if a required attribute is missing. Additionally, this function allows addition of attributes that are NOT
    attributes created by the __init__ method. The object has access to specified class's methods via specifying the
    "py/object" attribute as the specified class.

    """

    # Open json file and load data as python dictionary with comments removed.
    # Specify class for object to be created.
    # Convert dict containing class back to json and create Python object via jsonpickle.

    with open(fpath, "r") as f:
        data = json.load(f, object_hook=_strip_comments)
    data["py/object"] = clazz.__module__ + "." + clazz.__name__
    dataj = json.dumps(data)
    obj = jsonpickle.decode(dataj)

    return obj


def objects_from_dir_gen(location, clazz):
    """
    Creates generic objects of a specified class for each json file within a directory.

    Parameters
    ----------
    location: str
    Directory location for json files containing data to create objects.

    clazz: class
        Class name for objects to be created

    Returns
    -------

    Dictionary of objects with the specified class.

    """
    objects = {}
    entries = Path(location)
    for entry in entries.iterdir():
        obj = object_from_json_gen(entry, clazz)
        name = obj.name
        objects[name] = obj
    return objects


def object_from_json(fpath, clazz, level='base'):
    """
    Creates a instance of an object of a specified class with attributes specified in a json file.

    Parameters
    ----------

    fpath: str
        Filepath for json file containing data to be converted to objected

    clazz: class
        Class name for object to be created

    level: str
        For nested json data, specifies which key in nested dict to use for attribute value

    Returns
    -------
    Instance of object of specified class.

    Notes
    -----
    This function calls from_dict function, and as such, only supports creating objects from json files that convert
    to dicts in Python. Additionally, from_dict only supports 1 level of nesting.

    """
    with open(fpath, "r") as f:
        data = json.load(f, object_hook=_strip_comments)
    obj = from_dict(clazz, data, level)

    return obj


def objects_from_dir(location, clazz, level='base'):
    """
    Creates instances of a specified class for each json file within a directory.

    Parameters
    ----------
    location: str
        Directory location for json files containing data to create objects.

    clazz: class
        Class name for instances to be created

    level: str
        For nested json data, specifies which key in nested dict to use for attribute value

    Returns
    -------
    Dictionary of instances of the specified class.

    """
    objects = {}
    entries = Path(location)
    for entry in entries.iterdir():
        obj = object_from_json(entry, clazz, level)
        name = obj.name
        objects[name] = obj
    return objects
