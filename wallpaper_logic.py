import pathlib
import subprocess
import threading
import random
import sys
from config import _read_config, _write_config, _get_config_path, DEFAULT_CONFIG_STRUCTURE

#GLOBAL
_slideshow_stop_event = threading.Event()
_slideshow_thread: threading.Thread = None
_current_slideshow_index: int = 0

SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

def _get_all_available_wallpapers() -> list[str]:
    """
    Purpose: Collects all image files from the managed sources directories.

    Returns:
        list[str]: A list of absolute paths (as strings) to available wallpaper images.
    """

    available_wallpapers = []
    config = _read_config()
    managed_sources = config.get('managed_sources', [])

    if not managed_sources:
        sys.stderr.write("No managed wallpaper sources configured. Please add sources.\n")
        return []

    for source_path_str in managed_sources:
        source_path = pathlib.Path(source_path_str)

        if not source_path.exists():
            sys.stderr.write(f"Warning: Managed source '{source_path_str}' does not exist. Skipping.\n")
            continue

        #single file + supported -> add directly
        if source_path.is_file():
            if source_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                if source_path.as_posix() not in available_wallpapers:
                    available_wallpapers.append(source_path.as_posix())
            else:
                sys.stderr.write(f"Warning: File '{source_path_str}' is not a supported image type. Skipping.\n")
            continue

        #if it is a directory, find images in it
        if source_path.is_dir():
            for item in source_path.rglob('*'):
                if item.is_file() and item.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                    if item.as_posix() not in available_wallpapers:
                        available_wallpapers.append(item.as_posix())
        #cases where path exists but is neither a file or directory
        else:
            sys.stderr.write(f"Warning: Managed source '{source_path_str}' is not a file or directory. Skipping.\n")

    if not available_wallpapers:
        sys.stderr.write("No supported wallpaper images found in the configured sources.\n")

    return available_wallpapers


def _get_current_wallpaper_path() -> str:
    """
    Purpose: Retrieves the path of the currently set wallpaper from the configuration.

    Returns:
        str: The path of the current wallpaper, or an empty string "" if none is set.
    """

    current_config = _read_config()

    if current_config.get('current_wallpaper') is not None:
        return current_config['current_wallpaper']
    else:
        sys.stderr.write("No current wallpaper path found in configuration.")
        return ""


def _slideshow_loop_thread_target() -> None:
    """
    Purpose: This function runs in a separate thread and manages the wallpaper slideshow.
             It continuously picks and sets wallpapers based on the configured interval
             and managed sources until a stop signal is received.
    """

    sys.stderr.write("Slideshow thread started.\n")

    #to avoid setting the same wallpaper (immediate repeats if small list)
    last_wallpaper_path = ""

    while not _slideshow_stop_event.is_set():

        current_config = _read_config()
        slideshow_active = current_config.get('slideshow_active', False)
        slideshow_interval = current_config.get('slideshow_interval', 30)
        slideshow_random_order = current_config.get('slideshow_random_order', True)
    
    #Get wallpapers and ask user to add if there are none otherwise thread cannot continue
        #thread running but slideshow is false -> stop thread
        if not slideshow_active:
            sys.stderr.write("Slideshow deactivated via config. Stopping thread.\n")
            break

        #get wallpapers
        available_wallpapers = _get_all_available_wallpapers()

        #if there are no wallpapers, we wait for user to add but we dont stop thread
        if not available_wallpapers:
            sys.stderr.write("No wallpapers found in managed sources. Waiting for wallpapers...\n")
            _slideshow_stop_event.wait(slideshow_interval)
            continue

    #Wallpaper selection
        next_wallpaper = None

        #RANDOM WALLPAPER SETTING
        if slideshow_random_order:
            #attempt to avoid repeats if number of wallpapers exceeds 1
            if len(available_wallpapers) > 1:
                potential_wallpapers = [wp for wp in available_wallpapers if wp != last_wallpaper_path]
                
                if potential_wallpapers:
                    next_wallpaper = random.choice(potential_wallpapers)
                else:
                    next_wallpaper = random.choice(available_wallpapers)

            else:
                next_wallpaper = available_wallpapers[0]
            
            _current_slideshow_index = 0 #always start with first wallpaper for sequential when in random

        #SEQUENTIAL WALLPAPER SETTING
        else:
            if _current_slideshow_index >= len(available_wallpapers) or _current_slideshow_index < 0:
                _current_slideshow_index = 0

            next_wallpaper = available_wallpapers[_current_slideshow_index]
            #increment index for next iteration + wrap around
            _current_slideshow_index = (_current_slideshow_index + 1) % len(available_wallpapers)

        if next_wallpaper:
            set_wallpaper(next_wallpaper)
            last_wallpaper_path = next_wallpaper
        else:
            sys.stderr.write("Could not select a wallpaper. Make sure you have added wallpapers!\n")

        _slideshow_stop_event.wait(slideshow_interval)
    
    sys.stderr.write("Slideshow thread stopped\n")


