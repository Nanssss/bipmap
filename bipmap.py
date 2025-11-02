import os
import configparser
from threading import Timer
from pygame import mixer
from termcolor import colored
from colorama import init
import drawings

CONFIG_FILE = 'config.txt'



class RepeatTimer:
    """Timer that repeatedly executes a function at a fixed interval."""

    def __init__(self, interval, function, *args, **kwargs):
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self._timer = None
        self.is_running = False
        self.start()

    def _run(self):
        """Internal: run the function, then reschedule."""
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        """Start the repeating timer."""
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.daemon = True  # Avoid blocking program exit
            self._timer.start()
            self.is_running = True

    def stop(self):
        """Stop the repeating timer."""
        if self._timer:
            self._timer.cancel()
        self.is_running = False         



class BeepController:
    """Controller for playing repeated beeps with adjustable volume and delay."""

    def __init__(self, sound, delay, volume):
        """Initialize the beep controller with sound file, delay, and volume."""
        self.sound = sound
        self.delay = delay
        self.volume = volume
        self.paused = False

        mixer.init()
        try:
            mixer.music.load(sound)
        except Exception as e:
            print(colored(f"⚠️  Error loading sound '{sound}': {e}", "red"))
            exit(1)
        
        # Start the repeating timer
        self.timer = RepeatTimer(delay, self.dong)

    def dong(self):
        """Play the beep sound."""
        if not self.paused: 
            mixer.music.set_volume(self.volume / 100.0)  # Volume = [0, 1]
            mixer.music.play()

    def set_volume(self, volume: int):
        """Set the volume for the beep sound."""
        self.volume = volume
        print(colored(f"[INFO] - Volume : {int(self.volume)}%  |  Delay : {self.delay}s\n", "yellow", attrs=["bold"]))

    def set_delay(self, delay: float):
        """Set the delay interval for the beep sound."""
        self.delay = delay
        self.timer.interval = delay # Update timer interval
        print(colored(f"[INFO] - Volume : {int(self.volume)}%  |  Delay : {self.delay}s\n", "yellow", attrs=["bold"]))

    def set_sound(self, sound: str):
        """Set a new sound file for the beep."""
        try:
            self.sound = sound
            mixer.music.load(sound)
            print(colored(f"New sound loaded: {sound}", "yellow"))
        except Exception as e:
            print(colored(f"⚠️  Error loading sound '{sound}': {e}", "red"))
    
    def pause(self):
        """Pause the beep timer."""
        self.paused = True
        print(colored("Timer paused.", "yellow"))

    def resume(self):
        """Resume the beep timer."""
        self.paused = False
        print(colored("Timer resumed.", "green"))

    def stop(self):
        """Stop the beep timer."""
        self.timer.stop()



def load_config():
    """Load config file or create default one if missing."""

    config = configparser.ConfigParser()

    if not os.path.exists(CONFIG_FILE):
        # Create default config
        config["DEFAULT"] = {
            "sound": "beep.wav",
            "delay": "7",
            "volume": "20"
        }
        with open(CONFIG_FILE, "w") as f:
            config.write(f)
    else:
        # Load existing config
        config.read(CONFIG_FILE)

    return config

def print_banner():
    """Display welcome banner with ASCII art."""

    up_border = "#" * 80
    down_border = "-" * 80
    magikarp_art = drawings.bipmap  # Import ASCII art 
    description = "\n\nStay aware of the minimap — for bad players only :)"

    # Display
    print(colored(up_border, "yellow"))
    print(colored(magikarp_art, "red"))
    print(colored(description, "cyan", attrs=["bold"]))
    print(colored(down_border, "yellow"))
    print("\nUsage: Please enter the path to your sound file (wav or mp3) you want to play in config.txt.\n")

def init_app():
    """Initialize terminal, display, sound, and load configuration."""

    init() # Initialize colorama
    os.system("cls" if os.name == "nt" else "clear") # Clear terminal

    # Display welcome message
    print_banner()

    # Load configuration
    config = load_config()
    sound = config["DEFAULT"].get("sound")
    delay = int(config["DEFAULT"].get("delay"))
    volume = int(config["DEFAULT"].get("volume"))

    print(colored(
        "Available commands:\n"
        "   -v <volume (0–100%)>\n"
        "   -d <delay (s)>\n"
        "   -s <sound_file.ext>\n"
        "   quit\n",
        "green",
        attrs=["bold"]
    ))
    print(colored(f"[INFO] - Volume : {int(volume)}%  |  Delay : {delay}s\n", "yellow", attrs=["bold"]))
    return delay, volume, sound, config

def validate_sound(sound_path: str) -> bool:
    """Check if the sound file exists; support relative/absolute paths."""
    if not os.path.isabs(sound_path):
        sound_path = os.path.join(os.path.dirname(__file__), sound_path)
    return os.path.isfile(sound_path)

def main():
    """Main control loop."""
    delay, volume, sound, config = init_app()

    # Check if sound file exists
    if not validate_sound(sound):
        print(colored(f"⚠️  Invalid sound filename/path in {CONFIG_FILE}.", "red"))
        exit(1)

    # Initialize BeepController
    beeper = BeepController(sound, delay, volume)

    while True:
        # Get user command
        cmd=input("> ").strip()
        
        if cmd.startswith("-v "):
            # Set volume command
            try:
                new_volume = int(cmd.split()[1])
                if new_volume > 100 or new_volume < 0:
                    raise ValueError
                beeper.set_volume(new_volume)

                # Update config file
                config["DEFAULT"]["volume"] = str(new_volume)
                with open(CONFIG_FILE, "w") as f:
                    config.write(f)

            except (ValueError, IndexError):
                print(colored("⚠️  Invalid volume value.", "red"))

        elif cmd.startswith("-d "):
            # Set delay command
            try:
                new_delay = int(cmd.split()[1])
                beeper.set_delay(new_delay)

                # Update config file
                config["DEFAULT"]["delay"] = str(new_delay)
                with open(CONFIG_FILE, "w") as f:
                    config.write(f)

            except (ValueError, IndexError):
                print(colored("⚠️  Invalid delay value.", "red"))

        elif cmd.startswith("-s "):
            # Set sound command
            try:
                new_sound = cmd.split(" ", 1)[1]
                validate_sound(new_sound)
                if not validate_sound(new_sound):
                    raise FileNotFoundError
                beeper.set_sound(new_sound)

                # Update config file
                config["DEFAULT"]["sound"] = new_sound
                with open(CONFIG_FILE, "w") as f:
                    config.write(f)

            except Exception:
                print(colored("⚠️  Invalid sound filename/path.", "red"))
        
        elif cmd == "pause":
            # Pause command
            beeper.pause()

        elif cmd == "resume":
            # Resume command
            beeper.resume()
        
        elif cmd in ("exit","exit()", "stop", "stop()", "quit", "quit()", "q"):
            # Exit command
            beeper.stop()
            print(colored("Exiting program.", "yellow", attrs=["bold"]))
            break

        else:
            # Invalid command
            print(colored("⚠️  Invalid command. Try:", "red"))
            print(colored(
                "Available commands:\n"
                "   -v <volume (0–100%)>\n"
                "   -d <delay (s)>\n"
                "   -s <sound_file.ext>\n"
                "   quit\n",
                "green",
                attrs=["bold"]
            ))



if __name__ == "__main__":
    main()
