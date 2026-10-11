# Separate Darling Metal source patch

This directory's source patch is MPL-2.0 covered software, separate from ROBLOX-LX's proprietary application. Existing notices and upstream license texts are preserved. New bridge files carry their own MPL-2.0 notices. The root proprietary LICENSE is unchanged. Indium is an external 0BSD dependency; no Indium source is copied here. Linking the separate runtime uses the installed Darling Foundation, libobjc, libc++ and libindium; preserve their distribution notices if packaging these dependencies.

Pinned sources:
- Darling Metal: ae20248dc144beab899e38752f5a530f28a0ea56
- Darling header checkout: 60ba801decee7a00782f74f6be4c8ffb013f79ff
- Indium: 8423a7d2f053167030d2bc4a227f96243c740667

Initialize the Darling header submodules: corefoundation (including swift-corelibs-foundation), foundation, libc, libclosure, libcxx, libdispatch, libplatform, objc4, xnu, libpthread, architecture, libmalloc, libxpc, security, cfnetwork, cocotron and dyld. These are headers needed to compile the framework; no OpenGL renderer is built.

Run `bash packaging/darling-metal/build.sh METAL_SOURCE DARLING_SOURCE INDIUM_SOURCE OUTPUT_DIRECTORY`. The script checks revisions, applies the patch, compiles all Metal translation units and links against the installed runtime. It never installs packages or replaces system files. Use `robloxlx metal-test --metal-library OUTPUT_DIRECTORY/Metal` to execute the independent GPU buffer test. Build requires Clang, LLD, the installed Darling runtime, and its exact LLVM 18 dependency. Tested target: x86_64. Other targets and GPU models remain UNKNOWN.

The framework uses its output path as its Mach-O install name, so moving it requires rebuilding. No DYLD injection or client binary patch is used. Window presentation, Metal shader coverage and Roblox compatibility are not established by the buffer test.

## macOS Vulkan window fixture

Pass the fifth argument `src/robloxlx/compatibility/fixtures/macho_window.mm` to `build.sh` to build `OUTPUT_DIRECTORY/window-probe` as well. It uses native SDL only through Darling's ELF loader interface; SDL2 or SDL2-compat must be installed by the user. No SDL or Indium source is bundled in the fixture or wheel.

`robloxlx window-test --executable OUTPUT_DIRECTORY/window-probe --wsi wayland` selects the Wayland instance extension and SDL driver for this subprocess. Use `--wsi x11` for X11/XWayland. The patched Metal initialization enables only the requested WSI extension plus VK_KHR_surface. The existing offscreen Metal test retains its original extension set. These settings do not change system configuration.

See `docs/VULKAN_WINDOW.md` for the complete implementation boundary and executed evidence.
