import pathlib
import subprocess
import sys

def hyprpaper_setup() -> None:
    """
    Purpose:
        Verifies if the necessary hyprpaper configuration exists. If it does not,
        it prompts the user to automatically create the setup files and run
        the initial commands. This ensures that the program can interact with
        Hyprpaper for dynamic wallpaper changes.
    """
    sys.stderr.write("Verifying Hyprpaper is set up correctly...\n")

    hypr_config_path = pathlib.Path.home() / ".config" / "hypr" / "hyprpaper.conf"

    config_is_valid = False
    if hypr_config_path.exists():
        try:
            with open(hypr_config_path, 'r') as file:
                content = file.read().replace(' ', '')
                if "ipc=true" in content:
                    config_is_valid = True
        except IOError:
            pass

    if config_is_valid:
        sys.stderr.write("Hyprpaper is ready to go.\n")
        return

    sys.stderr.write("Hyprpaper is misconfigured or incomplete.\n")
    sys.stderr.write("Do you want to automatically setup the hyprpaper.conf file and run Hyprpaper? (y/n)\n")

    try:
        user_input = input()
    except EOFError:
        sys.stderr.write("Cannot prompt for user input in non-interactive session. Skipping setup.\n")
        return

    if user_input[0].lower() == "n":
        sys.stderr.write("Skipping Hyprpaper setup. Program may not function as intended.\n")
        return

    if user_input[0].lower() == "y":
        sys.stderr.write("Setting up Hyprpaper...\n")

        try:
            sys.stderr.write("  -> Creating hyprpaper.conf file...\n")
            hypr_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(hypr_config_path, 'w') as file:
                file.write('ipc=true\n')

            """Not required
            sys.stderr.write("  -> Enabling and starting hyprpaper systemd service...\n")
            subprocess.run(
                ['systemctl', '--user', 'enable', '--now', 'hyprpaper'],
                check=True,
                capture_output=True,
                text=True
            )
            """

            sys.stderr.write("  -> Launching hyprpaper process...\n")
            subprocess.Popen(['hyprpaper'])

            sys.stderr.write("\nSetup complete!\n")
            sys.stderr.write("You must now add 'exec-once=hyprpaper &' to your ~/.config/hypr/hyprland.conf file.\n")
            sys.stderr.write("Please restart Hyprland for this change to take effect.\n")

        except subprocess.CalledProcessError as e:
            sys.stderr.write("Error during Hyprpaper setup. A command failed.\n")
            sys.stderr.write(f"  Command: {' '.join(e.cmd)}\n")
            sys.stderr.write(f"  Return Code: {e.returncode}\n")
            sys.stderr.write(f"  Output: {e.stderr}\n")
            sys.stderr.write("Please try running the commands manually or check your system configuration.\n")
        except Exception as e:
            sys.stderr.write(f"An unexpected error occurred during setup: {e}\n")
    else:
        sys.stderr.write("Invalid input. Skipping Hyprpaper setup. Program may not function as intended.\n")
        return
