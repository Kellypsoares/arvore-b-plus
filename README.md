# Árvore B+ em Python

Projeto acadêmico de Banco de Dados que implementa uma Árvore B+ de ordem 4 para armazenar as siglas das 27 unidades federativas brasileiras. O objetivo é observar a organização da árvore e as operações de leitura e escrita durante a inserção dos dados.

## Implementação

Cada nó comporta até três chaves, considerando a ordem 4 adotada neste projeto. Os nós internos comportam até quatro filhos. Ao receber a quarta chave, o nó é dividido. As siglas ficam ordenadas nas folhas, que possuem uma referência para a próxima folha. Os nós internos guardam as chaves que orientam a navegação.

Cada nó é salvo em um arquivo `pagina_<id>.json`, na pasta `paginas_arvore_b`, representando uma página de disco. O JSON contém o indicador de folha (`leaf`), as chaves (`keys`), os identificadores dos filhos (`children`) e a referência para a próxima folha (`next`). A pasta é apagada e recriada a cada execução.

## Requisitos e execução

É necessário ter Python 3 instalado e permissão de escrita na pasta do projeto. O programa usa apenas a biblioteca padrão, sem dependências externas.

Na pasta do projeto, execute:

```bash
python3 arvore_b_mais.py
```

## Saída do programa

O programa apresenta no terminal:

- Quantidade de leituras e escritas de cada inserção.
- Cinco estados intermediários, após 5, 10, 15, 20 e 25 inserções.
- A árvore final organizada por níveis.
- Totais de leituras e escritas, tempo da carga e captura dos estados e verificação da inserção das 27 siglas.
- Caminho da pasta onde as páginas foram armazenadas.

## Contagem das operações

Cada carregamento de um arquivo JSON conta como uma leitura, e cada gravação conta como uma escrita. Essa contagem representa chamadas de leitura e gravação dos arquivos JSON, não necessariamente operações físicas individuais do dispositivo de armazenamento. As operações por inserção são calculadas pela diferença dos contadores antes e depois da chamada de inserção, incluindo as divisões de nós e a criação de uma nova raiz quando necessárias.

As capturas dos estados intermediários também leem os arquivos. Essas leituras entram no total que inclui os estados, mas não nas contagens por inserção. Esse total de escritas inclui a criação da página raiz inicial. As leituras da exibição final e da verificação das siglas ficam fora dos totais apresentados. O tempo medido inclui as inserções e as cinco capturas intermediárias, sem incluir a impressão dos resultados nem as verificações finais.
