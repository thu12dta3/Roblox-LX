# Instalação no Arch Linux / Garuda

O CLI é Python puro e não instala Darling nem dependências gráficas. No checkout privado, rode:

```sh
python -m unittest discover -s tests/unit
PYTHONPATH=src python -m robloxlx.cli doctor
```

Para instalar o CLI como pacote Arch local, use `packaging/arch/PKGBUILD` a partir da raiz do checkout:

```sh
(cd packaging/arch && makepkg -f)
```

O PKGBUILD inclui apenas o CLI, documentação e licença proprietária; não instala Darling, Roblox, GPU drivers ou pacotes de sistema. Instale o pacote local com o gerenciador Arch somente após revisar o artefato. Darling deve ser instalado separadamente por fonte que você confie. ROBLOX-LX não roda `pacman`, não usa `sudo` e não modifica configurações globais.

Após instalar Darling, confirme o runtime com `robloxlx doctor` e execute `robloxlx darling-test`. Esse teste compila um Mach-O local com syscalls Darwin básicos e usa um DPREFIX temporário; não usa Roblox nem sua conta. Use um programa macOS independente em seguida. O comando de execução aceita `robloxlx launch --program /caminho/App.app --dry-run` para validar o bundle e inspecionar o plano sem iniciar processo. Para iniciar de fato, remova `--dry-run`; logs ficam em `$XDG_STATE_HOME/robloxlx/logs` ou `~/.local/state/robloxlx/logs`.

No host, o teste gráfico direto Vulkan é `robloxlx graphics-test --frames 3`. Requer `vkcube`, uma sessão Wayland/X11 ativa e uma GPU Vulkan integrada ou discreta. Não usa OpenGL/Zink e testa a apresentação Linux Vulkan, não Metal/Darling.

**Atenção ao prefixo:** se `--prefix` for omitido, Darling pode criar/inicializar `~/.darling` ao primeiro uso. Para evitar isso, passe um DPREFIX já existente com `--prefix /caminho`. O backend não cria, apaga nem migra prefixos por conta própria.

Os comandos explícitos de teste são uma exceção: inicializam seu próprio prefixo isolado via launcher Darling e chamam `darling shutdown` ao terminar. O diretório de build é removido; os prefixos `/tmp/robloxlx-darling-prefix-*` são preservados porque Darling cria arquivos de overlay como root. O CLI não tenta removê-los com sudo. Logs persistem em `darling-test.log` e `metal-test.log` na pasta de logs do usuário.

`robloxlx metal-test` testa APIs Metal com um executável independente, sem Roblox. A release Ubuntu usada no pacote local depende de `libLLVM-18.so` para Iridium; o host Arch precisa dessa versão exata (pacote `llvm18-libs`). Uma biblioteca LLVM de outra versão não deve ser renomeada para satisfazer essa dependência. A presença do framework Metal e de Vulkan no host não comprova que o dispositivo Metal é criado.
