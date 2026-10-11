# Apresentação Vulkan de um executável macOS independente

## Implementação atual

`src/robloxlx/compatibility/fixtures/macho_window.mm` é um executável Mach-O x86_64 original. Ele usa o framework Metal recompilado, Indium instalado e a interface ELF `_elfcalls` do Darling para acessar SDL nativo. A SDL cria uma janela Vulkan real; nenhuma função OpenGL é chamada pelo fixture. O host deste teste usa `sdl2-compat 2.32.74-1` sobre `sdl3 3.4.18-1`.

O teste implementa a sequência real:

1. Inicializar SDL video e criar uma janela 640×480 com a flag Vulkan.
2. Consultar as extensões de instância exigidas pelo backend SDL. O processo é iniciado com WSI e driver de vídeo concordantes.
3. Criar dispositivo Metal real e obter o dispositivo Vulkan correspondente de Indium.
4. Criar VkSurfaceKHR, verificar suporte de apresentação da fila e consultar capacidades e formatos.
5. Criar uma swapchain FIFO respeitando limites de quantidade de imagens, extensão e alpha suportado. Exigir um formato RGBA8 e suporte TRANSFER_DST; falhar explicitamente caso ausentes.
6. Preencher um buffer compartilhado por `MTLBlitCommandEncoder.fillBuffer`, esperar conclusão real e conferir todos os bytes pela CPU.
7. Adquirir cada imagem, aplicar barreiras de memória/layout, copiar o buffer GPU para a imagem e submeter à fila Vulkan. Apresentar com semáforos, esperar fence/fila e repetir 30 vezes.
8. Esperar o dispositivo, destruir recursos WSI/SDL, liberar objetos Metal e encerrar o polling antes da destruição de Indium.

O marcador de sucesso exige que as 30 chamadas de apresentação e as esperas sejam aceitas pelo driver. A conferência verifica o buffer de origem; não faz captura nem leitura dos pixels exibidos pelo compositor. O teste não registra teclado, mouse, microfone ou tela.

## Reprodução

Preparar os checkouts e submódulos fixados conforme `packaging/darling-metal/README.md`. Compilar sem privilégios:

```bash
bash packaging/darling-metal/build.sh \
  /caminho/darling-metal /caminho/darling /caminho/indium \
  /caminho/build-window src/robloxlx/compatibility/fixtures/macho_window.mm
PYTHONPATH=src python -m robloxlx.cli window-test \
  --executable /caminho/build-window/window-probe --wsi wayland
PYTHONPATH=src python -m robloxlx.cli window-test \
  --executable /caminho/build-window/window-probe --wsi x11
ROBLOXLX_WINDOW_PROBE=/caminho/build-window/window-probe \
  PYTHONPATH=src python -m unittest discover -s tests/unit
```

A CLI rejeita ELF/arquiteturas incompatíveis, usa prefixo isolado, timeout de 30 segundos, log privado e shutdown daquele prefixo. Sem o fixture configurado, os testes de integração WSI são SKIPPED; mocks de orquestração não contam como evidência gráfica. Nenhum pacote é instalado pelo comando.

## Falhas encontradas e corrigidas

| Componente | Esperado | Observado | Correção/local |
|---|---|---|---|
| Declarações Metal | Compilar chamadas blit/status com tipos corretos | Header original não declara métodos implementados pelo patch | `packaging/darling-metal/metal-vulkan.patch`, `MTLCommandBuffer.h` |
| Extensões Vulkan de instância | Criar superfície correspondente ao sistema de janelas | Metal offscreen não habilita extensões WSI | Mesmo patch, `Metal.mm`: seleção de extensão por processo |
| Identificação de PrivateBuffer | Acessar backing Vulkan do buffer original | `dynamic_pointer_cast` retornou NULL mesmo com RTTI de objeto `Indium::PrivateBuffer`; desreferência inicial provocou SIGSEGV em ambos os backends | Fixture valida nome RTTI contra tipo esperado antes de `static_pointer_cast`; fonte/ABI fixados. Causa da comparação RTTI entre módulos UNKNOWN |
| Sincronização | Disponibilizar GPU fill para cópia e imagem para apresentação | Caminho exige barreiras, semáforos e fence | Fixture aplica barreiras de buffer/imagem e espera real de fila; não simula conclusão |

## Integração macOS ainda necessária

Este é o primeiro caminho WSI real de um Mach-O neste projeto. **Não é implementação de NSWindow, NSView, CALayer ou CAMetalLayer.** A apresentação atual ocorre pelo adaptador SDL do fixture. Integrá-lo às APIs públicas do cliente continua pendente:

- `NSWindow/NSView`: obter e manter a janela nativa e coordenadas/layout, incluindo ciclo de eventos. Upstream `AppKit/X11.backend/X11Window.m` fornece windowHandle; `X11SubWindow.m` cria subjanela, mas não existe integração Vulkan aqui. Wayland precisa de suporte próprio no backend de janelas.
- `CAMetalLayer.nextDrawable`: associar layer à superfície, devolver textura Metal de imagem adquirida e cumprir formato, drawableSize, framebufferOnly e timeout.
- `MTLCommandBuffer.presentDrawable`: integrar a conclusão real de renderização à fila de apresentação e liberar drawables somente após sincronização apropriada.
- Redimensionamento, minimização, OUT_OF_DATE, troca de formato, fechamento e múltiplas janelas: o fixture tem tamanho fixo e não cobre essas operações.
- `QuartzCore/CAMetalDrawable.mm`, `CAMetalLayer.mm` e `CALayerContext` upstream atualmente dependem de OpenGL. Esses componentes GPL-3.0 precisam permanecer externos com fonte/licenças próprias caso sejam modificados/distribuídos. Nenhuma fonte GPL foi copiada ao aplicativo proprietário.
- Shaders Metal, render pipelines e demais APIs usadas pelo Roblox continuam UNKNOWN.

Nada foi instalado como substituto de AppKit/QuartzCore; nenhum binário Roblox foi obtido, modificado ou executado. Abrir uma janela de teste não comprova que o cliente ou uma partida funcionem.

A integração pendente é acompanhada na [issue #4](https://github.com/thu12dta3/Roblox-LX/issues/4). A evidência CLI está em `VULKAN_WINDOW_EVIDENCE.txt`.

## Etapa posterior: APIs públicas

O runtime `runtime/window/` agora implementa um subconjunto real de NSWindow/NSView/CALayer/CAMetalLayer, com fixture separado sem chamadas SDL/Vulkan. Essa etapa passou incluindo resize e segunda janela. As limitações listadas anteriormente continuam aplicáveis ao restante das APIs; consultar `runtime/window/README.md` e a seção mais recente de TEST_RESULTS.md.
