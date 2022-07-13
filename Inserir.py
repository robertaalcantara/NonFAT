from pathlib import Path
from math import ceil
import os

def info_arquivo():

    caminho_arquivo = input("Insira o caminho do arquivo: \n")

    with open(caminho_arquivo, 'rb') as leitura_arquivo:
         conteudo_arquivo = leitura_arquivo.read(-1)
    leitura_arquivo.close()

    tamanho_arquivo = Path(caminho_arquivo).stat().st_size 

    arquivo = os.path.basename(caminho_arquivo)
    nome_arquivo, extensao_arquivo = os.path.splitext(arquivo)
    extensao_arquivo = extensao_arquivo.replace(extensao_arquivo[0], "")

    return(tamanho_arquivo, nome_arquivo, extensao_arquivo, conteudo_arquivo)

def inserir_arquivo(arq, primeiroClusterLivre, bytesPorSetor, setoresPorCluster, setoresBootRecord, numSetoresRootDir):

    arquivo = []
    arquivo = info_arquivo()

    bytes_cluster = bytesPorSetor*setoresPorCluster
    qtd_cluster_arquivo = ceil(arquivo[0]/bytes_cluster)

    #pula o ponteiro do arquivo para o início do primeiro bloco livre
    prim_setor_livre = setoresBootRecord + numSetoresRootDir + (primeiroClusterLivre*setoresPorCluster)
    arq.seek(bytesPorSetor*prim_setor_livre)

    qtd_clusters_livres = int.from_bytes(arq.read(4), "little")
    proximo_cluster_livre = int.from_bytes(arq.read(4), "little")
    arq.seek(bytesPorSetor*prim_setor_livre)
    
    if(qtd_clusters_livres >= qtd_cluster_arquivo):
        arq.write(arquivo[3])
        arq.write(b'\x00'*(bytes_cluster - (arquivo[0])%bytes_cluster))

        clusters_livres = qtd_clusters_livres - qtd_cluster_arquivo
        if(clusters_livres > 0):
            
            prim_cluster_livre_atual = primeiroClusterLivre + qtd_cluster_arquivo

            #atualizar próximo bloco
            prim_setor_livre_atual = setoresBootRecord + numSetoresRootDir + (prim_cluster_livre_atual*setoresPorCluster)
            arq.seek(bytesPorSetor*prim_setor_livre_atual)

            #tamanho de clusters livres
            arq.write(int.to_bytes(clusters_livres, 4, "little"))

            #ponteiro pro próximo
            proximo = proximo_cluster_livre
            arq.write(int.to_bytes(proximo, 4, "little"))  
        else:
            prim_cluster_livre_atual = proximo_cluster_livre

        #atualizar BR - arquivo
        arq.seek(9)
        arq.write(int.to_bytes(prim_cluster_livre_atual, 4, "little"))

        #atualizar RD - arquivo
        arq.seek(setoresBootRecord*bytesPorSetor)
        byte = 0
        while int.from_bytes(arq.read(11), "little")!=0:
            if int.from_bytes(arq.read(19), "little")==239:
                break
            byte += 32
            arq.seek((setoresBootRecord*bytesPorSetor)+byte)

        arq.seek((setoresBootRecord*bytesPorSetor)+byte)
        nome_arquivo_bytes = bytes(arquivo[1], 'ascii')
        arq.write(nome_arquivo_bytes[0:8])
        arq.write(b'\x00' * (8-len(nome_arquivo_bytes)))

        extensao_arquivo_bytes = bytes(arquivo[2], 'ascii')
        arq.write(extensao_arquivo_bytes[0:3])
        arq.write(b'\x00' * (3-len(extensao_arquivo_bytes)))

        arq.write(int.to_bytes(1, 1, "little"))
        arq.write(int.to_bytes(primeiroClusterLivre, 4, "little"))
        arq.write(int.to_bytes(arquivo[0], 3, "little"))


    

