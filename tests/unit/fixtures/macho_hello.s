.section __TEXT,__text,regular,pure_instructions
.globl _start
_start:
    movq $0x2000004, %rax
    movq $1, %rdi
    leaq message(%rip), %rsi
    movq $message_len, %rdx
    syscall
    movq $0x2000001, %rax
    xorq %rdi, %rdi
    syscall
.section __TEXT,__const
message:
    .ascii "ROBLOXLX_MACHO_OK\n"
.set message_len, . - message
