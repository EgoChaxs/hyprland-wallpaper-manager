import argparse
import sys
import time

from config import initialise_json, _read_config

from source_management import (
    _add_managed_source, 
    _remove_managed_source, 
    list_sources, 
    clean_invalid_sources
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
)sqws


def main():
    #without config file program is doomed.
    initialise_json()

    parser = argparse.ArgumentParser(
        prog='wallpaper'
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

    # --- Command: set-next ---
    set_parser = subparsers.add_parser(
        'set-next',
        help='Set the next wallpaper in sequence.'
    )

    # --- Command: set-prev ---
    set_parser = subparsers.add_parser(
        'set-prev',
        help='Set the previous wallpaper in sequence.'
    )

    # --- Command: set-rand ---
    set_parser = subparsers.add_parser(
        'set-rand',
        help='Set a random wallpaper from the available sources.'
    )

    # --- Command: add-wallpaper ---
    set_parser = subparsers.add_parser(
        'add-wallpaper',
        help='Adds a wallpaper to the available options.'
    )

    set_parser.add_argument(
        'path',
        type=str,
        help='The absolute path to the wallpaper image file.'
    )

    # --- Command: remove-wallpaper ---
    set_parser = subparsers.add_parser(
        'remove-wallpaper',
        help='Removes a wallpaper from the available options.'
    )

    set_parser.add_argument(
        'path',
        type=str,
        help='The absolute path to the wallpaper image file.'
    )

    # --- Command: get-curr ---
    set_parser = subparsers.add_parser(
        'get-curr',
        help='Gets current wallpaper path.'
    )

    # --- Command: list-sources ---
    set_parser = subparsers.add_parser(
        'list-sources',
        help='Lists every available wallpaper.'
    )

    # --- Command: clean-sources ---
    set_parser = subparsers.add_parser(
        'clean-sources',
        help='Checks if there are faulty sources and removes them.'
    )


    # Beautiful 'if' section :D

    args = parser.parse_args()

    if args.command == 'set':
        set_wallpaper(args.path)

    if args.command == 'set-next':
        set_next_wallpaper()

    if args.command == 'set-prev':
        set_previous_wallpaper()

    if args.command == 'set-rand':
        set_random_wallpaper()

    if args.command == 'add-wallpaper':
        _add_managed_source()

    if args.command == 'remove-wallpaper':
        _remove_managed_source()

    if args.command == 'get-curr':
        print(_get_current_wallpaper_path())

    if args.command == 'list-sources':
        for src in list_sources():
            print(src)

    if args.command == 'clean-sources':
        clean_invalid_sources()

if __name__ == "__main__":
    main()