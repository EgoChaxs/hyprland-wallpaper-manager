import pathlib
import json
import sys

DEFAULT_CONFIG_STRUCTURE = {
    "managed_sources": [],
    "current_wallpaper": None,
    "slideshow_active": False,
    "slideshow_interval": None,
    "slideshow_random_order": True,
    "slideshow_index": 0
}

def _get_config_path() -> pathlib.Path:
    """
    Purpose: Returns the pathlib.Path object for the configuration file and creates it if it does not exist.

    Returns:
        pathlib.Path: The path to the configuration file.
    """

    home_dir = pathlib.Path.home()
    config_dir = home_dir / ".config" / "hypr_wallpaper_app"
    config_file = config_dir / "config.json"

    try:
        #check if file's parents exist and creates them if not
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_file
    except OSError as e:
        #stop program if file can not be created
        sys.stderr.write(f"CRITICAL ERROR: Failed to create config directory {config_dir}: {e}\n")
        sys.exit(1)


def _write_config(data: dict, file_path: pathlib.Path) -> None:
    """
    Purpose: Writes the provided config data dictionary back to config.json.

    Arguments:
        data (dict): The dictionary containing the configuration to write.
        pathlib.Path: Path to the configuration file.
    """

    try:
        with open(file_path, "w", encoding="utf-8") as file_to_write:
            json.dump(data, file_to_write, indent=4)
    except OSError as e:
        sys.stderr.write(f"Error writing config to {file_path}: {e}\n")


def _read_config() -> dict:
    """
    Purpose:
        Reads the current application configuration from config.json.
        Returns a dictionary representing the config.
        Handles: If the file doesn't exist or is malformed, it returns a default config dictionary.

    Returns:
        dict: A dictionary containing the configuration data or the default structure if errors occur
    """

    config_file = _get_config_path()

    try:
        with open(config_file, "r", encoding="utf-8") as file:
            loaded_data = json.load(file)
        
        return loaded_data

    except json.JSONDecodeError:
        sys.stderr.write("Config file is corrupted or malformed JSON. Using default configuration.\n")
        return DEFAULT_CONFIG_STRUCTURE

    except FileNotFoundError:
        sys.stderr.write(f"Config file not found at {config_file}. Using default configuration.\n")
        return DEFAULT_CONFIG_STRUCTURE

    except OSError as e:
        sys.stderr.write(f"Error reading config file at {config_file}: {e}. Using default configuration.\n")
        return DEFAULT_CONFIG_STRUCTURE


def initialise_json():
    full_path = _get_config_path()

    if full_path.exists():
        try:
            with open(full_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            default_keys = DEFAULT_CONFIG_STRUCTURE.keys()
            loaded_keys = data.keys()
            if set(loaded_keys) != set(default_keys):
                sys.stderr.write("Config file structure incorrect, overwriting with default structure...\n")
                _write_config(DEFAULT_CONFIG_STRUCTURE, full_path)
                sys.stderr.write("Config file structure overwritten.\n")

        except json.JSONDecodeError:
            sys.stderr.write("Config file is corrupted.\n")
            _write_config(DEFAULT_CONFIG_STRUCTURE, full_path)
            sys.stderr.write("Config file overwritten due to corruption.\n")

        except OSError as e:
            sys.stderr.write(f"Error reading config file: {e}. Overwriting with default structure\n")
            _write_config(DEFAULT_CONFIG_STRUCTURE, full_path)
            sys.stderr.write("Config file overwritten due to read error.\n")

    else:
        sys.stderr.write("Config file not found, creating with default structure.\n")
        _write_config(DEFAULT_CONFIG_STRUCTURE, full_path)
        sys.stderr.write("Config file created with default structure.\n")