def stop_slideshow() -> None:
    """
    Purpose: Stops the wallpaper slideshow thread gracefully.
    """
    global _slideshow_thread, _slideshow_stop_event

    if _slideshow_thread and _slideshow_thread.is_alive():
        sys.stderr.write("Signaling slideshow thread to stop...\n")
        _slideshow_stop_event.set()

        #wait for thread to finish with timeout (prevent infinite blocking)
        _slideshow_thread.join(timeout=5)

        if _slideshow_thread.is_alive():
            sys.stderr.write("Warning: Slideshow thread did not terminate gracefully within timeout.\n")
        else:
            sys.stderr.write("Slideshow thread successfully stopped.\n")
    else:
        sys.stderr.write("Slideshow is not running.\n")


def start_slideshow() -> None:
    """
    Purpose: Starts the wallpaper slideshow in a separate thread.
             Ensures only one slideshow thread is running at a time.
    """

    global _slideshow_thread, _slideshow_stop_event, _current_slideshow_index

    #make sure any existing slideshow thread is stopped
    if _slideshow_thread and _slideshow_thread.is_alive():
        sys.stderr.write("Slideshow is already running. Stopping existing thread before restarting.\n")
        stop_slideshow()

    #reset stop event for fresh start
    _slideshow_stop_event.clear()
    #reset slideshow index just in case
    _current_slideshow_index = 0

    sys.stderr.write("Attempting to start slideshow...\n")

    #read config to confirm slideshow is active
    current_config = _read_config()
    if not current_config.get('slideshow_active', False):
        sys.stderr.write("Slideshow is not enabled in the configuration. Use 'toggle_slideshow(True)' first.\n")
        return

    #create thread
    _slideshow_thread = threading.Thread(target=_slideshow_loop_thread_target, name="SlideshowThread")
    _slideshow_thread.daemon = True

    #start thread
    _slideshow_thread.start()
    sys.stderr.write("Slideshow thread successfully started in background.\n")


def toggle_slideshow(enable: bool = None, interval: int = None, random_order: bool = None) -> None:
    """
    Purpose:
        Manages all slideshow configuration settings (active state, interval, and order).
        Only settings for which a non-None argument is provided will be updated.

    Arguments:
        enable (bool, optional): True to activate slideshow, False to deactivate. Defaults to None.
        interval (int, optional): The interval in seconds for the slideshow rotation. Must be a positive integer (min 5 seconds). Defaults to None.
        random_order (bool, optional): True for random order, False for sequential order. Defaults to None.
    """
    config_file_path = _get_config_path()
    current_config = _read_config()

    changes_made = False

    if enable is not None:
        if current_config['slideshow_active'] != enable:
            current_config['slideshow_active'] = enable
            sys.stderr.write(f"Slideshow active status set to: {enable}\n")
            changes_made = True

    if interval is not None:
        if not isinstance(interval, int) or interval <= 0:
            sys.stderr.write("Warning: Invalid interval provided. Interval must be a positive integer. Setting not updated.\n")
        elif interval < 5:
            sys.stderr.write("Warning: Provided interval is too short. Setting minimum 5 seconds.\n")
            if current_config['slideshow_interval'] != 5:
                current_config['slideshow_interval'] = 5
                changes_made = True
        elif current_config['slideshow_interval'] != interval:
            current_config['slideshow_interval'] = interval
            sys.stderr.write(f"Slideshow interval set to {interval} seconds.\n")
            changes_made = True

    if random_order is not None:
        if current_config['slideshow_random_order'] != random_order:
            current_config['slideshow_random_order'] = random_order
            sys.stderr.write(f"Slideshow order set to: {'RANDOM' if random_order else 'SEQUENTIAL'}\n")
            changes_made = True

    if changes_made:
        _write_config(current_config, config_file_path)
        sys.stderr.write("Slideshow configuration updated.\n")
    else:
        sys.stderr.write("No changes made to slideshow configuration.\n")


