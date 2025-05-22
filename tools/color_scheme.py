import json
import seaborn as sns


def color_from_json(filepath):
    """
    Creates a color list from a json file of colors.

    Parameters
    ----------
    filepath: str
        Filepath for the json file containing colors.

    Returns
    -------
    colors: list
        List of colors.
    """

    with open(filepath, "r") as f:
        data = json.load(f)
    colors = []
    for k, v in data.items():
        colors.append(v)

    return colors


def set_color_scheme(filepath):
    """
    Sets color palette for sns (seaborn).

    Parameters
    ----------
    filepath: str
        Filepath for the json file containing colors.

    Returns
    -------

    """
    colors = color_from_json(filepath)
    sns.set_palette(sns.color_palette(colors))
