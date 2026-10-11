// SPDX-FileCopyrightText: 2026 Bannaman6655 Productions
// SPDX-License-Identifier: LicenseRef-Proprietary
// Experimental, limited macOS API implementation for independent programs.
#import <Foundation/Foundation.h>
#import <Metal/Metal.h>

@interface CALayer : NSObject
@property NSRect frame;
@property NSRect bounds;
+ (instancetype)layer;
@end

@protocol CAMetalDrawable <MTLDrawable>
@property(readonly) id<MTLTexture> texture;
@end

@interface CAMetalLayer : CALayer
@property(retain) id<MTLDevice> device;
@property NSSize drawableSize;
@property MTLPixelFormat pixelFormat;
@property BOOL framebufferOnly;
- (id<CAMetalDrawable>)nextDrawable;
@end

@interface NSView : NSObject
- (instancetype)initWithFrame:(NSRect)frame;
@property NSRect frame;
@property BOOL wantsLayer;
@property(retain) CALayer* layer;
@end

@interface NSWindow : NSObject
- (instancetype)initWithContentRect:(NSRect)rect styleMask:(NSUInteger)style
                           backing:(NSUInteger)backing defer:(BOOL)defer;
@property(copy) NSString* title;
@property(retain) NSView* contentView;
- (void)makeKeyAndOrderFront:(id)sender;
- (void)orderOut:(id)sender;
- (void)setContentSize:(NSSize)size;
- (void)close;
@end
