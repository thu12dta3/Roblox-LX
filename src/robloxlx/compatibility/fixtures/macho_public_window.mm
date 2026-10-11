/* Original independent macOS public API probe. No SDL/Vulkan calls here. */
#import "LXWindow.h"
#include <cstdio>
#include <exception>
#include <stdexcept>
int main() {
    @autoreleasepool {
        NSWindow* window=nil;
        NSWindow* second=nil;
        id<MTLDevice> device=nil;
        id<MTLCommandQueue> queue=nil;
        @try {
            try {
                puts("PUBLIC_API_BEGIN:NSWindow.init"); fflush(stdout);
                window=[[NSWindow alloc] initWithContentRect:NSMakeRect(0,0,640,480)
                         styleMask:1|2|8 backing:2 defer:NO];
                if(!window) throw std::runtime_error("NSWindow allocation failed");
                window.title=@"ROBLOX-LX | NSWindow + CAMetalLayer Vulkan test";
                device=MTLCreateSystemDefaultDevice();
                queue=[device newCommandQueue];
                if(!device || !queue) throw std::runtime_error("Metal device/queue unavailable");
                CAMetalLayer* layer=[CAMetalLayer layer];
                layer.device=device; layer.drawableSize=NSMakeSize(640,480);
                layer.pixelFormat=MTLPixelFormatBGRA8Unorm; layer.framebufferOnly=YES;
                window.contentView.wantsLayer=YES; window.contentView.layer=layer;
                [window makeKeyAndOrderFront:nil];
                puts("PUBLIC_API_BEGIN:nextDrawable.render.present"); fflush(stdout);
                unsigned count=0;
                NSUInteger previousDrawableID=0;
                for(unsigned i=0;i<60;i++) {
                    if(i==30) {
                        [window setContentSize:NSMakeSize(320,240)];
                        layer.drawableSize=NSMakeSize(320,240);
                        puts("PUBLIC_API_RESIZED:320x240"); fflush(stdout);
                    }
                    @autoreleasepool {
                        id<CAMetalDrawable> drawable=[layer nextDrawable];
                        if(!drawable || !drawable.texture) throw std::runtime_error("nextDrawable returned no texture");
                        if(drawable.drawableID<=previousDrawableID) throw std::runtime_error("Drawable IDs are not unique/increasing");
                        previousDrawableID=drawable.drawableID;
                        NSUInteger expectedWidth=i<30?640:320, expectedHeight=i<30?480:240;
                        if(drawable.texture.width!=expectedWidth || drawable.texture.height!=expectedHeight)
                            throw std::runtime_error("Drawable texture dimensions mismatch after resize");
                        auto pass=[MTLRenderPassDescriptor renderPassDescriptor];
                        auto attachment=[pass.colorAttachments objectAtIndexedSubscript:0];
                        attachment.texture=drawable.texture;
                        attachment.loadAction=MTLLoadActionClear; attachment.storeAction=MTLStoreActionStore;
                        attachment.clearColor=MTLClearColorMake((i%30)/30.0,0.25,1.0-(i%30)/30.0,1.0);
                        auto command=[queue commandBuffer];
                        auto encoder=[command renderCommandEncoderWithDescriptor:pass];
                        if(!encoder) throw std::runtime_error("Metal render encoder unavailable");
                        [encoder endEncoding]; [command presentDrawable:drawable]; [command commit];
                        [command waitUntilCompleted];
                        if(command.status!=4) throw std::runtime_error("Render command did not complete");
                        ++count;
                    }
                }
                layer.drawableSize=NSMakeSize(0,0);
                if([layer nextDrawable]!=nil) throw std::runtime_error("Zero-sized layer returned a drawable");
                layer.drawableSize=NSMakeSize(320,240);
                puts("PUBLIC_API_ZERO_SIZE:nil drawable");
                BOOL rejected=NO;
                @try { layer.framebufferOnly=NO; }
                @catch(NSException* error) { rejected=[[error name] isEqualToString:NSInvalidArgumentException]; }
                if(!rejected) throw std::runtime_error("Unsupported framebufferOnly=NO was not rejected");
                rejected=NO;
                @try { layer.pixelFormat=MTLPixelFormatRGBA16Float; }
                @catch(NSException* error) { rejected=[[error name] isEqualToString:NSInvalidArgumentException]; }
                if(!rejected) throw std::runtime_error("Unsupported pixel format was not rejected");
                puts("PUBLIC_API_UNSUPPORTED_OPTIONS:explicitly rejected");
                second=[[NSWindow alloc] initWithContentRect:NSMakeRect(0,0,320,240) styleMask:1|2 backing:2 defer:NO];
                if(!second) throw std::runtime_error("Second NSWindow creation failed");
                second.title=@"ROBLOX-LX | second window lifetime test";
                CAMetalLayer* secondLayer=[CAMetalLayer layer];
                secondLayer.device=device; secondLayer.drawableSize=NSMakeSize(320,240);
                second.contentView.layer=secondLayer; second.contentView.wantsLayer=YES;
                [second makeKeyAndOrderFront:nil];
                @autoreleasepool {
                    auto drawable=[secondLayer nextDrawable];
                    if(!drawable) throw std::runtime_error("Second window nextDrawable failed");
                    auto pass=[MTLRenderPassDescriptor renderPassDescriptor];
                    auto attachment=[pass.colorAttachments objectAtIndexedSubscript:0];
                    attachment.texture=drawable.texture; attachment.loadAction=MTLLoadActionClear;
                    attachment.storeAction=MTLStoreActionStore; attachment.clearColor=MTLClearColorMake(0.1,0.8,0.2,1);
                    auto command=[queue commandBuffer];
                    auto encoder=[command renderCommandEncoderWithDescriptor:pass];
                    if(!encoder) throw std::runtime_error("Second window render encoder failed");
                    [encoder endEncoding]; [command presentDrawable:drawable]; [command commit]; [command waitUntilCompleted];
                    if(command.status!=4) throw std::runtime_error("Second window command incomplete");
                }
                [second close]; [second close];
                if([secondLayer nextDrawable]!=nil) throw std::runtime_error("Closed secondary layer returned a drawable");
                [second release]; second=nil;
                puts("PUBLIC_API_SECOND_WINDOW:rendered and closed");
                [window orderOut:nil]; [window close]; [window close];
                if([layer nextDrawable]!=nil) throw std::runtime_error("Closed layer returned a drawable");
                [queue release]; [device release]; [window release];
                printf("PUBLIC_API_PRESENTED:%u frames via NSWindow/CAMetalLayer/Metal\n",count);
                puts("ROBLOXLX_PUBLIC_WINDOW_OK"); fflush(stdout);
                return 0;
            } catch(const std::exception& error) {
                fprintf(stderr,"PUBLIC_API_FAILED:%s\n",error.what());
            }
        } @catch(NSException* error) {
            fprintf(stderr,"PUBLIC_API_EXCEPTION:%s\n",[[error reason] UTF8String]);
        }
        [second close]; [second release]; [window close]; [queue release]; [device release]; [window release];
    }
    return 1;
}
