#!/usr/bin/env bash
set -euo pipefail
if (( $# != 5 )); then
  echo 'Usage: build.sh METAL_SOURCE DARLING_SOURCE INDIUM_SOURCE BUILT_METAL OUTPUT_DIRECTORY' >&2
  exit 2
fi
metal_src=$(realpath "$1")
darling_src=$(realpath "$2")
indium_src=$(realpath "$3")
metal_library=$(realpath "$4")
mkdir -p "$5"
output_dir=$(realpath "$5")
runtime_dir=$(cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(cd -- "$runtime_dir/../.." && pwd)
[[ $(git -C "$metal_src" rev-parse HEAD) == ae20248dc144beab899e38752f5a530f28a0ea56 ]]
[[ $(git -C "$darling_src" rev-parse HEAD) == 60ba801decee7a00782f74f6be4c8ffb013f79ff ]]
[[ $(git -C "$indium_src" rev-parse HEAD) == 8423a7d2f053167030d2bc4a227f96243c740667 ]]
if ! git -C "$indium_src" apply --reverse --check "$runtime_dir/indium-kit.patch" 2>/dev/null; then
  git -C "$indium_src" apply --check "$runtime_dir/indium-kit.patch"
  git -C "$indium_src" apply "$runtime_dir/indium-kit.patch"
fi
source "$repo_dir/packaging/darling-metal/sdk-flags.sh"
flags+=(-I "$darling_src/src/startup/mldr/elfcalls" -I "$runtime_dir")
clang++ "${flags[@]}" -c "$indium_src/src/indium-kit/layer.cpp" -o "$output_dir/indium-kit.o"
clang++ "${flags[@]}" -c "$runtime_dir/LXWindow.mm" -o "$output_dir/LXWindow.o"
link_flags=(-target x86_64-apple-darwin -mmacosx-version-min=11.0 -fuse-ld=lld -isysroot /usr/libexec/darling
  -F /usr/libexec/darling/System/Library/Frameworks -L /usr/libexec/darling/usr/lib/darling)
clang++ "${link_flags[@]}" -dynamiclib -install_name "/Volumes/SystemRoot$output_dir/LXWindow" \
  -o "$output_dir/LXWindow" "$output_dir/LXWindow.o" "$output_dir/indium-kit.o" "$metal_library" \
  -lindium -framework Foundation -lobjc -lc++ -lc++abi
clang++ "${flags[@]}" -c "$repo_dir/src/robloxlx/compatibility/fixtures/macho_public_window.mm" -o "$output_dir/public-window.o"
clang++ "${link_flags[@]}" -o "$output_dir/public-window-probe" "$output_dir/public-window.o" \
  "$output_dir/LXWindow" "$metal_library" -lindium -framework Foundation -lobjc -lc++ -lc++abi
sha256sum "$output_dir/LXWindow" "$output_dir/public-window-probe"
