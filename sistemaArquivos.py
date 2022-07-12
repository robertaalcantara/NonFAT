from ctypes import sizeof
from numpy import ceil

operacoes = ['Abrir', 'Exportar', 'Adicionar', 'Formatar']

def inicio():
    nomeArquivo = input("Insira o caminho do arquivo que deseja abrir: \n")

    arq = open(nomeArquivo, 'rb')

    #pega do arquivo os bytes referentes ao boot record
    bootRecord = arq.read(13)

    global bytesPorSetor, setoresPorCluster, dados

    #dados do boot record
    bytesPorSetor = int.from_bytes(bootRecord[0:2], "little")
    setoresPorCluster = int.from_bytes(bootRecord[2], "little")
    setoresBootRecord = int.from_bytes(bootRecord[3:5], "little")
    totalSetores = int.from_bytes(bootRecord[5:7], "little")
    entradasRootDir = int.from_bytes(bootRecord[7:9], "little")
    primeiroClusterLivre = int.from_bytes(bootRecord[9:13], "little")

    #pula o ponteiro do arquivo para o início do root dir
    arq.seek((bytesPorSetor*setoresBootRecord)-13)

    numSetoresRootDir = int((entradasRootDir *32)/bytesPorSetor)

     #pega do arquivo os bytes referentes ao root dir
    rootDir = arq.read(numSetoresRootDir * bytesPorSetor)
    dados = arq.read((totalSetores-setoresBootRecord-numSetoresRootDir) * bytesPorSetor)

    printarConteudoDir(rootDir)

def printarConteudoDir(diretorio):  
    posIn = 0  
    listaArquivos = []

    #verifica se o byte do tipo está zerado ( se = 0 significa que não há mais entradas nesse dir)
    while(diretorio[posIn+11] != 0):
        conteudoArquivo = []
        #verifica se o arquivo foi excluído
        if diretorio[posIn+19] == 239:
            posIn +=32
            continue
        nome = diretorio[posIn:posIn + 8].decode("ASCII")
        firstCluster = int.from_bytes(diretorio[posIn + 12:posIn + 16], "little")
        tamanhoArquivo = int.from_bytes(diretorio[posIn + 16:posIn + 19], "little")
        
        #cálculo do número de clusters utilizados
        numClusterUtilizados = int(ceil(int(ceil(tamanhoArquivo / bytesPorSetor))/setoresPorCluster))
            
        #verifica se no byte 8 do arquivo é um espaço (não tem extensão)
        if diretorio[posIn + 8] == 32:
            extensao = ' '
        else:
            extensao = diretorio[posIn + 8:posIn + 11].decode("ASCII")

        if diretorio[posIn+11] == 1:
            tipo = "arquivo"
        elif diretorio[posIn+11] == 2:
            tipo = "diretorio"

        conteudoArquivo = [nome, extensao, tipo, tamanhoArquivo, firstCluster, numClusterUtilizados]
        posIn += 32
        listaArquivos.append(conteudoArquivo)

    #printa os arquivos presentes no diretório
    listagens(listaArquivos)
    
def listagens(listaArquivos):

    printarLista(listaArquivos)

    opcaoEscolhida = printarOperacoes()

    if(opcaoEscolhida == 0):
        printarLista(listaArquivos)
        numArquivo = input("Digite o número do arquivo que deseja abrir: ")

        if(numArquivo < 0 or numArquivo >= sizeof(listaArquivos)):
            print("Opção inválida")
            listagens(listaArquivos)
        
        arquivoAberto = listaArquivos[numArquivo]
        setorInicio = arquivoAberto[4] * setoresPorCluster

        if(arquivoAberto[2] == 'diretorio'):
            conteudo = dados[setorInicio*bytesPorSetor:(setorInicio+1)*bytesPorSetor]
            printarConteudoDir(conteudo)
        elif(arquivoAberto[2] == 'arquivo'):
            conteudo = dados[setorInicio*bytesPorSetor:(setorInicio+arquivoAberto[5])*bytesPorSetor]   
            print(conteudo.decode("ASCII"))      

    elif(opcaoEscolhida == 1):
        exportarArquivo()

    elif(opcaoEscolhida == 2):
        adicionarArquivo()
        #lembrar de atualizar o conteudo da variavel dados sempre que um arquivo for adicionado

    elif(opcaoEscolhida == 3):
        formatar()
    else:
        print("Opção inválida")
        listagens(listaArquivos)

def printarLista(lista):
    aux = 0
    for arquivo in lista:
        print(f"{aux} - Nome: {arquivo[0]} | Extensao: {arquivo[1]} | Tipo: {arquivo[2]} | Tamanho: {arquivo[3]} | First_cluster: {arquivo[4]}")
        aux +=1

def printarOperacoes():
    aux = 0
    print("\nDigite o número da operação abaixo que deseja realizar:")
    for opcao in operacoes:
        print(f"{aux} - {opcao}")
    
    return input()
