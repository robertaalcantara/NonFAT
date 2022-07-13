from ctypes import sizeof
from numpy import ceil
import os.path
import Inserir

operacoes = ['Abrir', 'Exportar', 'Adicionar', 'Formatar']

def inicio():
    global bytesPorSetor, setoresPorCluster, dados, rootDir, setoresBootRecord, numSetoresRootDir, totalSetores, arq, primeiroClusterLivre

    nomeArquivo = input("Insira o caminho do arquivo que deseja abrir: \n")

    arq = open(nomeArquivo, 'rb+')

    #pega do arquivo os bytes referentes ao boot record
    bootRecord = arq.read(13)


    #dados do boot record
    bytesPorSetor = int.from_bytes(bootRecord[0:2], "little")
    setoresPorCluster = bootRecord[2]
    setoresBootRecord = int.from_bytes(bootRecord[3:5], "little")
    totalSetores = int.from_bytes(bootRecord[5:7], "little")
    entradasRootDir = int.from_bytes(bootRecord[7:9], "little")
    primeiroClusterLivre = int.from_bytes(bootRecord[9:13], "little")

    numSetoresRootDir = int((entradasRootDir*32)/bytesPorSetor)
    
    #pula o ponteiro do arquivo para o início do root dir
    arq.seek((bytesPorSetor*setoresBootRecord)-13)

    #pula o ponteiro do arquivo para o início do root dir
    #arq.seek(bytesPorSetor*setoresBootRecord)

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

    opcaoEscolhida = int(printarOperacoes())
    
    #abrir um arq/dir
    if(opcaoEscolhida == 0):
        printarLista(listaArquivos)
        numArquivo = input("Digite o número do arquivo que deseja abrir: ")

        #numeros que não encaixam com os indices da lista
        if(numArquivo < 0 or numArquivo >= sizeof(listaArquivos)):
            print("Opção inválida")
            listagens(listaArquivos)
        
        arquivoAberto = listaArquivos[numArquivo]
        setorInicio = arquivoAberto[4] * setoresPorCluster

        #abre um diretorio
        if(arquivoAberto[2] == 'diretorio'):
            conteudo = dados[setorInicio*bytesPorSetor:(setorInicio+1)*bytesPorSetor]
            printarConteudoDir(conteudo)
        #abre um arquivo
        elif(arquivoAberto[2] == 'arquivo'):
            conteudo = dados[setorInicio*bytesPorSetor:(setorInicio+arquivoAberto[5])*bytesPorSetor]   
            print(conteudo.decode("ASCII"))      

    #exportar um arquivo do sistema de arquivos para fora
    elif(opcaoEscolhida == 1):
        exportarArquivo(listaArquivos)

    #adicionar arquivo no sistema de arquivos
    elif(opcaoEscolhida == 2):
        Inserir.inserir_arquivo(arq, primeiroClusterLivre, bytesPorSetor, setoresPorCluster, setoresBootRecord, numSetoresRootDir, totalSetores)
        #lembrar de atualizar o conteudo da variavel dados sempre que um arquivo for adicionado

    #formatar o disco
    elif(opcaoEscolhida == 3):
        formatar()
    else:
        print("----Opção inválida")
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
        aux+=1
    return input()
def exportarArquivo(listaArquivos):
    printarLista(listaArquivos)

    num = input('Digite o numero do arquivo que deseja exportar: ')

    escolhido = listaArquivos[num]

    if escolhido[2] != 'arquivo':
        print('Selecione um arquivo')
        exportarArquivo(listaArquivos)

    path = input('Digite o caminho do local que deseja exportar o arquivo: ')
    nome = escolhido[0]
    ext = escolhido[1]
    FirstC = escolhido[4]
    nomeCompleto = os.path.join(path, nome+ext)

    setorInicio = escolhido[4] * setoresPorCluster
    conteudoByte = dados[setorInicio*bytesPorSetor:(setorInicio+escolhido[5])*bytesPorSetor]   

    conteudo = conteudoByte.decode("ASCII")
    with open(nomeCompleto,'w') as f:
        f.write(conteudo)

def formatar():

    numSetores = input('Numero de setores que deseja formatar: ')
    # recebo em setores e tenho que calcular numero de cluster com estes setores
    numCluster = numSetores/setoresPorCluster
    # clusters formatados sao adicionadas na lista de clusters livres
    # colocar na posicao 19 0xff ou 239
    # se excluir um deretorio do diretorio raiz q tem arquivos e outros diretorios, isso conta na quantidade de setores q tem q ser formatados?
    i = 0
    while(rootDir[i+11] != 0):
        #verifica se o arquivo foi excluído
        if rootDir[i+19] == 239:
            i +=32
            continue
        tamanhoArquivo = int.from_bytes(rootDir[i + 16:i + 19], "little")
        
        #cálculo do número de clusters utilizados
        numClusterUtilizados = int(ceil(int(ceil(tamanhoArquivo / bytesPorSetor))/setoresPorCluster))
        if numClusterUtilizados<=numCluster:
            rootDir[i+19] = 239
            numCluster=numCluster-numClusterUtilizados
            firstCluster = int.from_bytes(rootDir[i + 12:i + 16], "little")
            # colocar na lista os clusters que agora estao liberados
        i+=32
    print('Formatação finalizada')
    printarConteudoDir()


if __name__ == '__main__':
   inicio()