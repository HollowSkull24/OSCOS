# OSCOS — Oscillation Control System

OSCOS is a desktop application for controlling and acquiring data from an experimental mechanical oscillation rig. It provides real-time control, telemetry visualization, and synchronized image capture using Basler cameras.

## Overview

Key features:

- Real-time motor control (RPM and control parameters)
- Telemetry acquisition and visualization (speed, acceleration, peaks)
- Synchronized image capture with metadata
- Signal processing modules (filtering, peak detection)
- Export telemetry and metadata as CSV

The application is written in Python and uses PyQt5 for the GUI. The codebase is organized to separate UI, controllers, core processing and worker threads.

## Quick start

There are two common ways to run OSCOS:

### 1) Use the prebuilt binaries (no Python setup required)

Run the appropriate bundled executable for your platform.

Linux:

```bash
./bin/linux/OSCOS
```

Windows (double-click `OSCOS.exe` or run from PowerShell/CMD):

```powershell
.\bin\windows\OSCOS.exe
```

These executables include the runtime and dependencies so end users can run the application without installing Python packages.

### 2) Run from source (for development)

Requirements:

- Python 3.8 or newer
- pip

Recommended: create and activate a virtual environment before installing dependencies.

Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application from the project root:

```bash
python src/oscos/main.py
```

## Dependencies

All Python dependencies are declared in `requirements.txt`. Example entries:

```
numpy<2.3.0
opencv_python_headless==4.12.0.88
Pillow==12.1.0
pypylon==4.2.0
PyQt5==5.15.11
pyqt5_sip==12.17.2
pyqtgraph==0.14.0
pyserial==3.5
```

## Project layout

```
OSCOS/
├── bin/                # Prebuilt executables for Linux and Windows
├── src/oscos/          # Application source code
│   ├── main.py
│   ├── ui/
│   ├── controllers/
│   ├── core/
│   └── workers/
├── docs/               # Full documentation and manual (LaTeX)
├── requirements.txt
└── README.md
```

## Documentation

Full user and developer documentation is under `docs/`. The main manual is `docs/Manual.tex` and a compiled PDF may be present as `docs/manual.pdf`.
## Usage notes and recommendations

- Use the prebuilt binaries for end-users who only need to run the app.
- Run from source when developing or debugging.
- Always use a virtual environment for Python development.

## Troubleshooting

- If serial ports are not visible on Linux, add your user to the `dialout` group:

```bash
sudo usermod -a -G dialout $USER
```

- If `pypylon` or camera drivers fail to install, consult Basler's documentation and verify the camera is connected.
