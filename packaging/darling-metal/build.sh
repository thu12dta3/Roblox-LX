#!/usr/bin/env bash
# Build the separate MPL-2.0 Metal runtime; no installation or client changes.
set -euo pipefail
if (( $# < 4 || $# > 5 )); then
  echo 'Usage: build.sh METAL_SOURCE DARLING_SOURCE INDIUM_SOURCE OUTPUT_DIRECTORY [WINDOW_PROBE_SOURCE]' >&2
  exit 2
fi
metal_src=$(realpath "$1")
darling_src=$(realpath "$2")
indium_src=$(realpath "$3")
mkdir -p "$4"
output_dir=$(realpath "$4")
patch_dir=$(cd -- "$(dirname -- "$0")" && pwd)
[[ $(git -C "$metal_src" rev-parse HEAD) == ae20248dc144beab899e38752f5a530f28a0ea56 ]]
[[ $(git -C "$darling_src" rev-parse HEAD) == 60ba801decee7a00782f74f6be4c8ffb013f79ff ]]
[[ $(git -C "$indium_src" rev-parse HEAD) == 8423a7d2f053167030d2bc4a227f96243c740667 ]]
if git -C "$metal_src" apply --reverse --check "$patch_dir/metal-vulkan.patch" 2>/dev/null; then
  echo 'Metal patch already applied'
else
  git -C "$metal_src" apply --check "$patch_dir/metal-vulkan.patch"
  git -C "$metal_src" apply "$patch_dir/metal-vulkan.patch"
fi
sdk="$darling_src/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk"
flags=(-target x86_64-apple-darwin -mmacosx-version-min=11.0 -isysroot /usr/libexec/darling -fblocks -std=c++17 -fno-objc-arc -nostdinc++
  -I "$darling_src/src/external/libcxx/include" -isystem "$sdk/usr/include"
  -F "$sdk/System/Library/Frameworks" -F "$sdk/System/Library/PrivateFrameworks"
  -I "$darling_src/src/external/cocotron/CoreGraphics/include" -I "$darling_src/src/frameworks/CoreServices/include"
  -I "$metal_src/include" -I "$metal_src/private-include" -I "$indium_src/include" -I "$indium_src/private-include" -idirafter /usr/include
  -DDARLING_METAL_ENABLED=1 -DDARLING -DPLATFORM_MacOSX -DTARGET_OS_WASI=0 -Wno-nullability-completeness -Wno-availability -Wno-deprecated-declarations)
objects=()
for source in "$metal_src"/src/Metal/*.mm; do
  object="$output_dir/$(basename "${source%.mm}").o"
  clang++ "${flags[@]}" -c "$source" -o "$object"
  objects+=("$object")
done
clang++ -target x86_64-apple-darwin -mmacosx-version-min=11.0 -fuse-ld=lld -isysroot /usr/libexec/darling -dynamiclib \
  -install_name "/Volumes/SystemRoot$output_dir/Metal" -o "$output_dir/Metal" "${objects[@]}" \
  -F /usr/libexec/darling/System/Library/Frameworks -L /usr/libexec/darling/usr/lib/darling \
  -lindium -framework Foundation -lobjc -lc++ -lc++abi
sha256sum "$output_dir/Metal"

if (( $# == 5 )); then
  clang++ "${flags[@]}" -I "$darling_src/src/startup/mldr/elfcalls" -c "$(realpath "$5")" -o "$output_dir/window-probe.o"
  clang++ -target x86_64-apple-darwin -mmacosx-version-min=11.0 -fuse-ld=lld -isysroot /usr/libexec/darling \
    -o "$output_dir/window-probe" "$output_dir/window-probe.o" "$output_dir/Metal" \
    -F /usr/libexec/darling/System/Library/Frameworks -L /usr/libexec/darling/usr/lib/darling \
    -lindium -framework Foundation -lobjc -lc++ -lc++abi
fi
