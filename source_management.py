import sys
import pathlib
from config import _read_config, _write_config, _get_config_path, DEFAULT_CONFIG_STRUCTURE
from wallpaper_logic import _get_all_available_wallpapers

def _add_managed_source(path: str) -> None:
    """
    Purpose: 
        Adds a path (wallpaper) to config.json, 'managed_sources' list.
        Handles: Prevents adding duplicate paths (wallpaper) to config.json.

    Arguments:
        str: String path of the wallpaper source to be added.
    """

    config_file_path = _get_config_path()
    current_config = _read_config()

    if path not in current_config['managed_sources']:
        current_config['managed_sources'].append(path)
        _write_config(current_config, config_file_path)
        sys.stderr.write("Wallpaper was added successfully.\n")
    else:
        sys.stderr.write("Wallpaper has already been added.\n")


def _remove_managed_source(path: str) -> None:
    """
    Purpose:
        Removes a path (wallpaper) from config.json, 'managed_sources' list.
        Handles: Prevents removing nonexistent path (wallpaper) from config.json.
    Arguments:
        string: String path of the wallpaper source to be removed.
    """

    config_file_path = _get_config_path()
    current_config = _read_config()

    if path in current_config['managed_sources']:
        current_config['managed_sources'].remove(path)
        _write_config(current_config, config_file_path)
        sys.stderr.write("Wallpaper was removed successfully.\n")
    else:
        sys.stderr.write("Wallpaper does not exist.\n")


def list_sources() -> list[str]:
    """
    Purpose:
        Retrieves the list of managed wallpaper source paths from the configuration file.
    Returns:
        list[str]: A list of absolute paths (as strings) to the managed wallpaper sources.
                   Returns an empty list if no sources are configured or if the key is missing.
    """

    current_config = _read_config()

    return current_config.get('managed_sources', [])


def clean_invalid_sources() -> None:
    """
    Purpose:
        Removes all non-existent paths from managed_sources in the configuration.
        This function iterates through the list of managed sources, checks if
        each path actually exists on the filesystem, and removes any that do not.
    """

    config_file_path = _get_config_path()
    current_config = _read_config()

    managed_sources = current_config.get('managed_sources', [])

    valid_sources = []
    changes_made = False

    sys.stderr.write("Checking managed wallpaper sources for validity...\n")

    for wp_string in managed_sources:
        wallpaper = pathlib.Path(wp_string)

        if wallpaper.exists():
            valid_sources.append(wp_string)
        else:
            sys.stderr.write(f"Invalid source removed: '{wp_string}' (path does not exist).\n")
            changes_made = True

    if changes_made:
        current_config['managed_sources'] = valid_sources
        _write_config(current_config, config_file_path)
        sys.stderr.write("Managed sources cleaned and configuration updated.\n")
    else:
        sys.stderr.write("No invalid sources found.\n")


def place_source_ahead(wallpaper_to_move: str, wallpaper_to_precede: str) -> None:
    # For another time :D
    pass

def place_source_before(wallpaper_to_move: str, wallpaper_to_precede: str) -> None:
    # For another another time :D 
    pass