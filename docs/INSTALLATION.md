# Installation

For development, use Python 3.10+ and install the local package with `python -m pip install -e .`. The CLI itself adds no system dependencies. Optional system probes (`nvidia-smi`, `lspci`, `glxinfo`, `vulkaninfo`) are detected if present.

No Arch package, desktop launcher, Roblox installer, or Wine installation is implemented yet. ROBLOX-LX only detects Wine if the user already installed it and never changes system configuration.
