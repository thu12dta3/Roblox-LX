# API e componentes pendentes

## Estado do ambiente

Darling `20260609-2` e LLVM 18 foram instalados neste host. O fixture Mach-O que usa `write`/`exit` passou; o fixture de rede confirmou resolução de `localhost` e TCP loopback com endereço de saída fornecido a `accept`. O teste Metal inicialmente retornava `nil` por uma dependência LLVM ausente; depois da instalação de `llvm18-libs`, o processo passou a terminar com SIGSEGV durante inicialização, antes de entrar em `main`, tanto com NVIDIA quanto com Lavapipe. Nenhum teste usou Roblox ou uma conta.

O projeto Darling atual usa o servidor de kernel em espaço de usuário (`darlingserver`), conforme o [README oficial](https://github.com/darlinghq/darling) e o histórico do [release oficial](https://github.com/darlinghq/darling/releases/tag/v0.1.20260608). Uma página antiga da documentação ainda menciona o módulo de kernel. O artefato oficial Ubuntu contém um launcher host que exige modo setuid root para criar namespaces e mounts; isso torna a instalação uma alteração administrativa. O launcher e o helper do servidor estão instalados e executam o fixture independente. A busca anterior por `darling-mach` e headers não é um requisito do Darling atual e foi removida do diagnóstico.

| Área / API | Comportamento esperado | Comportamento observado aqui | Implementação / evidência | Estado |
|---|---|---|---|---|
| Launcher e `darlingserver` | Criar o servidor e namespaces para um Mach-O | Revisão local `20260609-2` instalada; launcher e helper presentes; fixture executado | `src/robloxlx/compatibility/darling.py`; pacote externo local | PASS |
| Runtime / Mach-O loader | Executar `write` e `exit` pela libSystem Darwin e retornar status 0 | `ROBLOXLX_MACHO_OK` recebido com status 0; o antigo fixture de syscall direto foi corrigido porque essa interface não é traduzida pelo Darling | `src/robloxlx/compatibility/fixtures/macho_hello.s`; `test_darling_runtime()` | PASS para essas APIs |
| Prefixo DPREFIX | Inicializar prefixo isolado, executar o teste e parar seu servidor | Inicialização pelo launcher e execução passaram; `darling shutdown` é chamado e seu status registrado. Prefixos com arquivos root de overlay são preservados, sem remoção administrativa | `_test_fixture()` em `src/robloxlx/compatibility/darling.py` | PASS para inicialização; limpeza completa NÃO EXECUTADA |
| OpenGL / EGL | Não faz parte da rota de gráficos solicitada | `robloxlx graphics-test` chama `vkcube` com WSI Vulkan; não consulta GL/EGL | `src/robloxlx/graphics/vulkan.py` | OUT OF SCOPE; sem fallback |
| Vulkan host / swapchain | Obter GPU física, criar swapchain WSI e apresentar frames | `vkcube --wsi wayland --c 2` selecionou NVIDIA RTX 2060 SUPER e saiu com status 0 | `src/robloxlx/graphics/vulkan.py`; testado no host | PASS (host only) |
| Metal API→Vulkan via Darling | Criar dispositivo Metal, executar blit e verificar 256 bytes | Antes de LLVM 18: `MTLCreateSystemDefaultDevice()` retornou nil. Depois: SIGSEGV no mldr durante inicialização, antes do primeiro marcador em main; reproduzido com NVIDIA e Lavapipe. Buffer/blit e apresentação NÃO EXERCITADOS | `src/robloxlx/compatibility/fixtures/macho_metal.c`; log `metal-test.log`; upstream `darling-metal/src/Metal/Metal.mm` inicia Indium; causa exata do crash UNKNOWN | BLOCKED por crash do runtime gráfico |
| CoreAudio HAL / AUHAL | `AudioObjectGetPropertyData`, `AudioUnitInitialize`, `AudioUnitRender`, `AudioDeviceStart/Stop` enumeram dispositivos e transferem buffers de áudio | Runtime CLI funcional, áudio ainda sem teste dinâmico. MacOBlox implementa ponte de saída/entrada a PipeWire/PulseAudio e registra incompatibilidades do AUHAL; dados são de terceiros | APIs enumeradas no audit `audio_hal.c`; nada equivalente implementado aqui | UNKNOWN |
| Eventos AppKit / `NSEvent` | Receber eventos de teclado, scroll e botões com semântica macOS | Sem janela AppKit de teste | MacOBlox implementa tradução de eventos X11/Wayland e `NSEvent`; seus shims não foram copiados | UNKNOWN |
| CoreGraphics / mouse relativo | `CGAssociateMouseAndMouseCursorPosition`, estado de teclas e posição relativa bloqueiam cursor e entregam deltas corretos | Sem teste de mouse no Darling | MacOBlox documenta chamadas ausentes/incompletas em `libMacOBloxShims.m` e `raw_mouse.c`; não implementado aqui | UNKNOWN |
| XInput2 raw mouse | Fornecer movimento relativo sem aceleração para câmera | Ferramenta/biblioteca host detectada apenas por disponibilidade, sem captura de eventos | `diagnostics.py`; MacOBlox `raw_mouse.c` é referência, não copiado | UNKNOWN |
| POSIX sockets / DNS | Resolver localhost e trocar bytes por TCP loopback | `getaddrinfo`, `socket`, `bind`, `getsockname`, `listen`, `connect`, `accept` com buffers de saída, `write`, `read` e `close` passaram; marcador `ROBLOXLX_NETWORK_OK` | `src/robloxlx/compatibility/fixtures/macho_network.c`; `test_network_runtime()`; log `network-test.log` | PASS para loopback; rede externa e Roblox UNKNOWN |
| `accept(fd, NULL, NULL)` | Aceitar conexão sem retornar endereço do peer | O fixture encerrou com status 1 ao chamar essa variante; o mesmo teste com buffers passou. A implementação upstream converte o endereço sem guarda NULL | [Darling XNU `accept.c`](https://github.com/darlinghq/darling-xnu/blob/main/darling/src/libsystem_kernel/emulation/src/xnu_syscall/bsd/impl/network/accept.c); linha de dereferência no `sys_accept_nocancel`; nenhuma biblioteca externa foi modificada | BLOCKED nessa variante; correção upstream ainda não aplicada |
| `connectx` / transporte Roblox | API Darwin transfere dados TCP conforme semântica macOS | Não observado. MacOBlox mantém patches RakNet específicos do binário cliente | Audit `connectx_compat.c`, `transport_patches.py`; mudanças no protocolo/binário são BLOCKED e não reutilizadas | BLOCKED para patch de protocolo; API host UNKNOWN |
| AppKit GUI e janelas | Criar janela, receber eventos e apresentar frames Vulkan | Não exercitado: pacote CLI exclui componentes GUI; teste Metal offscreen já falha na inicialização | backend CLI não implementa AppKit; `macho_metal.c` isola APIs Metal | UNKNOWN / BLOCKED para apresentação Vulkan-only |

## Transferibilidade do audit MacOBlox

- **Darling upstream:** Mach-O loader, `darlingserver`, syscalls/Mach IPC e frameworks são o runtime externo; podem ser detectados e invocados como processo separado. O projeto Darling é GPL-3.0, e submódulos podem ter outras licenças. Nenhum código foi copiado.
- **Adaptadores host conceitualmente transferíveis:** Vulkan direto para gráficos; áudio por PipeWire/PulseAudio; eventos e raw mouse de X11/Wayland; sockets POSIX/DNS do sistema. OpenGL e Zink foram excluídos como backend/fallback. Cada adaptador exige teste independente e revisão de licença.
- **Não transferíveis para este projeto:** `libMacOBloxShims.dylib`, stubs de framework carregados no processo, `patch_startup_throttle.py`, substituição de bytes/funções, patches de transporte/RakNet, alterações FastFlags para forçar renderizador, ocultar device Metal ou injeção/interposição destinada ao cliente. A política exige executável íntegro e não altera protocolos/verificações.
- **Licenças:** MacOBlox declara MIT, mas incorpora bibliotecas/fontes com avisos próprios e conteúdo proprietário Roblox. O repositório foi auditado em `work/MacOBlox-audit` e não será empacotado. Darling permanece dependência externa; a licença proprietária do ROBLOX-LX não altera suas licenças.

## Atualização: Metal offscreen corrigido (2026-10-11)

Os resultados anteriores de crash permanecem como histórico. O teste atual com framework recompilado e ICD NVIDIA isolado passou, incluindo saída 0 e término da thread de polling. Nenhum cliente Roblox foi executado.

| API/comportamento | Esperado | Observado atual | Implementação | Estado |
|---|---|---|---|---|
| Inicialização Vulkan | Criar dispositivo físico | Enumeração conjunta carregava LLVM 18 e LLVM 23 via Lavapipe; seleção de um ICD NVIDIA permite inicialização real | `src/robloxlx/graphics/vulkan.py`; patch `src/Metal/Metal.mm` | PASS no host testado |
| `MTLDevice.name` | Nome real da GPU | NVIDIA GeForce RTX 2060 SUPER | Patch `src/Metal/MTLDevice.mm`, delega a Indium | PASS |
| `blitCommandEncoder`, `fillBuffer:range:value:` | Executar preenchimento GPU | Todos os 256 bytes conferidos após conclusão | Patch `src/Metal/MTLBlitCommandEncoder.mm` | PASS |
| `copyFromBuffer:sourceOffset:toBuffer:destinationOffset:size:` | Copiar buffers GPU | Todos os 256 bytes do segundo buffer conferidos | Mesmo adaptador; operação real de Indium | PASS |
| `MTLCommandBuffer.status` | Reportar conclusão real | Estado 4 recebido após callback de conclusão Indium | Patch `src/Metal/MTLCommandBuffer.mm` | PASS no caminho de sucesso; caminho de erro UNKNOWN |
| Término Metal | Parar polling antes de destruir dispositivos | Thread encerrada e processo sai 0 | Patch `src/Metal/MTLDevice.mm` usa join; `Metal.mm` usa atexit idempotente | PASS |
| AppKit / CAMetalLayer apresentação | Janela e frames por Vulkan | Não implementado/testado; integração upstream envolve OpenGL | QuartzCore/CAMetalDrawable upstream; adaptador Vulkan de apresentação ainda ausente | BLOCKED para Vulkan-only atual |

O patch é distribuído separadamente em `packaging/darling-metal/metal-vulkan.patch` sob MPL-2.0, preservando os avisos. O framework do sistema não foi substituído.
