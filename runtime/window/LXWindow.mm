// SPDX-FileCopyrightText: 2026 Bannaman6655 Productions
// SPDX-License-Identifier: LicenseRef-Proprietary
#import "LXWindow.h"
#import <Metal/MTLDeviceInternal.h>
#import <Metal/MTLTextureInternal.h>
#import <Metal/MTLDrawableInternal.h>
#include <indium-kit/layer.hpp>
#include <indium/device.private.hpp>
#include <indium/instance.private.hpp>
#include <elfcalls.h>
#include <cmath>
#include <atomic>
#include <stdexcept>
extern "C" struct elf_calls* _elfcalls;
namespace Indium::DynamicVK { extern PFN_vkGetInstanceProcAddr vkGetInstanceProcAddr; }

static void* sdlLibrary;
static unsigned videoUsers;
template<class T> static T sdl(const char* name) {
    if(!sdlLibrary) sdlLibrary=_elfcalls->dlopen("libSDL2-2.0.so.0");
    if(!sdlLibrary) throw std::runtime_error("SDL2 host library unavailable");
    auto function=reinterpret_cast<T>(_elfcalls->dlsym(sdlLibrary,name));
    if(!function) throw std::runtime_error(std::string("SDL API unavailable: ")+name);
    return function;
}
static __attribute__((noreturn)) void reject(NSString* message) {
    [NSException raise:NSInvalidArgumentException format:@"%@",message];
    __builtin_unreachable();
}
static void validateSize(NSSize size) {
    if(!std::isfinite(size.width) || !std::isfinite(size.height) ||
       size.width<1 || size.height<1 || size.width>8192 || size.height>8192)
        reject(@"Window dimensions must be finite and between 1 and 8192");
}
@interface CAMetalLayer (LXAttachment)
- (void)lxAttachWindow:(void*)window;
@end
@interface NSView (LXAttachment)
- (void)lxAttachWindow:(void*)window;
@end

@implementation CALayer {
    NSRect _frame;
    NSRect _bounds;
}
@synthesize frame=_frame, bounds=_bounds;
+ (instancetype)layer { return [[[self alloc] init] autorelease]; }
@end

@interface LXMetalDrawable : MTLDrawableInternal <CAMetalDrawable>
- (instancetype)initWithBacking:(std::shared_ptr<IndiumKit::Drawable>)backing device:(id<MTLDevice>)device;
@end
static std::atomic<NSUInteger> nextDrawableID{1};
@implementation LXMetalDrawable {
    id<MTLTexture> _texture;
    NSUInteger _drawableID;
}
- (instancetype)initWithBacking:(std::shared_ptr<IndiumKit::Drawable>)backing device:(id<MTLDevice>)device {
    self=[super initWithDrawable:backing];
    if(self) _drawableID=nextDrawableID.fetch_add(1);
    if(self) _texture=[[MTLTextureInternal alloc] initWithTexture:backing->texture()
              device:device resourceOptions:MTLResourceStorageModePrivate];
    return self;
}
- (id<MTLTexture>)texture { return _texture; }
- (NSUInteger)drawableID { return _drawableID; }
- (CFTimeInterval)presentedTime { reject(@"Compositor presentation timestamps are not implemented"); }
- (void)presentAtTime:(CFTimeInterval)time { reject(@"Timed drawable presentation is not implemented"); }
- (void)presentAfterMinimumDuration:(CFTimeInterval)duration { reject(@"Timed drawable presentation is not implemented"); }
- (void)addPresentedHandler:(MTLDrawablePresentedHandler)handler { reject(@"Compositor presentation callbacks are not implemented"); }
- (void)dealloc { [_texture release]; [super dealloc]; }
@end

