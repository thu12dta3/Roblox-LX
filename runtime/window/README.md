# Experimental macOS window/layer API runtime

Original ROBLOX-LX compatibility code in LXWindow.h/LXWindow.mm remains proprietary, under the unchanged project LICENSE copied here. IndiumKit source is an external 0BSD dependency; its license is preserved in INDIUM_LICENSE and its changes are supplied separately in indium-kit.patch. The build compiles that external source directly from its pinned checkout. Existing Darling Metal changes remain separately MPL-2.0 covered. No GPL AppKit/QuartzCore implementation is copied here.

This library implements a limited subset of NSWindow, NSView, CALayer and CAMetalLayer. It uses real native SDL Vulkan windows, real IndiumKit swapchains, real MTLTexture wrappers and Indium-backed MTLCommandBuffer.presentDrawable. The original public-window fixture has no SDL or Vulkan calls. It creates and renders using these macOS API names.

## Build

Prepare the pinned sources and headers described in packaging/darling-metal/README.md. Also initialize the Darling dyld header submodule (pinned by that checkout to 63f667cf06d7ed59553adebb0c8d70a117135ac9). Build the patched Metal first, then:

```bash
bash runtime/window/build.sh METAL_SOURCE DARLING_SOURCE INDIUM_SOURCE BUILT_METAL OUTPUT_DIRECTORY
PYTHONPATH=src python -m robloxlx.cli window-api-test --executable OUTPUT_DIRECTORY/public-window-probe --wsi wayland
PYTHONPATH=src python -m robloxlx.cli window-api-test --executable OUTPUT_DIRECTORY/public-window-probe --wsi x11
```

These commands require no installation or system changes. The generated library has its output path as Mach-O install name and is a normal link dependency of the independent executable. It is not injected into a client and does not replace installed frameworks. Never co-load this experimental library with another implementation of the same Objective-C classes; that combination has not been implemented or tested.

## Implemented and tested

- NSWindow initWithContentRect:styleMask:backing:defer:, title, contentView, makeKeyAndOrderFront:, orderOut:, setContentSize:, close. Real window creation/show/hide/resize/destruction; second window and idempotent close tested. Buffered backing only. Window origin/defer semantics are not fully implemented; window is created hidden at a compositor-selected position.
- NSView frame, wantsLayer, layer: stores geometry and attaches the layer to its native window. Automatic CALayer creation on wantsLayer=YES. General drawing, subviews and event dispatch are absent.
- CALayer layer/frame/bounds: genuine object and geometry storage. No generic composition, animation or drawing engine.
- CAMetalLayer device, drawableSize, BGRA8Unorm pixelFormat, framebufferOnly=YES, nextDrawable: real swapchain acquisition and Metal texture. Zero-sized layer returns nil. Resize recreates backing after GPU idle. Only a layer filling the framebuffer is supported.
- CAMetalDrawable texture and unique drawableID. Immediate MTLCommandBuffer.presentDrawable delegates to actual Indium presentation. Compositor timestamps, timing and presented callbacks raise explicit exceptions rather than return invented values.
- Unsupported format/framebuffer options raise NSInvalidArgumentException. Other unsupported selectors are not implemented.

## Remaining limitations

This is not a complete AppKit/QuartzCore replacement or a Roblox-compatible framework ABI. Canonical framework installation/linkage, NSApplication event loop, input events, composition, mixed layers, display scaling, full window geometry/delegates/styles, arbitrary drawable sizes, maximumDrawableCount/timeout controls, timed presentation, presentation callbacks, and general swapchain OUT_OF_DATE recovery remain UNKNOWN/pending. Minimized and spontaneous compositor-driven resizes are not validated. Only explicit content resize at the tested scale is covered.

The API test presents 60 changing clear-color frames, resizes 640x480 to 320x240 and renders a second window. It checks texture dimensions, unique IDs, GPU completion, unsupported-option rejection, zero-size behavior, closed-layer behavior and clean teardown. It does not read back compositor pixels, exercise shaders or run Roblox.

IndiumKit corrections include vector size before writing surface formats, image-count bounds, surface/format/queue checks, composite-alpha selection and acceptance of successful VK_SUBOPTIMAL_KHR presentation. Some upstream error paths still abort; failure-path resource cleanup and other hardware remain unverified.
