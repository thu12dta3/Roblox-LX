# Roadmap

- [x] Reinspect the ROBLOX-LX code and shift implementation priority to macOS desktop through Darling.
- [x] Audit MacOBlox runtime, graphics, audio, input, network and client-specific changes without copying source.
- [x] Implement read-only dependency diagnostics, Darling discovery, process lifecycle, path mapping, private logs, and launch/dry-run CLI.
- [x] Build an independent x86_64 Mach-O syscall fixture and add a Darling execution integration test.
- [x] Add Arch/Garuda PKGBUILD and document exact UNKNOWN/BLOCKED API observations.
- [ ] Run the independent Mach-O fixture under an already installed Darling runtime and isolated DPREFIX.
- [ ] Add standalone graphics, audio, mouse/keyboard and networking probes; run them only when runtime/device prerequisites exist.
- [ ] Implement narrowly scoped APIs only after independent tests reproduce a missing behavior and license review is complete.
- [ ] Assess the unmodified Roblox macOS executable only after independent API coverage is known and official provenance is verifiable.
- [ ] Test gameplay only with explicit account-risk approval; report process launch separately from an actual playable session.

The current host does not have Darling, so runtime compatibility remains unverified.
