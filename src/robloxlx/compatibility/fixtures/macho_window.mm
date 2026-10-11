/* Original ROBLOX-LX independent macOS WSI probe. No Roblox/client code.
 * Creates a native SDL Vulkan window through Darling's documented ELF bridge,
 * uploads a buffer filled by real Metal GPU commands, and presents it.
 * This is WSI infrastructure testing, not an AppKit/CAMetalLayer implementation.
 */
#import <Metal/Metal.h>
#import <Metal/MTLDeviceInternal.h>
#import <Metal/MTLBufferInternal.h>
#include <indium/device.private.hpp>
#include <indium/buffer.private.hpp>
#include <indium/instance.private.hpp>
namespace Indium::DynamicVK { extern PFN_vkGetInstanceProcAddr vkGetInstanceProcAddr; }
#include <elfcalls.h>
#include <vector>
#include <algorithm>
#include <stdexcept>
#include <cstdio>
#include <cstring>
extern "C" struct elf_calls* _elfcalls;

static void vkCheck(VkResult result, const char* api) {
    if (result != VK_SUCCESS) throw std::runtime_error(std::string(api) + " returned " + std::to_string(result));
}
template<class T> static T host(void* library, const char* name) {
    auto pointer = reinterpret_cast<T>(_elfcalls->dlsym(library, name));
    if (!pointer) throw std::runtime_error(std::string("SDL API absent: ") + name);
    return pointer;
}
template<class T> static T vk(const char* name) {
    auto pointer = reinterpret_cast<T>(Indium::DynamicVK::vkGetInstanceProcAddr(Indium::globalInstance, name));
    if (!pointer) throw std::runtime_error(std::string("Vulkan API absent: ") + name);
    return pointer;
}
#define VK_CALL(name) vk<PFN_##name>(#name)

