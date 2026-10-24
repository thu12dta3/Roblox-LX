# Roadmap

## Current foundation
- [x] Remove the macOS/Darling client route and its experimental framework, fixtures, and documentation.
- [x] Keep the project focused on traditional Linux desktop diagnostics.
- [x] Preserve the independent Vulkan host smoke test and its unit coverage.
- [x] Document the difference between host capability checks and actual Roblox compatibility.

## Next
- [ ] Run the full unit suite and static checks on every change.
- [ ] Test the Vulkan smoke command on real Wayland and X11 hardware configurations.
- [ ] Improve GPU/driver reporting across NVIDIA, AMD, and Intel without treating missing tools as a hard failure.
- [ ] Define a concrete Linux-native compatibility approach before implementing a launcher or client integration.
- [ ] Keep the compatibility matrix evidence-based; do not claim gameplay support until independently demonstrated.

## Explicitly out of scope
- macOS client, Darling, Metal bridges, and macOS framework shims.
- Client modification, injection, anti-cheat bypass, or protocol spoofing.
- Claims that a successful Vulkan smoke test proves Roblox is playable.
