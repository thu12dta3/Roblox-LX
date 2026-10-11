/* Original ROBLOX-LX probe of Darwin POSIX networking, entirely on loopback. */
typedef struct {
    unsigned char length, family;
    unsigned short port;
    unsigned int address;
    unsigned char reserved[8];
} DarwinIPv4;
extern int socket(int, int, int);
extern int bind(int, const void *, unsigned int);
extern int listen(int, int);
extern int getsockname(int, void *, unsigned int *);
extern int connect(int, const void *, unsigned int);
extern int accept(int, void *, unsigned int *);
extern long write(int, const void *, unsigned long);
extern long read(int, void *, unsigned long);
extern int close(int);
extern unsigned int htonl(unsigned int);
extern int getaddrinfo(const char *, const char *, const void *, void **);
extern void freeaddrinfo(void *);
extern int printf(const char *, ...);
extern int puts(const char *);
extern int fflush(void *);

static int fail(const char *api) {
    printf("NETWORK_API_FAILED:%s\n", api);
    fflush((void *)0);
    return 1;
}

static void stage(const char *api) {
    printf("NETWORK_API_BEGIN:%s\n", api);
    fflush((void *)0);
}

int main(void) {
    puts("NETWORK_API_BEGIN:getaddrinfo(localhost)");
    fflush((void *)0);
    void *resolved = (void *)0;
    if (getaddrinfo("localhost", (void *)0, (void *)0, &resolved) != 0 || !resolved)
        return fail("getaddrinfo(localhost)");
    freeaddrinfo(resolved);
    puts("NETWORK_DNS_OK:localhost");
    fflush((void *)0);
    stage("socket(server)");
    int server = socket(2, 1, 0); /* Darwin AF_INET, SOCK_STREAM */
    if (server < 0) return fail("socket(server)");
    DarwinIPv4 address = {16, 2, 0, htonl(0x7f000001), {0}};
    stage("bind(loopback)");
    if (bind(server, &address, sizeof(address)) != 0) return fail("bind(loopback)");
    unsigned int length = sizeof(address);
    stage("getsockname");
    if (getsockname(server, &address, &length) != 0) return fail("getsockname");
    stage("listen");
    if (listen(server, 1) != 0) return fail("listen");
    stage("socket(client)");
    int client = socket(2, 1, 0);
    if (client < 0) return fail("socket(client)");
    stage("connect(loopback)");
    if (connect(client, &address, sizeof(address)) != 0) return fail("connect(loopback)");
    stage("accept");
    DarwinIPv4 peer_address = {0};
    unsigned int peer_length = sizeof(peer_address);
    int peer = accept(server, &peer_address, &peer_length);
    if (peer < 0) return fail("accept");
    const char message[] = "ROBLOXLX_LOOPBACK";
    if (write(client, message, sizeof(message)) != sizeof(message)) return fail("write(TCP)");
    char received[sizeof(message)];
    unsigned long count = 0;
    while (count < sizeof(message)) {
        long size = read(peer, received + count, sizeof(message) - count);
        if (size <= 0) return fail("read(TCP)");
        count += (unsigned long)size;
    }
    for (unsigned long i = 0; i < sizeof(message); ++i)
        if (received[i] != message[i]) return fail("TCP payload mismatch");
    close(peer);
    close(client);
    close(server);
    puts("ROBLOXLX_NETWORK_OK");
    fflush((void *)0);
    return 0;
}