int main() {
    int outcome = 1;
    void* library = nullptr;
    void* window = nullptr;
    bool videoInitialized = false;
    VkSurfaceKHR surface = VK_NULL_HANDLE;
    VkSwapchainKHR swapchain = VK_NULL_HANDLE;
    VkCommandPool pool = VK_NULL_HANDLE;
    VkSemaphore acquired = VK_NULL_HANDLE, rendered = VK_NULL_HANDLE;
    VkFence fence = VK_NULL_HANDLE;
    VkDevice logical = VK_NULL_HANDLE;
    id<MTLDevice> metalDevice = nil;
    id<MTLCommandQueue> metalQueue = nil;
    id<MTLBuffer> metalBuffer = nil;
    @autoreleasepool {
        try {
            library = _elfcalls->dlopen("libSDL2-2.0.so.0");
            if (!library) throw std::runtime_error("libSDL2-2.0.so.0 not loadable");
            auto init = host<int(*)(unsigned)>(library, "SDL_InitSubSystem");
            auto error = host<const char*(*)()>(library, "SDL_GetError");
            if (init(0x20) != 0) throw std::runtime_error(std::string("SDL video: ") + error());
            videoInitialized = true;
            auto create = host<void*(*)(const char*, int, int, int, int, unsigned)>(library, "SDL_CreateWindow");
            window = create("ROBLOX-LX | macOS Metal to Vulkan WSI test", 0x2fff0000, 0x2fff0000, 640, 480, 0x10000000 | 4);
            if (!window) throw std::runtime_error(std::string("SDL Vulkan window: ") + error());
            auto videoDriver = host<const char*(*)()>(library, "SDL_GetCurrentVideoDriver");
            printf("WSI_VIDEO_DRIVER:%s\n", videoDriver()); fflush(stdout);
            auto extensions = host<int(*)(void*, unsigned*, const char**)>(library, "SDL_Vulkan_GetInstanceExtensions");
            unsigned extensionCount = 0;
            if (!extensions(window, &extensionCount, nullptr)) throw std::runtime_error(error());
            std::vector<const char*> names(extensionCount);
            if (!extensions(window, &extensionCount, names.data())) throw std::runtime_error(error());
            for (auto name: names) printf("WSI_REQUIRED_EXTENSION:%s\n", name);
            metalDevice = MTLCreateSystemDefaultDevice();
            if (!metalDevice) throw std::runtime_error("MTLCreateSystemDefaultDevice returned nil");
            auto device = std::dynamic_pointer_cast<Indium::PrivateDevice>(((MTLDeviceInternal*)metalDevice).device);
            logical = device->device();
            printf("WSI_DEVICE:%s\n", device->name().c_str()); fflush(stdout);
            auto createSurface = host<int(*)(void*, VkInstance, VkSurfaceKHR*)>(library, "SDL_Vulkan_CreateSurface");
            puts("WSI_API_BEGIN:SDL_Vulkan_CreateSurface"); fflush(stdout);
            if (!createSurface(window, Indium::globalInstance, &surface)) throw std::runtime_error(std::string("SDL surface: ") + error());
            VkBool32 supported = VK_FALSE;
            vkCheck(VK_CALL(vkGetPhysicalDeviceSurfaceSupportKHR)(device->physicalDevice(), device->graphicsQueueFamilyIndex().value(), surface, &supported), "vkGetPhysicalDeviceSurfaceSupportKHR");
            if (!supported) throw std::runtime_error("Indium graphics queue does not support this surface");
            VkSurfaceCapabilitiesKHR caps{};
            vkCheck(VK_CALL(vkGetPhysicalDeviceSurfaceCapabilitiesKHR)(device->physicalDevice(), surface, &caps), "vkGetPhysicalDeviceSurfaceCapabilitiesKHR");
            if (!(caps.supportedUsageFlags & VK_IMAGE_USAGE_TRANSFER_DST_BIT)) throw std::runtime_error("Surface lacks transfer-destination support");
            unsigned formatCount = 0;
            vkCheck(VK_CALL(vkGetPhysicalDeviceSurfaceFormatsKHR)(device->physicalDevice(), surface, &formatCount, nullptr), "vkGetPhysicalDeviceSurfaceFormatsKHR");
            std::vector<VkSurfaceFormatKHR> formats(formatCount);
            vkCheck(VK_CALL(vkGetPhysicalDeviceSurfaceFormatsKHR)(device->physicalDevice(), surface, &formatCount, formats.data()), "vkGetPhysicalDeviceSurfaceFormatsKHR");
            auto format = formats.end();
            for (auto it = formats.begin(); it != formats.end(); ++it)
                if (it->format == VK_FORMAT_B8G8R8A8_UNORM || it->format == VK_FORMAT_R8G8B8A8_UNORM) { format = it; break; }
            if (format == formats.end()) throw std::runtime_error("Surface lacks supported RGBA8 format");
            VkExtent2D size = caps.currentExtent;
            if (size.width == UINT32_MAX) {
                int width, height;
                host<void(*)(void*,int*,int*)>(library,"SDL_Vulkan_GetDrawableSize")(window,&width,&height);
                size = {static_cast<unsigned>(width),static_cast<unsigned>(height)};
                size.width = std::max(caps.minImageExtent.width,std::min(size.width,caps.maxImageExtent.width));
                size.height = std::max(caps.minImageExtent.height,std::min(size.height,caps.maxImageExtent.height));
            }
            if (!size.width || !size.height) throw std::runtime_error("Surface has zero extent");
            unsigned count = caps.minImageCount + 1;
            if (caps.maxImageCount && count > caps.maxImageCount) count = caps.maxImageCount;
            VkCompositeAlphaFlagBitsKHR alpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;
            if (!(caps.supportedCompositeAlpha & alpha)) {
                alpha = static_cast<VkCompositeAlphaFlagBitsKHR>(caps.supportedCompositeAlpha & (~caps.supportedCompositeAlpha + 1));
            }
            VkSwapchainCreateInfoKHR info{};
            info.sType = VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR;
            info.surface = surface; info.minImageCount = count; info.imageFormat = format->format;
            info.imageColorSpace = format->colorSpace; info.imageExtent = size; info.imageArrayLayers = 1;
            info.imageUsage = VK_IMAGE_USAGE_TRANSFER_DST_BIT; info.imageSharingMode = VK_SHARING_MODE_EXCLUSIVE;
            info.preTransform = caps.currentTransform; info.compositeAlpha = alpha;
            info.presentMode = VK_PRESENT_MODE_FIFO_KHR; info.clipped = VK_TRUE;
            vkCheck(VK_CALL(vkCreateSwapchainKHR)(logical,&info,nullptr,&swapchain),"vkCreateSwapchainKHR");
            puts("WSI_SWAPCHAIN_CREATED"); fflush(stdout);
            unsigned imageCount = 0;
            vkCheck(VK_CALL(vkGetSwapchainImagesKHR)(logical,swapchain,&imageCount,nullptr),"vkGetSwapchainImagesKHR");
            std::vector<VkImage> images(imageCount);
            vkCheck(VK_CALL(vkGetSwapchainImagesKHR)(logical,swapchain,&imageCount,images.data()),"vkGetSwapchainImagesKHR");
            metalQueue = [metalDevice newCommandQueue];
            const size_t byteCount = static_cast<size_t>(size.width)*size.height*4;
            metalBuffer = [metalDevice newBufferWithLength:byteCount options:MTLResourceStorageModeShared];
            if (!metalQueue || !metalBuffer) throw std::runtime_error("Metal queue/buffer allocation failed");
            auto command = [metalQueue commandBuffer];
            auto encoder = [command blitCommandEncoder];
            [encoder fillBuffer:metalBuffer range:NSMakeRange(0,byteCount) value:0x5a];
            [encoder endEncoding]; [command commit]; [command waitUntilCompleted];
            if ([command status] != 4) throw std::runtime_error("Metal GPU fill did not complete");
            auto pixels = static_cast<unsigned char*>([metalBuffer contents]);
            for (size_t i=0;i<byteCount;i++) if(pixels[i]!=0x5a) throw std::runtime_error("Metal pixel verification failed");
            auto rawBuffer = ((MTLBufferInternal*)metalBuffer).buffer;
            // The pinned Indium newBuffer implementation constructs PrivateBuffer.
            // Darwin RTTI identity is not coalesced between this Mach-O executable
            // and the installed dylib: dynamic_cast returns null despite matching
            // runtime type names. Validate that type before the internal cast.
            if (!rawBuffer || strcmp(typeid(*rawBuffer).name(), typeid(Indium::PrivateBuffer).name()) != 0)
                throw std::runtime_error("Unexpected Metal backing buffer type");
            auto buffer = std::static_pointer_cast<Indium::PrivateBuffer>(rawBuffer);
            puts("WSI_METAL_PIXELS_VERIFIED"); fflush(stdout);
            VkCommandPoolCreateInfo poolInfo{}; poolInfo.sType=VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO;
            poolInfo.queueFamilyIndex=device->graphicsQueueFamilyIndex().value(); poolInfo.flags=VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
            vkCheck(VK_CALL(vkCreateCommandPool)(logical,&poolInfo,nullptr,&pool),"vkCreateCommandPool");
            VkCommandBufferAllocateInfo alloc{}; alloc.sType=VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO;
            alloc.commandPool=pool; alloc.level=VK_COMMAND_BUFFER_LEVEL_PRIMARY; alloc.commandBufferCount=1;
            VkCommandBuffer commands;
            vkCheck(VK_CALL(vkAllocateCommandBuffers)(logical,&alloc,&commands),"vkAllocateCommandBuffers");
            VkSemaphoreCreateInfo semaphoreInfo{}; semaphoreInfo.sType=VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO;
            vkCheck(VK_CALL(vkCreateSemaphore)(logical,&semaphoreInfo,nullptr,&acquired),"vkCreateSemaphore");
            vkCheck(VK_CALL(vkCreateSemaphore)(logical,&semaphoreInfo,nullptr,&rendered),"vkCreateSemaphore");
            VkFenceCreateInfo fenceInfo{}; fenceInfo.sType=VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;
            vkCheck(VK_CALL(vkCreateFence)(logical,&fenceInfo,nullptr,&fence),"vkCreateFence");
            for (unsigned frame=0;frame<30;frame++) {
                host<void(*)()>(library,"SDL_PumpEvents")();
                unsigned index;
                auto result=VK_CALL(vkAcquireNextImageKHR)(logical,swapchain,3000000000ULL,acquired,VK_NULL_HANDLE,&index);
                if(result!=VK_SUCCESS && result!=VK_SUBOPTIMAL_KHR) vkCheck(result,"vkAcquireNextImageKHR");
                vkCheck(VK_CALL(vkResetCommandPool)(logical,pool,0),"vkResetCommandPool");
                VkCommandBufferBeginInfo begin{}; begin.sType=VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO;
                vkCheck(VK_CALL(vkBeginCommandBuffer)(commands,&begin),"vkBeginCommandBuffer");
                VkImageMemoryBarrier barrier{}; barrier.sType=VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
                barrier.oldLayout=VK_IMAGE_LAYOUT_UNDEFINED; barrier.newLayout=VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL;
                barrier.srcQueueFamilyIndex=barrier.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;
                barrier.image=images[index]; barrier.subresourceRange={VK_IMAGE_ASPECT_COLOR_BIT,0,1,0,1};
                barrier.dstAccessMask=VK_ACCESS_TRANSFER_WRITE_BIT;
                VK_CALL(vkCmdPipelineBarrier)(commands,VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT,VK_PIPELINE_STAGE_TRANSFER_BIT,0,0,nullptr,0,nullptr,1,&barrier);
                VkBufferMemoryBarrier sourceBarrier{};
                sourceBarrier.sType=VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER;
                sourceBarrier.srcAccessMask=VK_ACCESS_TRANSFER_WRITE_BIT; sourceBarrier.dstAccessMask=VK_ACCESS_TRANSFER_READ_BIT;
                sourceBarrier.srcQueueFamilyIndex=sourceBarrier.dstQueueFamilyIndex=VK_QUEUE_FAMILY_IGNORED;
                sourceBarrier.buffer=buffer->buffer(); sourceBarrier.size=VK_WHOLE_SIZE;
                VK_CALL(vkCmdPipelineBarrier)(commands,VK_PIPELINE_STAGE_TRANSFER_BIT,VK_PIPELINE_STAGE_TRANSFER_BIT,0,0,nullptr,1,&sourceBarrier,0,nullptr);
                VkBufferImageCopy region{}; region.imageSubresource={VK_IMAGE_ASPECT_COLOR_BIT,0,0,1}; region.imageExtent={size.width,size.height,1};
                VK_CALL(vkCmdCopyBufferToImage)(commands,buffer->buffer(),images[index],VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL,1,&region);
                barrier.oldLayout=VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL; barrier.newLayout=VK_IMAGE_LAYOUT_PRESENT_SRC_KHR;
                barrier.srcAccessMask=VK_ACCESS_TRANSFER_WRITE_BIT; barrier.dstAccessMask=0;
                VK_CALL(vkCmdPipelineBarrier)(commands,VK_PIPELINE_STAGE_TRANSFER_BIT,VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT,0,0,nullptr,0,nullptr,1,&barrier);
                vkCheck(VK_CALL(vkEndCommandBuffer)(commands),"vkEndCommandBuffer");
                VkPipelineStageFlags waitStage=VK_PIPELINE_STAGE_TRANSFER_BIT;
                VkSubmitInfo submit{}; submit.sType=VK_STRUCTURE_TYPE_SUBMIT_INFO; submit.waitSemaphoreCount=1;
                submit.pWaitSemaphores=&acquired; submit.pWaitDstStageMask=&waitStage; submit.commandBufferCount=1;
                submit.pCommandBuffers=&commands; submit.signalSemaphoreCount=1; submit.pSignalSemaphores=&rendered;
                vkCheck(VK_CALL(vkQueueSubmit)(device->graphicsQueue(),1,&submit,fence),"vkQueueSubmit");
                VkPresentInfoKHR present{}; present.sType=VK_STRUCTURE_TYPE_PRESENT_INFO_KHR; present.waitSemaphoreCount=1;
                present.pWaitSemaphores=&rendered; present.swapchainCount=1; present.pSwapchains=&swapchain; present.pImageIndices=&index;
                result=VK_CALL(vkQueuePresentKHR)(device->graphicsQueue(),&present);
                if(result!=VK_SUCCESS && result!=VK_SUBOPTIMAL_KHR) vkCheck(result,"vkQueuePresentKHR");
                vkCheck(VK_CALL(vkWaitForFences)(logical,1,&fence,VK_TRUE,3000000000ULL),"vkWaitForFences");
                vkCheck(VK_CALL(vkQueueWaitIdle)(device->graphicsQueue()),"vkQueueWaitIdle");
                vkCheck(VK_CALL(vkResetFences)(logical,1,&fence),"vkResetFences");
            }
            printf("WSI_PRESENTED:30 frames, %ux%u, verified Metal GPU pixels, Vulkan only\n",size.width,size.height);
            outcome=0;
        } catch(const std::exception& error) {
            fprintf(stderr,"WSI_FAILED:%s\n",error.what());
        }
        if(logical) {
            VK_CALL(vkDeviceWaitIdle)(logical);
            if(fence) VK_CALL(vkDestroyFence)(logical,fence,nullptr);
            if(rendered) VK_CALL(vkDestroySemaphore)(logical,rendered,nullptr);
            if(acquired) VK_CALL(vkDestroySemaphore)(logical,acquired,nullptr);
            if(pool) VK_CALL(vkDestroyCommandPool)(logical,pool,nullptr);
            if(swapchain) VK_CALL(vkDestroySwapchainKHR)(logical,swapchain,nullptr);
        }
        if(surface) VK_CALL(vkDestroySurfaceKHR)(Indium::globalInstance,surface,nullptr);
        [metalBuffer release]; [metalQueue release]; [metalDevice release];
        if(window) host<void(*)(void*)>(library,"SDL_DestroyWindow")(window);
        if(videoInitialized) host<void(*)(unsigned)>(library,"SDL_QuitSubSystem")(0x20);
        // Keep the host library loaded through process exit: SDL may register callbacks.
        if(outcome==0) puts("ROBLOXLX_MACOS_VULKAN_WINDOW_OK");
    }
    fflush(stdout);
    return outcome;
}
