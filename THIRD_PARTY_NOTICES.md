# Third-party notices

No third-party source code is included in ROBLOX-LX 0.1.0. Python runtime/library components are used from the Python standard library.

Research references (not bundled or incorporated):

- Darling: GPL-3.0 project; consult per-component notices before any integration or distribution.
- Darling Metal: MPL-2.0 notices in upstream source; runtime framework is an external dependency, not included in the Python wheel. Separately licensed source modifications are provided in `packaging/darling-metal/metal-vulkan.patch`; MPL-2.0 and other upstream notices are preserved in that directory.
- Indium/Iridium: upstream Indium repository declares 0BSD; used only through the installed external Darling runtime. No source copied.
- MacOBlox: its public repository identifies the project as MIT licensed. Its source has not been copied into ROBLOX-LX. Review every file and license before any future reuse.
- Wine: upstream identifies the source as LGPL licensed; no Wine code is included.

Using an external runtime is distinct from copying/linking its source. Any future distribution or source integration needs a component-level license review; this notice is not a legal determination that the requested proprietary notice supersedes third-party terms.

- Window probe: native SDL2/SDL2-compat (zlib license), an external host dependency accessed through Darling ELF calls. No SDL source/library is bundled. The original fixture includes external Darling Metal/Indium headers at build time; it is not copied from their example programs. No GPL QuartzCore/AppKit source is included.

- Experimental window runtime: original LXWindow source uses the unchanged proprietary project license. The separately supplied IndiumKit patch/source dependency is 0BSD; notices are preserved in `runtime/window/INDIUM_LICENSE`. That compatible permissive source is compiled from its external pinned checkout into the experimental library. Darling Metal remains a separately licensed dynamic dependency. No GPL AppKit/QuartzCore implementation is copied or linked into LXWindow.