@implementation CAMetalLayer {
    id<MTLDevice> _device;
    NSSize _drawableSize;
    MTLPixelFormat _pixelFormat;
    void* _window;
    std::shared_ptr<IndiumKit::Layer> _backing;
}
- (instancetype)init {
    self=[super init];
    if(self) _pixelFormat=MTLPixelFormatBGRA8Unorm;
    return self;
}
- (void)lxReset {
    if(_backing && _device) {
        auto device=std::dynamic_pointer_cast<Indium::PrivateDevice>(((MTLDeviceInternal*)_device).device);
        auto wait=reinterpret_cast<PFN_vkDeviceWaitIdle>(Indium::DynamicVK::vkGetInstanceProcAddr(Indium::globalInstance,"vkDeviceWaitIdle"));
        if(device && wait) wait(device->device());
    }
    _backing.reset();
}
- (void)lxAttachWindow:(void*)window { [self lxReset]; _window=window; }
- (id<MTLDevice>)device { return _device; }
- (void)setDevice:(id<MTLDevice>)device {
    if(device==_device) return;
    [self lxReset]; [device retain]; [_device release]; _device=device;
}
- (NSSize)drawableSize { return _drawableSize; }
- (void)setDrawableSize:(NSSize)size {
    if(!std::isfinite(size.width) || !std::isfinite(size.height) ||
       size.width<0 || size.height<0 || size.width>8192 || size.height>8192)
        reject(@"Drawable dimensions must be finite and between 0 and 8192");
    if(NSEqualSizes(size,_drawableSize)) return;
    [self lxReset]; _drawableSize=size;
}
- (MTLPixelFormat)pixelFormat { return _pixelFormat; }
- (void)setPixelFormat:(MTLPixelFormat)format {
    if(format!=MTLPixelFormatBGRA8Unorm) reject(@"Only BGRA8Unorm swapchain format is currently supported");
    _pixelFormat=format;
}
- (BOOL)framebufferOnly { return YES; }
- (void)setFramebufferOnly:(BOOL)value {
    if(!value) reject(@"Readable/non-framebuffer swapchain textures are not implemented");
}
- (id<CAMetalDrawable>)nextDrawable {
    if(!_window || !_device || _drawableSize.width==0 || _drawableSize.height==0) return nil;
    sdl<void(*)()>("SDL_PumpEvents")();
    int width=0,height=0;
    sdl<void(*)(void*,int*,int*)>("SDL_Vulkan_GetDrawableSize")(_window,&width,&height);
    if(width<1 || height<1) return nil;
    // This subset supports layer pixel size matching the window framebuffer.
    // Arbitrary-sized sublayers require composition and are rejected explicitly.
    if(_drawableSize.width!=width || _drawableSize.height!=height)
        reject(@"drawableSize must match the actual Vulkan window framebuffer");
    if(!_backing) {
        VkSurfaceKHR surface=VK_NULL_HANDLE;
        if(!sdl<int(*)(void*,VkInstance,VkSurfaceKHR*)>("SDL_Vulkan_CreateSurface")(_window,Indium::globalInstance,&surface))
            throw std::runtime_error(sdl<const char*(*)()>("SDL_GetError")());
        try {
            _backing=IndiumKit::Layer::make(surface,((MTLDeviceInternal*)_device).device,width,height);
        } catch(...) {
            auto destroy=reinterpret_cast<PFN_vkDestroySurfaceKHR>(Indium::DynamicVK::vkGetInstanceProcAddr(Indium::globalInstance,"vkDestroySurfaceKHR"));
            if(destroy) destroy(Indium::globalInstance,surface,nullptr);
            throw;
        }
    }
    auto drawable=_backing->nextDrawable();
    if(!drawable) return nil;
    return [[[LXMetalDrawable alloc] initWithBacking:drawable device:_device] autorelease];
}
- (void)dealloc { [self lxReset]; [_device release]; [super dealloc]; }
@end

@implementation NSView {
    NSRect _frame;
    BOOL _wantsLayer;
    CALayer* _layer;
    void* _window;
}
@synthesize frame=_frame;
- (BOOL)wantsLayer { return _wantsLayer; }
- (void)setWantsLayer:(BOOL)value {
    _wantsLayer=value;
    if(value && !_layer) [self setLayer:[CALayer layer]];
}
- (instancetype)initWithFrame:(NSRect)frame {
    self=[super init]; if(self) _frame=frame; return self;
}
- (CALayer*)layer { return _layer; }
- (void)setLayer:(CALayer*)layer {
    if(_layer==layer) return;
    if([_layer isKindOfClass:[CAMetalLayer class]]) [(CAMetalLayer*)_layer lxAttachWindow:nullptr];
    [layer retain]; [_layer release]; _layer=layer;
    if([layer isKindOfClass:[CAMetalLayer class]]) [(CAMetalLayer*)layer lxAttachWindow:_window];
}
- (void)lxAttachWindow:(void*)window {
    _window=window;
    if([_layer isKindOfClass:[CAMetalLayer class]]) [(CAMetalLayer*)_layer lxAttachWindow:window];
}
- (void)dealloc { [self lxAttachWindow:nullptr]; [_layer release]; [super dealloc]; }
@end

