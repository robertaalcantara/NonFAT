from numpy import ceil
import Inserir

def inicio():
    nomeArquivo = input("Insira o caminho do arquivo que deseja abrir: \n")

    arq = open(nomeArquivo, 'rb+')

    #pega do arquivo os bytes referentes ao boot record
    bootRecord = arq.read(13)

    global bytesPorSetor, setoresPorCluster

    #dados do boot record
    bytesPorSetor = int.from_bytes(bootRecord[0:2], "little")
    setoresPorCluster = int.from_bytes(bootRecord[2:3], "little")
    setoresBootRecord = int.from_bytes(bootRecord[3:5], "little")
    totalSetores = int.from_bytes(bootRecord[5:7], "little")
    entradasRootDir = int.from_bytes(bootRecord[7:9], "little")
    primeiroClusterLivre = int.from_bytes(bootRecord[9:13], "little")

    numSetoresRootDir = int((entradasRootDir*32)/bytesPorSetor)
    
    Inserir.inserir_arquivo(arq, primeiroClusterLivre, bytesPorSetor, setoresPorCluster, setoresBootRecord, numSetoresRootDir, totalSetores)

    #pula o ponteiro do arquivo para o início do root dir
    #arq.seek(bytesPorSetor*setoresBootRecord)

     # pega cdo arquivo os bytes referentes ao root dir
    #rootDir = arq.read(numSetoresRootDir * bytesPorSetor)

   # printarConteudoDir(rootDir)

def printarConteudoDir(diretorio):  
    posIn = 0  
    listaArquivos = []

    #verifica se o byte do tipo está zerado (significa que não há mais elementos nesse dir)
    while(diretorio[posIn+11] != 0):
        conteudoArquivo = []
        #verifica se o arquivo foi excluído
        if diretorio[posIn+20] == 239:
            posIn +=32
            continue
        nome = diretorio[posIn:posIn + 8].decode("ASCII")
        tamanhoArquivo = int.from_bytes(diretorio[posIn + 28:posIn + 32], "little")
        firstCluster = int.from_bytes(diretorio[posIn + 12:posIn + 16], "little")
        tamanhoArquivo = int.from_bytes(diretorio[posIn + 16:posIn + 18], "little")
        
        #cálculo do número de clusters utilizados
        if(diretorio[posIn+18:posIn+19] == 0):
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
    aux = 0
    for arquivo in listaArquivos:
        print(f"{aux} - Nome: {arquivo[0]} | Extensao: {arquivo[1]} | Tipo: {arquivo[2]} | Tamanho: {arquivo[3]} | First_cluster: {arquivo[4]}")
        aux +=1

inicio()



