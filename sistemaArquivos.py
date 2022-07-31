from ctypes import sizeof
from numpy import ceil
import os.path
import Inserir

operacoes = ['Abrir', 'Exportar', 'Adicionar arquivo', 'Formatar', 'Novo diretório','Copiar arquivo' ,'Sair']

def inicio():
    global bytesPorSetor, setoresPorCluster, setoresBootRecord, numSetoresRootDir, arq, totalSetores, dados, rootDir

    #pega do arquivo os bytes referentes ao boot record
    bootRecord = arq.read(13)

    #dados do boot record
    bytesPorSetor = int.from_bytes(bootRecord[0:2], "little")
    setoresPorCluster = bootRecord[2]
    setoresBootRecord = int.from_bytes(bootRecord[3:5], "little")
    totalSetores = int.from_bytes(bootRecord[5:7], "little")
    entradasRootDir = int.from_bytes(bootRecord[7:9], "little")
    #primeiroClusterLivre = int.from_bytes(bootRecord[9:], "little")

    numSetoresRootDir = int((entradasRootDir*32)/bytesPorSetor)

    #pula o ponteiro do arquivo para o início do root dir
    arq.seek(bytesPorSetor*setoresBootRecord)

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
    #percorrer a lista de arquivos para saber se é um subdiretorio ou raiz
    PonteiroDiretorioPai = 0
    root = True
    copiar = False
    for arquivo in listaArquivos:
        if(arquivo[0] == '..      '):
            root = False
    if(root):
        PonteiroDiretorioPai = setoresBootRecord*bytesPorSetor
    else:
        PonteiroDiretorioPai = listaArquivos[0][4]

    #printarLista(listaArquivos)

    opcaoEscolhida = int(printarOperacoes())
    
    #abrir um arq/dir
    if(opcaoEscolhida == 0):
        if(len(listaArquivos) == 0):
            print("\nLista vazia. Opção inválida.")
            listagens(listaArquivos)
        printarLista(listaArquivos)
        numArquivo = int(input("\nDigite o número do arquivo que deseja abrir: "))

        #numeros que não encaixam com os indices da lista
        if(numArquivo < 0 or numArquivo >= len(listaArquivos)):
            print("Opção inválida")
            listagens(listaArquivos)
        
        arquivoAberto = listaArquivos[numArquivo]
        setorInicio = arquivoAberto[4] * setoresPorCluster

        #abre um diretorio
        if(arquivoAberto[2] == 'diretorio'):
            if(arquivoAberto[4] == 2053726546):
                conteudo = rootDir
            else:
                conteudo = dados[setorInicio*bytesPorSetor:(setorInicio+numSetoresRootDir)*bytesPorSetor]
            printarConteudoDir(conteudo)
        #abre um arquivo
        elif(arquivoAberto[2] == 'arquivo'):
            conteudo = dados[setorInicio*bytesPorSetor:(setorInicio+(arquivoAberto[5]*setoresPorCluster))*bytesPorSetor]   
            print(conteudo) 

            fechar(listaArquivos)

    #exportar um arquivo do sistema de arquivos para fora
    elif(opcaoEscolhida == 1):
        if(len(listaArquivos) == 0):
            print("\nLista vazia. Opção inválida.")
            listagens(listaArquivos)
        exportarArquivo(listaArquivos)

    #adicionar arquivo no sistema de arquivos
    elif(opcaoEscolhida == 2):
        Inserir.inserir(arq, bytesPorSetor, setoresPorCluster, setoresBootRecord, numSetoresRootDir, 1, PonteiroDiretorioPai, copiar, NomeArq=0)
        alterar_info(PonteiroDiretorioPai)
        fechar(listaArquivos)

    #formatar os setores
    elif(opcaoEscolhida == 3):
        formatar()
    #adicionar diretorio no sistema de arquivos
    elif(opcaoEscolhida == 4):
         Inserir.inserir(arq, bytesPorSetor, setoresPorCluster, setoresBootRecord, numSetoresRootDir, 2, PonteiroDiretorioPai,copiar,NomeArq=0)
         alterar_info(PonteiroDiretorioPai)
         fechar(listaArquivos)

    elif (opcaoEscolhida == 5):
        copia(listaArquivos, PonteiroDiretorioPai)

    elif(opcaoEscolhida == 6):
        arq.close()
        exit()
    else:
        print("Opção inválida")
        listagens(listaArquivos)

def alterar_info(PonteiroDiretorioPai):
    global dados, rootDir
    arq.seek(0)

    arq.seek(bytesPorSetor*setoresBootRecord)

    rootDir = arq.read(numSetoresRootDir * bytesPorSetor)
    dados = arq.read((totalSetores-setoresBootRecord-numSetoresRootDir) * bytesPorSetor)

    if(PonteiroDiretorioPai == (bytesPorSetor*setoresBootRecord)):
        printarConteudoDir(rootDir)
    else:

        setores_diretorio_pai = PonteiroDiretorioPai*setoresPorCluster
        qtd_bytes = setores_diretorio_pai*bytesPorSetor

        print(PonteiroDiretorioPai)

        print(qtd_bytes)
        print(qtd_bytes+numSetoresRootDir*bytesPorSetor)
        printarConteudoDir(dados[qtd_bytes:qtd_bytes+numSetoresRootDir*bytesPorSetor])

    arq.read(qtd_bytes)

