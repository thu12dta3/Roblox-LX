# ROBLOX-LX

**Bannaman6655 Productions** — projeto privado de compatibilidade desktop no Linux. Não afiliado à Roblox Corporation.

## Objetivo e estado

Investigar a execução do cliente desktop macOS original através da camada de tradução de APIs Darling, diretamente no Linux e sem Android, VM ou emulação de um sistema operacional convidado. ROBLOX-LX não baixa, altera ou injeta código no executável. O trabalho atual entrega um launcher Darling genérico, diagnóstico real do host e um teste independente Mach-O; o runtime Darling não está instalado neste host, portanto a execução do fixture e do Roblox está **UNKNOWN/BLOCKED**, respectivamente.

## CLI implementada

- `robloxlx doctor`: detecta distribuição, sessão gráfica, GPU, driver, OpenGL/Vulkan, Darling, ferramentas e bibliotecas de host associadas a gráficos, áudio, entrada e rede.
- `robloxlx launch --program /caminho/para/binario-macos [-- argumentos]`: executa um binário local pelo Darling instalado, captura stdout/stderr em `~/.local/state/robloxlx/logs/darling-launch.log` e recolhe o processo. `--prefix` seleciona um prefixo Darling existente. Sem `--prefix`, o próprio Darling pode inicializar o prefixo padrão no primeiro uso.
- `robloxlx launch --dry-run --program ...`: mostra o comando e não inicia processo.
- `robloxlx compatibility`, `logs`, `self-test`, `cleanup`, `verify` e `version`.

O comando genérico aceita binários locais para testes de compatibilidade. Isso não demonstra que Roblox abre, renderiza, aceita entrada, reproduz áudio, conecta a partidas ou funciona com Hyperion.

## Desenvolvimento

Requer Python 3.10+. Sem dependências Python externas:

```sh
PYTHONPATH=src python -m robloxlx.cli doctor
PYTHONPATH=src python -m robloxlx.cli self-test
python -m unittest discover -s tests/unit
```

Darling e sondas de host são dependências opcionais e nunca instaladas pelo CLI. Veja [instalação Arch/Garuda](docs/INSTALLATION.md), [matriz de compatibilidade](docs/COMPATIBILITY.md), [auditoria Darling/MacOBlox e bloqueios de API](docs/API_BLOCKERS.md) e [resultados dos testes](docs/TEST_RESULTS.md).

## Compatibilidade

| Capacidade | Estado |
|---|---|
| CLI, descoberta de dependências e gestão de processo Darling | IMPLEMENTADO; coberto por testes unitários |
| Binário Mach-O x86_64 independente | Fixture compila; execução real **BLOCKED** porque Darling não está instalado neste host |
| Cliente macOS oficial Roblox em Darling | UNKNOWN; nenhuma cópia foi adquirida ou executada |
| Hyperion e partida multiplayer | UNKNOWN; não testados |
| Adaptações que modificam o cliente ou suas verificações | BLOCKED por política do projeto |

Não declarar compatibilidade ou segurança sem evidência reproduzível. Nenhuma conta, credencial ou binário Roblox foi usado nesta execução.

## Licença

O arquivo proprietário `LICENSE` aplica-se exatamente aos materiais de Bannaman6655 Productions. Nenhum código do Darling ou MacOBlox foi copiado para este repositório.
