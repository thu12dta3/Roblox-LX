/* Original ROBLOX-LX probe. Calls public Metal APIs; requires no Apple SDK. */
typedef void *Object;
typedef void *Selector;
typedef struct { unsigned long location, length; } Range;
extern Object MTLCreateSystemDefaultDevice(void);
extern Selector sel_registerName(const char *);
extern void objc_msgSend(void);
extern int printf(const char *, ...);
extern int puts(const char *);
extern int fflush(void *);

static Object send(Object object, const char *name) {
    return ((Object (*)(Object, Selector))objc_msgSend)(object, sel_registerName(name));
}

static void action(Object object, const char *name) {
    ((void (*)(Object, Selector))objc_msgSend)(object, sel_registerName(name));
}

static int failed(const char *api) {
    printf("METAL_API_FAILED:%s\n", api);
    return 1;
}

int main(void) {
    puts("METAL_API_BEGIN:MTLCreateSystemDefaultDevice");
    fflush((void *)0);
    Object device = MTLCreateSystemDefaultDevice();
    if (!device) return failed("MTLCreateSystemDefaultDevice returned nil");
    Object name = send(device, "name");
    const char *text = (const char *)send(name, "UTF8String");
    printf("METAL_DEVICE:%s\n", text ? text : "UNKNOWN");
    Object queue = send(device, "newCommandQueue");
    if (!queue) return failed("newCommandQueue returned nil");
    Object buffer = ((Object (*)(Object, Selector, unsigned long, unsigned long))objc_msgSend)(
        device, sel_registerName("newBufferWithLength:options:"), 256, 0);
    if (!buffer) return failed("newBufferWithLength:options: returned nil");
    unsigned char *bytes = (unsigned char *)send(buffer, "contents");
    if (!bytes) return failed("MTLBuffer.contents returned NULL");
    for (unsigned long i = 0; i < 256; ++i) bytes[i] = 0;
    Object command = send(queue, "commandBuffer");
    if (!command) return failed("commandBuffer returned nil");
    Object encoder = send(command, "blitCommandEncoder");
    if (!encoder) return failed("blitCommandEncoder returned nil");
    puts("METAL_API_BEGIN:fillBuffer:range:value:");
    fflush((void *)0);
    ((void (*)(Object, Selector, Object, Range, unsigned char))objc_msgSend)(
        encoder, sel_registerName("fillBuffer:range:value:"), buffer, (Range){0, 256}, 0x5a);
    action(encoder, "endEncoding");
    action(command, "commit");
    action(command, "waitUntilCompleted");
    unsigned long status = ((unsigned long (*)(Object, Selector))objc_msgSend)(
        command, sel_registerName("status"));
    if (status != 4) return failed("MTLCommandBuffer.status is not Completed");
    for (unsigned long i = 0; i < 256; ++i)
        if (bytes[i] != 0x5a) return failed("MTLBlitCommandEncoder buffer contents mismatch");
    action(buffer, "release");
    action(queue, "release");
    puts("ROBLOXLX_METAL_BUFFER_OK");
    return 0;
}
