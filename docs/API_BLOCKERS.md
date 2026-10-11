# API e componentes pendentes

## Estado do ambiente

`darling` não foi encontrado no PATH deste host durante a execução. Assim, nenhuma observação dinâmica sobre APIs macOS no Darling instalado pode ser declarada. Todas as linhas marcadas UNKNOWN exigem execução no Darling correspondente ou um programa de teste independente. O inventário do MacOBlox abaixo serve para direcionar testes, não como confirmação independente de comportamento.

| Área / API | Comportamento esperado | Comportamento observado aqui | Implementação / evidência | Estado |
|---|---|---|---|---|
| Runtime / Mach-O loader | Iniciar executável Mach-O x86_64 e devolver status/saída do processo | Runtime `darling`: NOT FOUND; fixture local compila e tem magic `cffaedfe`, mas não foi executado | `src/robloxlx/compatibility/darling.py`; `tests/unit/fixtures/macho_hello.s`; integração `test_macho_hello_executable` | BLOCKED por dependência ausente |
| Prefixo DPREFIX | Usar prefixo existente selecionado pelo usuário | Não exercitado porque Darling ausente | `run_darling(..., prefix=...)`; integração usa DPREFIX temporário se Darling existir | UNKNOWN |
| OpenGL / EGL | Aplicação obtém contexto de janela e apresenta frames via driver Linux | Host tem bibliotecas/utilitários detectáveis; nenhuma chamada de contexto foi feita por macOS | Diagnóstico em `src/robloxlx/diagnostics.py`; teste gráfico independente ainda não implementado | UNKNOWN |
| Metal / Metal-to-Vulkan | Criar device e compilar/apresentar pipelines | Nenhum device Metal observado. Darling upstream descreve backend Metal inicial via tradução Vulkan; isso não comprova Roblox | Nenhum adaptador ROBLOX-LX. Referência MacOBlox: `launcher/macoblox/graphics.py` e `experimental/metal/` (não copiados) | UNKNOWN |
| CoreAudio HAL / AUHAL | `AudioObjectGetPropertyData`, `AudioUnitInitialize`, `AudioUnitRender`, `AudioDeviceStart/Stop` enumeram dispositivos e transferem buffers de áudio | Runtime ausente, sem observação. MacOBlox implementa ponte de saída/entrada a PipeWire/PulseAudio e registra incompatibilidades do AUHAL; dados são de terceiros | APIs enumeradas no audit `audio_hal.c`; nada equivalente implementado aqui | UNKNOWN |
| Eventos AppKit / `NSEvent` | Receber eventos de teclado, scroll e botões com semântica macOS | Sem janela AppKit de teste | MacOBlox implementa tradução de eventos X11/Wayland e `NSEvent`; seus shims não foram copiados | UNKNOWN |
| CoreGraphics / mouse relativo | `CGAssociateMouseAndMouseCursorPosition`, estado de teclas e posição relativa bloqueiam cursor e entregam deltas corretos | Sem teste de mouse no Darling | MacOBlox documenta chamadas ausentes/incompletas em `libMacOBloxShims.m` e `raw_mouse.c`; não implementado aqui | UNKNOWN |
| XInput2 raw mouse | Fornecer movimento relativo sem aceleração para câmera | Ferramenta/biblioteca host detectada apenas por disponibilidade, sem captura de eventos | `diagnostics.py`; MacOBlox `raw_mouse.c` é referência, não copiado | UNKNOWN |
| POSIX sockets / DNS | Resolução de nomes e sockets seguem a configuração Linux e preservam tráfego padrão | Ferramentas `getent`/`resolvectl` detectadas; sem chamada por processo Darling | `diagnostics.py`; protocolo Roblox/DNS customizado não será interceptado | UNKNOWN |
| `connectx` / transporte Roblox | API Darwin transfere dados TCP conforme semântica macOS | Não observado. MacOBlox mantém patches RakNet específicos do binário cliente | Audit `connectx_compat.c`, `transport_patches.py`; mudanças no protocolo/binário são BLOCKED e não reutilizadas | BLOCKED para patch de protocolo; API host UNKNOWN |
| AppKit GUI e janelas | Criar janela, ciclo de eventos e fechar processo corretamente | Darling ausente | backend atual só gerencia processo CLI, não reimplementa AppKit | UNKNOWN |

## Transferibilidade do audit MacOBlox

- **Darling upstream:** Mach-O loader, `darlingserver`, syscalls/Mach IPC e frameworks são o runtime externo; podem ser detectados e invocados como processo separado. O projeto Darling é GPL-3.0, e submódulos podem ter outras licenças. Nenhum código foi copiado.
- **Adaptadores host conceitualmente transferíveis:** OpenGL via driver do host, Zink opcional, áudio por PipeWire/PulseAudio, eventos e raw mouse de X11/Wayland, e sockets POSIX/DNS do sistema. Precisam de testes independentes e implementação própria sob licença compatível antes de uso.
- **Não transferíveis para este projeto:** `libMacOBloxShims.dylib`, stubs de framework carregados no processo, `patch_startup_throttle.py`, substituição de bytes/funções, patches de transporte/RakNet, alterações FastFlags para forçar renderizador, ocultar device Metal ou injeção/interposição destinada ao cliente. A política exige executável íntegro e não altera protocolos/verificações.
- **Licenças:** MacOBlox declara MIT, mas incorpora bibliotecas/fontes com avisos próprios e conteúdo proprietário Roblox. O repositório foi auditado em `work/MacOBlox-audit` e não será empacotado. Darling permanece dependência externa; a licença proprietária do ROBLOX-LX não altera suas licenças.
