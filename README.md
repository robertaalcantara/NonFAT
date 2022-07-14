# NonFAT

O sistema de arquivos NonFAT inicia pedindo para o usuário digitar qual o caminho da imagem que deseja abrir pelo sistema de arquivos. Se a imagem estiver dentro da pasta com o código de implementação basta digitar o nome do arquivo e sua extensão. Caso esteja em outro local, o caminho deve ser informado por completo.


Após isso, o usuário pode selecionar uma das opções permitidas no sistema:

  0. **Abrir** (para printar o conteúdo de um arquivo ou listar as entradas de um subdiretório)

  1. **Exportar** (para adicionar ao disco rígido algum arquivo que se encontra no sistema de arquivos)

  2. **Adicionar arquivo** (para adicionar um arquivo no sistema de arquivos que se encontra no disco rígido)

  3. **Formatar** (excluir conteúdo do sistema de arquivos)

  4. **Novo diretório** (criar um novo diretório vazio)
  
  5. **Sair** (parar a execução do sistema de arquivos)


Cada operação é acompanhada de um índice que se encontra a sua esquerda. Quando lhe for solicitado para escolher uma das operações, é esse índice que deve ser digitado no terminal. Caso o usuário digite um valor que não possui um índice correspondente na listagem (no caso, valores menores que zero ou maiores que os listados) a opção escolhida será dada como inválida.

### Opção 0) Abrir

A lista das entradas será exibida para que o usuário escolha qual deseja abrir. O número a ser digitado refere-se ao índice da entrada que deseja abrir, portanto índices que não se enquadram com a lista são consideradas opções inválidas. 

Caso o índice seja referente a um arquivo, será exibido para o usuário o conteúdo presente nele. Após isso, o usuário pode optar por voltar para o diretório que estava anteriormente (opção 0) ou sair do sistema de arquivos (opção 1). Valores diferentes de 0 e 1 farão com que o sistema seja encerrado, assim como se tem com o índice 1.

### Opção 1) Exportar

Novamente a lista das entradas será exibida para que o usuário escolha qual deseja exportar para seu disco rígido. Necessariamente essa entrada deve corresponder a um arquivo.txt, visto que não é possível a exportação de diretório pelo NonFAT. Enquanto o usuário não digitar um índice que corresponda a uma entrada do tipo arquivo lhe será pedido para informar outro índice.

Com o arquivo selecionado, basta indicar qual o caminho para o qual o arquivo será exportado.

Após isso, o usuário pode optar por voltar para o diretório que estava anteriormente (opção 0) ou sair do sistema de arquivos (opção 1). Valores diferentes de 0 e 1 farão com que o sistema seja encerrado, assim como se tem com o índice 1.

### Opção 2) Adicionar arquivo

Para adicionar um arquivo do disco rígido deve ser informado qual o seu caminho. O arquivo será adicionado no diretorio atual.


### Opção 3) Formatar

Nos arquivos e diretórios presentes será atualizado o a posição do byte 19 para 0xEF (arquivo excluido). 

### Opção 4) Novo diretório

O diretório a ser criado inicialmente estará vazio, portanto a única informação que deve ser indicada é o nome que se deseja atribuir a ele. Nele serão criados automaticamente as opções . (continuar no diretorio atual) e .. (voltar para o diretorio pai)

### Opção 5) Sair

Ao selecionar essa opção o arquivo será fechado e a janela atual do sistema de arquivos será encerrada. Dessa forma, para abrir o conteúdo de uma imagem ele deverá ser executado novamente.

