import pathlib
import subprocess
import sys

def hyprland_setup() -> None:
    """
    Purpose:
        Verifies if the necessary hyprpaper configuration exists. If it does not,
        it prompts the user to automatically create the setup files and run
        the initial commands. This ensures that the program can interact with
        Hyprpaper for dynamic wallpaper changes.
    """
    sys.stderr.write("Verifying hyprland is set up correctly...\n")

    hypr_config_path = pathlib.Path.home() / ".config" / "hypr" / "hyprpaper.conf"
    
    config_is_valid = False
    if hypr_config_path.exists():
        try:
            with open(hypr_config_path, 'r') as file:
                content = file.read()
                if "ipc = true" in content:
                    config_is_valid = True
        except IOError:
            pass

    if config_is_valid:
        sys.stderr.write("Hyprland is ready to go.\n")
        return

    sys.stderr.write("Hyprland setup for hyprpaper is missing or incomplete.\n")
    sys.stderr.write("Do you want to automatically set up the config file and run hyprpaper? (y/n)\n")

    try:
        user_input = input()
    except EOFError:
        sys.stderr.write("Cannot prompt for user input in non-interactive session. Skipping setup.\n")
        return

    if user_input.lower() in ("n", "no"):
        sys.stderr.write("Skipping hyprland setup. Program may not function as intended.\n")
        return
    
    if user_input.lower() in ("y", "yes"):
        sys.stderr.write("Setting up hyprland...\n")
        
        try:
            sys.stderr.write("  -> Creating hyprpaper.conf file...\n")
            hypr_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(hypr_config_path, 'w') as file:
                file.write('ipc = true\n')

            sys.stderr.write("  -> Enabling and starting hyprpaper systemd service...\n")
            subprocess.run(
                ['systemctl', '--user', 'enable', '--now', 'hyprpaper'],
                check=True,
                capture_output=True,
                text=True
            )

            sys.stderr.write("  -> Launching hyprpaper process...\n")
            subprocess.Popen(['hyprpaper'])

            sys.stderr.write("\nSetup complete!\n")
            sys.stderr.write("You must now add 'exec-once = hyprpaper' to your ~/.config/hypr/hyprland.conf file.\n")
            sys.stderr.write("Please restart Hyprland for this change to take effect.\n")

        except subprocess.CalledProcessError as e:
            sys.stderr.write(f"Error during Hyprland setup. A command failed.\n")
            sys.stderr.write(f"  Command: {' '.join(e.cmd)}\n")
            sys.stderr.write(f"  Return Code: {e.returncode}\n")
            sys.stderr.write(f"  Output: {e.stderr}\n")
            sys.stderr.write("Please try running the commands manually or check your system configuration.\n")
        except Exception as e:
            sys.stderr.write(f"An unexpected error occurred during setup: {e}\n")
    else:
        sys.stderr.write("Invalid input. Skipping hyprland setup. Program may not function as intended.\n")
        return