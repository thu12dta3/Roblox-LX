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

Após instalar Darling, confirme o runtime com `robloxlx doctor`. Use um programa macOS independente primeiro. O comando de execução aceita `robloxlx launch --program /caminho/binario --dry-run` para inspecionar o plano sem iniciar processo. Para iniciar de fato, remova `--dry-run`; logs ficam em `$XDG_STATE_HOME/robloxlx/logs` ou `~/.local/state/robloxlx/logs`.

**Atenção ao prefixo:** se `--prefix` for omitido, Darling pode criar/inicializar `~/.darling` ao primeiro uso. Para evitar isso, passe um DPREFIX já existente com `--prefix /caminho`. O backend não cria, apaga nem migra prefixos por conta própria.