def set_wallpaper(path: str) -> None:

    wallpaper_path = pathlib.Path(path)

    if not wallpaper_path.exists():
        sys.stderr.write(f"Error: Wallpaper file does not exist at '{path}'.\n")
        return

    #check if the path provided is a file
    if not wallpaper_path.is_file():
        sys.stderr.write(f"Error: Path '{path}' is a directory, not a file. Please provide a file path.\n")
        return

    sys.stderr.write(f"Attempting to set wallpaper to '{path}'...\n")

    #Common default monitor name
    monitor_name = "DP-1"

    command1 = [
        "hyprctl",
        "hyprpaper",
        "preload",
        f"{wallpaper_path.as_posix()}"
    ]

    command2 = [
        "hyprctl",
        "hyprpaper",
        "wallpaper",
        f"{monitor_name},{wallpaper_path.as_posix()}"
    ]

    try:
        result1 = subprocess.run(
            command1,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        result2 = subprocess.run(
            command2,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        sys.stderr.write(f"Successfully set wallpaper to '{path}' on monitor '{monitor_name}'.\n")

    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Error setting wallpaper with hyprctl:\n")
        sys.stderr.write(f"  Command: {' '.join(e.cmd)}\n")
        sys.stderr.write(f"  Exit Code: {e.returncode}\n")
        sys.stderr.write(f"  hyprctl stdout: {e.stdout}\n")
        sys.stderr.write(f"  hyprctl stderr: {e.stderr}\n")
        return

    except FileNotFoundError:
        sys.stderr.write("Error: 'hyprctl' command not found.\n")
        return

    except Exception as e:
        sys.stderr.write(f"An unexpected error occurred during wallpaper setting: {e}\n")
        return

    config_file_path = _get_config_path()
    current_config = _read_config()

    current_config['current_wallpaper'] = path
    _write_config(current_config, config_file_path)

    sys.stderr.write(f"Wallpaper set to '{path}' succesfully.\n")


def set_next_wallpaper() -> None:
    """
    Purpose:
        Sets the next wallpaper in the sequence of managed sources.
        It finds the current wallpaper, determines its position in the
        list of available wallpapers, and then sets the subsequent one,
        wrapping around to the beginning if the current wallpaper is the last.
    """

    config_file_path = _get_config_path()
    config = _read_config()
    current_wp = config.get('current_wallpaper')

    available_wallpapers = _get_all_available_wallpapers()

    if not available_wallpapers:
        sys.stderr.write("No managed wallpaper sources found. Cannot set next wallpaper.\n")
        return
    if len(available_wallpapers) == 1:
        sys.stderr.write("Only one wallpaper available. Cannot 'advance' to the next one.\n")
        return

    current_wp_index = -1
    if current_wp:
        try:
            current_wp_index = available_wallpapers.index(current_wp)
        except ValueError:
            sys.stderr.write(f"Current wallpaper '{current_wp}' is not in managed sources. "
                             f"Picking first available wallpaper as a starting point.\n")
            current_wp_index = -1

    next_wp_index = (current_wp_index + 1) % len(available_wallpapers)
    next_wallpaper_path = available_wallpapers[next_wp_index]

    set_wallpaper(next_wallpaper_path)
    config['current_wallpaper'] = next_wallpaper_path
    _write_config(config, config_file_path)

    sys.stderr.write(f"Wallpaper set to: {next_wallpaper_path}\n")


def set_previous_wallpaper() -> None:
    """
    Purpose:
        Sets the previous wallpaper in the sequence of managed sources.
        It finds the current wallpaper, determines its position in the
        list of available wallpapers, and then sets the antecedent one,
        wrapping around to the end if the current wallpaper is the first.
    """

    config_file_path = _get_config_path()
    config = _read_config()
    current_wp = config.get('current_wallpaper')

    available_wallpapers = _get_all_available_wallpapers()

    if not available_wallpapers:
        sys.stderr.write("No managed wallpaper sources found. Cannot set next wallpaper.\n")
        return
    if len(available_wallpapers) == 1:
        sys.stderr.write("Only one wallpaper available. Cannot 'advance' to the next one.\n")
        return
    
    current_wp_index = -1
    if current_wp:
        try:
            current_wp_index = available_wallpapers.index(current_wp)
        except ValueError:
            sys.stderr.write(f"Current wallpaper '{current_wp}' is not in managed sources. "
                             f"Picking last available wallpaper as a starting point.\n")
            current_wp_index = 0

    previous_wp_index = (current_wp_index - 1) % len(available_wallpapers)
    previous_wallpaper_path = available_wallpapers[previous_wp_index]

    set_wallpaper(previous_wallpaper_path)
    config['current_wallpaper'] = previous_wallpaper_path
    _write_config(config, config_file_path)

    sys.stderr.write(f"Wallpaper set to: {previous_wallpaper_path}\n")


def set_random_wallpaper() -> None:
    """
    Purpose:
        Selects a random wallpaper path from the list of all available
        managed wallpapers and sets it as the current system wallpaper.
    """
    config_file_path = _get_config_path()
    config = _read_config()

    available_wallpapers = _get_all_available_wallpapers()

    if not available_wallpapers:
        sys.stderr.write("Error: No available wallpapers found in managed sources to set randomly.\n")
        return

    random_wallpaper_path = random.choice(available_wallpapers)

    set_wallpaper(random_wallpaper_path)

    config['current_wallpaper'] = random_wallpaper_path
    _write_config(config, config_file_path)

    sys.stderr.write(f"Wallpaper set to random image: {random_wallpaper_path}\n")