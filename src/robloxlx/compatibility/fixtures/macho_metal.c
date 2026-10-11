/* Original ROBLOX-LX probe. Calls public Metal APIs; requires no Apple SDK. */
typedef void *Object;
typedef void *Selector;
typedef struct { unsigned long location, length; } Range;
extern Object MTLCreateSystemDefaultDevice(void);
extern Selector sel_registerName(const char *);
extern void objc_msgSend(void);
extern void *objc_autoreleasePoolPush(void);
extern void objc_autoreleasePoolPop(void *);
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
    fflush((void *)0);
    return 1;
}

int main(void) {
    void *pool = objc_autoreleasePoolPush();
    puts("METAL_API_BEGIN:MTLCreateSystemDefaultDevice");
    fflush((void *)0);
    Object device = MTLCreateSystemDefaultDevice();
    if (!device) return failed("MTLCreateSystemDefaultDevice returned nil");
    unsigned char has_name = ((unsigned char (*)(Object, Selector, Selector))objc_msgSend)(
        device, sel_registerName("respondsToSelector:"), sel_registerName("name"));
    if (has_name) {
        Object name = send(device, "name");
        const char *text = (const char *)send(name, "UTF8String");
        printf("METAL_DEVICE:%s\n", text ? text : "UNKNOWN");
    } else {
        puts("METAL_API_MISSING:MTLDevice.name; device name UNKNOWN");
    }
    fflush((void *)0);
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
    Object destination = ((Object (*)(Object, Selector, unsigned long, unsigned long))objc_msgSend)(
        device, sel_registerName("newBufferWithLength:options:"), 256, 0);
    if (!destination) return failed("destination buffer allocation returned nil");
    unsigned char *copied = (unsigned char *)send(destination, "contents");
    if (!copied) return failed("destination contents returned NULL");
    for (unsigned long i = 0; i < 256; ++i) copied[i] = 0;
    Object copy_command = send(queue, "commandBuffer");
    Object copy_encoder = send(copy_command, "blitCommandEncoder");
    if (!copy_command || !copy_encoder) return failed("copy command/encoder returned nil");
    puts("METAL_API_BEGIN:copyFromBuffer:sourceOffset:toBuffer:destinationOffset:size:");
    fflush((void *)0);
    ((void (*)(Object, Selector, Object, unsigned long, Object, unsigned long, unsigned long))objc_msgSend)(
        copy_encoder, sel_registerName("copyFromBuffer:sourceOffset:toBuffer:destinationOffset:size:"),
        buffer, 0, destination, 0, 256);
    action(copy_encoder, "endEncoding");
    action(copy_command, "commit");
    action(copy_command, "waitUntilCompleted");
    unsigned long copy_status = ((unsigned long (*)(Object, Selector))objc_msgSend)(
        copy_command, sel_registerName("status"));
    if (copy_status != 4) return failed("copy command is not Completed");
    for (unsigned long i = 0; i < 256; ++i)
        if (copied[i] != 0x5a) return failed("GPU buffer copy contents mismatch");
    action(destination, "release");
    action(buffer, "release");
    action(queue, "release");
    action(device, "release");
    objc_autoreleasePoolPop(pool);
    puts("ROBLOXLX_METAL_BUFFER_OK");
    fflush((void *)0);
    return 0;
}