@implementation NSWindow {
    void* _window;
    NSString* _title;
    NSView* _contentView;
}
- (instancetype)initWithContentRect:(NSRect)rect styleMask:(NSUInteger)style backing:(NSUInteger)backing defer:(BOOL)defer {
    validateSize(rect.size);
    if(backing!=2) reject(@"Only NSBackingStoreBuffered is implemented");
    if(style & ~((NSUInteger)1|2|4|8)) reject(@"Unsupported NSWindow style mask");
    self=[super init];
    if(self) {
        if(!videoUsers && sdl<int(*)(unsigned)>("SDL_InitSubSystem")(0x20)!=0)
            throw std::runtime_error(sdl<const char*(*)()>("SDL_GetError")());
        _window=sdl<void*(*)(const char*,int,int,int,int,unsigned)>("SDL_CreateWindow")(
            "ROBLOX-LX public macOS API test",0x2fff0000,0x2fff0000,(int)rect.size.width,(int)rect.size.height,
            0x10000000|8|((style&8)?0x20:0));
        if(!_window) {
            if(!videoUsers) sdl<void(*)(unsigned)>("SDL_QuitSubSystem")(0x20);
            [self release]; return nil;
        }
        ++videoUsers;
        _title=[@"ROBLOX-LX public macOS API test" copy];
        _contentView=[[NSView alloc] initWithFrame:NSMakeRect(0,0,rect.size.width,rect.size.height)];
        [_contentView lxAttachWindow:_window];
    }
    return self;
}
- (NSString*)title { return _title; }
- (void)setTitle:(NSString*)title {
    NSString* copy=[title copy]; [_title release]; _title=copy;
    if(_window) sdl<void(*)(void*,const char*)>("SDL_SetWindowTitle")(_window,title?[title UTF8String]:"");
}
- (NSView*)contentView { return _contentView; }
- (void)setContentView:(NSView*)view {
    if(view==_contentView) return;
    [view retain]; [_contentView lxAttachWindow:nullptr]; [_contentView release]; _contentView=view;
    [view lxAttachWindow:_window];
}
- (void)makeKeyAndOrderFront:(id)sender {
    if(_window) { sdl<void(*)(void*)>("SDL_ShowWindow")(_window); sdl<void(*)(void*)>("SDL_RaiseWindow")(_window); }
}
- (void)orderOut:(id)sender { if(_window) sdl<void(*)(void*)>("SDL_HideWindow")(_window); }
- (void)setContentSize:(NSSize)size {
    validateSize(size);
    if(!_window) reject(@"Cannot resize a closed window");
    sdl<void(*)(void*,int,int)>("SDL_SetWindowSize")(_window,(int)size.width,(int)size.height);
    // SDL Wayland sizes are asynchronous. Wait for the actual framebuffer
    // before reporting resize complete; preserve the old layer on timeout.
    bool resized=false;
    for(unsigned attempt=0;attempt<100;attempt++) {
        sdl<void(*)()>("SDL_PumpEvents")();
        int width=0,height=0;
        sdl<void(*)(void*,int*,int*)>("SDL_Vulkan_GetDrawableSize")(_window,&width,&height);
        if(width==(int)size.width && height==(int)size.height) { resized=true; break; }
        sdl<void(*)(unsigned)>("SDL_Delay")(10);
    }
    if(!resized) reject(@"Compositor did not accept the requested framebuffer size within 1 second");
    _contentView.frame=NSMakeRect(0,0,size.width,size.height);
}
- (void)close {
    if(!_window) return;
    [_contentView lxAttachWindow:nullptr];
    sdl<void(*)(void*)>("SDL_DestroyWindow")(_window); _window=nullptr;
    if(--videoUsers==0) sdl<void(*)(unsigned)>("SDL_QuitSubSystem")(0x20);
}
- (void)dealloc { [self close]; [_contentView release]; [_title release]; [super dealloc]; }
@end
