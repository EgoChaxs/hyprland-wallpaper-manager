##  Hyprland Wallpaper CLI Manager

A command-line interface tool to easily manage and control wallpapers for the Hyprland compositor. This tool allows you to set specific wallpapers, navigate through your collection, and manage an automatic slideshow.

# Requirements:

This application relies on the hyprpaper wallpaper utility for Hyprland. You must have hyprpaper installed and correctly configured for this tool to function.

To install hyprpaper, use your distribution's package manager:
    - Arch Linux: sudo pacman -S hyprpaper
    - Ubuntu/Debian: sudo apt-get install hyprpaper (or compile from source)

# Setup & Configuration:

This tool can automate the initial setup for you. Simply run the main script. If the hyprpaper.conf file is missing or invalid, the script will prompt you to set it up automatically.

In case of Automation: 
    When you first run a command, you will be asked to automate the setup process. This will:

        - Create the ~/.config/hypr/hyprpaper.conf file.
        - Add 'ipc = true' to the file to enable inter-process communication.
        - Enable and start the hyprpaper systemd user service.
        - Launch hyprpaper in the background.

Manual Hyprland Configuration:
    You must add the following line: 'exec-once = hyprpaper', to your Hyprland configuration file 
    '~/.config/hypr/hyprland.conf' to ensure hyprpaper launches automatically when you start Hyprland.

# Usage

Wallpaper Control:

-> set <path> : Sets a specific wallpaper from a file path.
e.g: python main.py set /home/user/pictures/wallpaper.jpg

-> set-next : Sets the next wallpaper in the managed list.
e.g: python main.py set-next

-> set-prev : Sets the previous wallpaper in the managed list.
e.g: python main.py set-prev

-> set-rand : Sets a random wallpaper from the managed list.
e.g: python main.py set-rand

-> get-curr : Prints the absolute path of the current wallpaper.
e.g: python main.py get-curr

Source Management:

-> add-source <path> : Adds a directory or file path to your managed sources.
e.g: python main.py add-source /home/user/wallpapers

-> remove-source <path> : Removes a managed source.
e.g: python main.py remove-source /home/user/wallpapers 

-> list-sources : Lists all currently managed wallpaper sources.
e.g: python main.py list-sources

-> move-source <current-index> <new-position> : Changes the order of a managed source in the list. (Indexing starts at 0)
e.g: python main.py move-source 2 0

-> clean-sources : Removes all non-existent paths from your managed sources.
e.g: python main.py clean-sources

Slideshow Control:

-> slideshow on : Activates the slideshow mode in the config.
e.g: python main.py slideshow on

-> slideshow off : Deactivates the slideshow mode.
e.g: python main.py slideshow off

-> slideshow interval <seconds> : Sets the rotation interval in seconds.
e.g: python main.py slideshow interval 300 (5 minutes)

-> slideshow order --random : Sets the slideshow to shuffle wallpapers.
e.g: python main.py slideshow order --random

-> slideshow order --sequential : Sets the slideshow to follow a fixed order.
e.g: python main.py slideshow order --sequential

-> slideshow start : Immediately starts the slideshow thread.
e.g: python main.py slideshow start

-> slideshow stop : Immediately stops the slideshow thread.
e.g: python main.py slideshow stop