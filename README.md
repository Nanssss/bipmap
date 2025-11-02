# bipmap
Kindly reminder script that beeps every few seconds so you don’t forget to look at the minimap during your League of Legends games, for bad players only :)

## Setup

Make sure Python is installed on your system.

1. Create and activate a virtual environment:
```bash
python -m venv .venv

# On windows
.venv\Scripts\activate

# On Linux/macOS
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The configuration is stored in `config.txt`.
- You **must specify the path to your sound file**.
- Easiest approach: name your sound `beep.wav` and put it in the `bipmap` folder.

Other settings like **volume** and **delay** can be edited in this file or at runtime via the CLI.
