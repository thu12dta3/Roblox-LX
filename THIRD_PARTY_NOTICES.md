# Third-party notices

No third-party source code is included in ROBLOX-LX 0.1.0. Python runtime/library components are used from the Python standard library.

Research references (not bundled or incorporated):

- Darling: GPL-3.0 project; consult per-component notices before any integration or distribution.
- Darling Metal: MPL-2.0 notices in upstream source; runtime framework is an external dependency, not included in the Python wheel. Separately licensed source modifications are provided in `packaging/darling-metal/metal-vulkan.patch`; MPL-2.0 and other upstream notices are preserved in that directory.
- Indium/Iridium: upstream Indium repository declares 0BSD; used only through the installed external Darling runtime. No source copied.
- MacOBlox: its public repository identifies the project as MIT licensed. Its source has not been copied into ROBLOX-LX. Review every file and license before any future reuse.
- Wine: upstream identifies the source as LGPL licensed; no Wine code is included.

Using an external runtime is distinct from copying/linking its source. Any future distribution or source integration needs a component-level license review; this notice is not a legal determination that the requested proprietary notice supersedes third-party terms.