def printarLista(lista):
    aux = 0
    print("\nLista de entradas:")
    for arquivo in lista:
        if(arquivo[4] == 2053726546):
            print(f"{aux} - Nome: {arquivo[0]} | Extensao: {arquivo[1]} | Tipo: {arquivo[2]} | Tamanho: {arquivo[3]} | First_cluster: Raiz")
        else:
            print(f"{aux} - Nome: {arquivo[0]} | Extensao: {arquivo[1]} | Tipo: {arquivo[2]} | Tamanho: {arquivo[3]} | First_cluster: {arquivo[4]}")

        aux +=1

def printarOperacoes():
    aux = 0
    print("\nOperações: ")
    for opcao in operacoes:
        print(f"{aux} - {opcao}")
        aux+=1
    return input("\nDigite o número da operação que deseja realizar: ")

def exportarArquivo(listaArquivos):
    printarLista(listaArquivos)

    num = int(input('Digite o numero do arquivo que deseja exportar: '))

    escolhido = listaArquivos[num]

    if escolhido[2] != 'arquivo':
        print('Selecione um arquivo')
        exportarArquivo(listaArquivos)

    path = input('Digite o caminho do local que deseja exportar o arquivo: ')
    nome = escolhido[0]
    ext = escolhido[1]
    nomeCompleto = os.path.join(path, nome+'.'+ext)
    # nomeCompleto = path+'\\'+nome+'.'+ext
    setorInicio = escolhido[4] * setoresPorCluster
    conteudoByte = dados[setorInicio*bytesPorSetor:(setorInicio+(escolhido[5]*setoresPorCluster))*bytesPorSetor]   
    
    with open(nomeCompleto.replace(chr(0), ""),"wb") as f:
        f.write(conteudoByte)

    fechar(listaArquivos)

def fechar(listaArquivos):

    print("\n\nO que deseja realizar?")
    print("0 - Voltar para o diretório anterior\n1 - Sair do sistema de arquivos")
    opcao = int(input())
    if(opcao == 0):
        listagens(listaArquivos)
    else:
        arq.close()
        exit()

def formatar():

    # numSetores = int(input('Numero de setores que deseja formatar: '))
    # recebo em setores e tenho que calcular numero de cluster com estes setores
    # numCluster = numSetores/setoresPorCluster
    # clusters formatados sao adicionadas na lista de clusters livres
    # colocar na posicao 19 0xff ou 239
    # se excluir um deretorio do diretorio raiz q tem arquivos e outros diretorios, isso conta na quantidade de setores q tem q ser formatados?
    i = 0
    rotDir = arq.seek(bytesPorSetor*setoresBootRecord)

    while int.from_bytes(arq.read(11), "little")!=0:
        #verifica se o arquivo foi excluído
        if int.from_bytes(arq.read(19), "little")== 239:
            i +=32
            arq.seek(rotDir+i)
            continue
 
        #cálculo do número de clusters utilizados
        arq.seek(arq.tell()-11)
        arq.write(int.to_bytes(239, 1, "little"))
        
        i+=32
        arq.seek(rotDir+i)

    # atualizar BR
    arq.seek(9)
    arq.write(int.to_bytes(0, 4, "little"))

    # atualizar First Cluster
    arq.seek((setoresBootRecord+numSetoresRootDir)*bytesPorSetor)
    arq.write(int.to_bytes(14991, 4, "little"))

    #ponteiro pro próximo
    arq.write(int.to_bytes(4278190079, 4, "little"))

    print('Formatação finalizada')
    # printarConteudoDir(rootDir)

def copia(listaArquivos, PonteiroDiretorioPai):
    printarLista(listaArquivos)
    copiar = True
    num = int(input('Digite o numero do arquivo que deseja copiar: '))

    escolhido = listaArquivos[num]

    if escolhido[2] != 'arquivo':
        print('Selecione um arquivo')
        copia(listaArquivos)
    ext = escolhido[1]
    setorInicio = escolhido[4] * setoresPorCluster
    conteudoByte = dados[setorInicio*bytesPorSetor:(setorInicio+(escolhido[5]*setoresPorCluster))*bytesPorSetor]
    NomeCopia=input('Nome do arquivo: ')
    NomeArq = NomeCopia + '.'+ ext
    with open(NomeArq,"wb") as f:
        f.write(conteudoByte)


    Inserir.inserir(arq, bytesPorSetor, setoresPorCluster, setoresBootRecord, numSetoresRootDir, 1, PonteiroDiretorioPai, copiar, NomeArq)
    alterar_info(PonteiroDiretorioPai)

if __name__ == '__main__':
    print("\n-----Sistema de Arquivos NonFAT-----\n")
    nomeArquivo = input("Insira o caminho do arquivo que deseja abrir: ")
    arq = open(nomeArquivo, 'rb+')

    inicio()