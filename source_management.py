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


def move_source(wallpaper_to_move_index: int, wallpaper_position: int) -> None:
    """
    Purpose:
        Moves a wallpaper source (directory or file path) to a desired position
        within the 'managed_sources' list in the configuration.
        This reordering affects the sequence in which wallpapers are processed
        for 'set-next', 'set-prev', and sequential slideshows.

    Arguments:
        wallpaper_to_move_index (int): The current 0-based index of the wallpaper source
                                       to be moved.
        wallpaper_position (int): The 0-based index of the desired new position for the source.
                                  If less than 0, it moves to the beginning.
                                  If greater than the number of available sources, it moves to the end.
    """
    config_file_path = _get_config_path()
    config = _read_config()
    managed_sources = config.get('managed_sources', []) 

    if not managed_sources:
        sys.stderr.write("Error: No managed wallpaper sources configured. Please add sources first.\n")
        return

    if not (0 <= wallpaper_to_move_index < len(managed_sources)):
        sys.stderr.write(f"Error: Source index to move ({wallpaper_to_move_index}) is out of range. "
                         f"Valid indices are 0 to {len(managed_sources) - 1}.\n")
        return

    wallpaper_to_be_moved = managed_sources.pop(wallpaper_to_move_index)
    sys.stderr.write(f"Removed '{wallpaper_to_be_moved}' from index {wallpaper_to_move_index}.\n")

    final_insert_position = wallpaper_position

    if final_insert_position < 0:
        final_insert_position = 0
        sys.stderr.write(f"Adjusting target position to beginning (0) as {wallpaper_position} is negative.\n")

    elif final_insert_position > len(managed_sources):
        final_insert_position = len(managed_sources)
        sys.stderr.write(f"Adjusting target position to end ({len(managed_sources)}) as {wallpaper_position} is too large.\n")

    managed_sources.insert(final_insert_position, wallpaper_to_be_moved)
    sys.stderr.write(f"Inserted '{wallpaper_to_be_moved}' at new index {final_insert_position}.\n")

    config['managed_sources'] = managed_sources
    _write_config(config, config_file_path)

    sys.stderr.write("Managed wallpaper sources reordered successfully and saved to configuration.\n")
