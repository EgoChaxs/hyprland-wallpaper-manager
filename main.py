import argparse
import sys

from hyperland import hyprland_setup
from config import initialise_json, _read_config, _get_config_path, _write_config
from source_management import (
    _add_managed_source,
    _remove_managed_source,
    list_sources,
    clean_invalid_sources,
    move_source
)
from wallpaper_logic import (
    set_wallpaper,
    set_next_wallpaper,
    set_previous_wallpaper,
    set_random_wallpaper,
    _get_current_wallpaper_path,
    toggle_slideshow,
    start_slideshow,
    stop_slideshow,
    _slideshow_thread,
)


def main():
    """
    Main entry point for the Hyprland Wallpaper CLI application.
    Initializes configuration, parses command-line arguments, and
    dispatches to the appropriate wallpaper management functions.
    """

    #No hyprland no program. No config file no program.
    hyprland_setup()
    initialise_json()

    parser = argparse.ArgumentParser(
        prog='wallpaper',
        description='A command-line tool to manage wallpapers for Hyprland.'
    )

    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
    )

    # --- Command: set ---
    set_parser = subparsers.add_parser(
        'set',
        help='Set a specific wallpaper from a file path.'
    )
    set_parser.add_argument(
        'path',
        type=str,
        help='The absolute path to the wallpaper image file.'
    )

    set_parser.add_argument(
    '--monitor',
    type=str,
    help="Target monitor(s) by number (e.g., '0', '1-3', '0,2')."
    )

    # --- Command: set-next ---
    set_next_parser = subparsers.add_parser(
        'set-next',
        help='Set the next wallpaper in sequence.'
    )

    # --- Command: set-prev ---
    set_prev_parser = subparsers.add_parser(
        'set-prev',
        help='Set the previous wallpaper in sequence.'
    )

    # --- Command: set-rand ---
    set_rand_parser = subparsers.add_parser(
        'set-rand',
        help='Set a random wallpaper from the available sources.'
    )

    # --- Command: add-source ---
    add_source_parser = subparsers.add_parser(
        'add-source',
        help='Adds a directory or file path to managed wallpaper sources.'
    )
    add_source_parser.add_argument(
        'path',
        type=str,
        help='The absolute path to the directory or file to add.'
    )

    # --- Command: remove-source ---
    remove_source_parser = subparsers.add_parser(
        'remove-source',
        help='Removes a directory or file path from managed wallpaper sources.'
    )
    remove_source_parser.add_argument(
        'path',
        type=str,
        help='The absolute path to the directory or file to remove.'
    )

    # --- Command: move-source ---
    move_source_parser = subparsers.add_parser(
        'move-source',
        help='Changes position of specified source to the specified index.'
    )

    move_source_parser.add_argument(
        'source_index',
        type=int,
        help='Index of source to be moved.'
    )

    move_source_parser.add_argument(
        'source_new_pos',
        type=int,
        help='Index of source new position (Negative Index -> Position 0, Index out of range -> Last position).'
    )

    # --- Command: get-curr ---
    get_curr_parser = subparsers.add_parser(
        'get-curr',
        help='Gets current wallpaper path.'
    )

    # --- Command: list-sources ---
    list_sources_parser = subparsers.add_parser(
        'list-sources',
        help='Lists all currently managed wallpaper sources.'
    )

    # --- Command: clean-sources ---
    clean_sources_parser = subparsers.add_parser(
        'clean-sources',
        help='Removes all non-existent paths from managed sources.'
    )

    # --- Parent command: slideshow ---
    slideshow_parser = subparsers.add_parser(
        'slideshow',
        help='Control the automatic wallpaper slideshow.'
    )
    slideshow_subparsers = slideshow_parser.add_subparsers(
        dest='slideshow_command',
        help='Commands for slideshow control.'
    )

    # --- Command: slideshow on ---
    slideshow_on_parser = slideshow_subparsers.add_parser(
        'on',
        help='Activate the slideshow. It will start with the next wallpaper rotation.'
    )

    # --- Command: slideshow off ---
    slideshow_off_parser = slideshow_subparsers.add_parser(
        'off',
        help='Deactivate the slideshow. It will stop at the end of the current rotation.'
    )

    # --- Command: slideshow interval ---
    slideshow_interval_parser = slideshow_subparsers.add_parser(
        'interval',
        help='Set the slideshow interval in seconds.'
    )
    slideshow_interval_parser.add_argument(
        'seconds',
        type=int,
        help='The interval in seconds (e.g., 30 for 30 seconds, 600 for 10 minutes).'
    )

    # --- Command: slideshow order ---
    slideshow_order_parser = slideshow_subparsers.add_parser(
        'order',
        help='Set the wallpaper rotation order for the slideshow.'
    )
    slideshow_order_group = slideshow_order_parser.add_mutually_exclusive_group(required=True)
    slideshow_order_group.add_argument(
        '--random',
        action='store_true',
        help='Set slideshow to pick wallpapers in random order.'
    )
    slideshow_order_group.add_argument(
        '--sequential',
        action='store_true',
        help='Set slideshow to pick wallpapers in sequential order.'
    )

    # --- Command: slideshow start ---
    slideshow_start_parser = slideshow_subparsers.add_parser(
        'start',
        help='Immediately start the slideshow thread. Checks if slideshow is active in config.'
    )

    # --- Command: slideshow stop ---
    slideshow_stop_parser = slideshow_subparsers.add_parser(
        'stop',
        help='Immediately stop the running slideshow thread.'
    )

    # --- DEBUGGING START ---
    #sys.argv = ["main.py", "move-source", "2", "0"]#, "--monitor", "0"]
    #sys.argv = ["main.py", "set", "~/Pictures/dark-japanese-style-4k.jpeg"]#, "--monitor", "0"]
    # --- DEBUGGING END ---

    # --- Parse the arguments ---
    args = parser.parse_args()

    # Beautiful if section :D
    if args.command == 'set':
        # check if user is trying to use a source from the sources list
        wallpaper_path = args.path.strip()
        if wallpaper_path.isdigit():
            source_number = int(wallpaper_path) # not index, starts at 1
            available_sources = list_sources()
            if source_number <= 0 or source_number > len(available_sources):
                sys.stderr.write(f"Error: The number you entered is outside of range. The number of sources is {len(available_sources)}.\n")
            else:
                set_wallpaper(available_sources[source_number - 1], monitor_target=args.monitor)
        else:
            set_wallpaper(wallpaper_path, monitor_target=args.monitor)

    elif args.command == 'set-next':
        set_next_wallpaper()

    elif args.command == 'set-prev':
        set_previous_wallpaper()

    elif args.command == 'set-rand':
        set_random_wallpaper()

    elif args.command == 'add-source':
        _add_managed_source(args.path)

    elif args.command == 'remove-source':
        _remove_managed_source(args.path)

    elif args.command == 'move-source':
        move_source(args.source_index, args.source_new_pos)

    elif args.command == 'get-curr':
        print(_get_current_wallpaper_path())

    elif args.command == 'list-sources':
        sources = list_sources()
        if sources:
            sys.stdout.write("Managed wallpaper sources:\n")
            for i, source in enumerate(sources):
                sys.stdout.write(f"  {i+1}. {source}\n")
        else:
            sys.stdout.write("No wallpaper sources currently managed. Use 'add-source <path>' to add some.\n")

    elif args.command == 'clean-sources':
        clean_invalid_sources()

    # slideshow section
    elif args.command == 'slideshow':
        if args.slideshow_command == 'on':
            toggle_slideshow(enable=True)
            start_slideshow()

        elif args.slideshow_command == 'off':
            toggle_slideshow(enable=False)
            stop_slideshow()

        elif args.slideshow_command == 'interval':
            toggle_slideshow(interval=args.seconds)
            
            if _slideshow_thread and _slideshow_thread.is_alive():
                sys.stdout.write("Note: If slideshow is running, restart it ('slideshow stop' then 'slideshow start') for the new interval to take effect.\n")

        elif args.slideshow_command == 'order':
            if args.random:
                toggle_slideshow(random_order=True)
            elif args.sequential:
                toggle_slideshow(random_order=False)

            if _slideshow_thread and _slideshow_thread.is_alive():
                sys.stdout.write("Note: If slideshow is running, restart it ('slideshow stop' then 'slideshow start') for the new order to take effect.\n")

        elif args.slideshow_command == 'start':
            start_slideshow()

        elif args.slideshow_command == 'stop':
            stop_slideshow()

        else:
            slideshow_parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()