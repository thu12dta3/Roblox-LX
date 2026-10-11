# Shared build flags; requires the three pinned source directory variables.
sdk="$darling_src/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk"
flags=(-target x86_64-apple-darwin -mmacosx-version-min=11.0 -isysroot /usr/libexec/darling -fblocks -std=c++17 -fno-objc-arc -nostdinc++
  -I "$darling_src/src/external/libcxx/include" -isystem "$sdk/usr/include"
  -F "$sdk/System/Library/Frameworks" -F "$sdk/System/Library/PrivateFrameworks"
  -I "$darling_src/src/external/cocotron/CoreGraphics/include" -I "$darling_src/src/frameworks/CoreServices/include"
  -I "$metal_src/include" -I "$metal_src/private-include" -I "$indium_src/include" -I "$indium_src/private-include" -idirafter /usr/include
  -DDARLING_METAL_ENABLED=1 -DDARLING -DPLATFORM_MacOSX -DTARGET_OS_WASI=0 -Wno-nullability-completeness -Wno-availability -Wno-deprecated-declarations)
