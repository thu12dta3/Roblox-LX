.section __TEXT,__text,regular,pure_instructions
.globl _start
_start:
    subq $8, %rsp
    movq $1, %rdi
    leaq message(%rip), %rsi
    movq $message_len, %rdx
    callq _write
    cmpq $message_len, %rax
    jne failed
    xorq %rdi, %rdi
    callq _exit
failed:
    movq $1, %rdi
    callq _exit
.section __TEXT,__const
message:
    .ascii "ROBLOXLX_MACHO_OK\n"
.set message_len, . - message
