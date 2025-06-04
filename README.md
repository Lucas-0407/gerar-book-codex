# gerar-book-codex

Ferramenta para gerar PDFs de book fotográfico a partir de imagens.
Inclui uma interface gráfica simples em Tkinter e suporte a 2, 3 ou 4 colunas por página.

## Instalação

```bash
python3 -m pip install -r requirements.txt
```

## Uso

Execute a interface gráfica:

```bash
python -m src.gui
```

Escolha a pasta de imagens, defina o número de colunas e o nome do arquivo PDF de saída.
O primeiro arquivo pode ser usado como capa se a opção de adicionar capa estiver habilitada.

## Testes

Para rodar os testes unitários:

```bash
pytest
```

