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

def inserir_arquivo(arq, primeiroClusterLivre, bytesPorSetor, setoresPorCluster, setoresBootRecord, numSetoresRootDir, totalSetores):

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
        #verificar se ainda sobrou clusters livres a frente. Se sobrou, br aponta para esse cluster livre e 
        # cluster livre aponta pro proximo cluster livre. Senao sobrou é simplesmente o br aponto pro proximo cluster livre

        clusters_livres = qtd_clusters_livres - qtd_cluster_arquivo
        if(clusters_livres > 0):
            
            prim_cluster_livre_atual = primeiroClusterLivre + qtd_cluster_arquivo

            #atualizar próximo bloco
            prim_setor_livre_atual = setoresBootRecord + numSetoresRootDir + (prim_cluster_livre_atual*setoresPorCluster)
            arq.seek(bytesPorSetor*prim_setor_livre_atual)

            #tamanho em clusters
            arq.write(int.to_bytes(clusters_livres, 4, "little"))

            proximo = proximo_cluster_livre
            arq.write(int.to_bytes(proximo, 4, "little"))  

        else:
            prim_cluster_livre_atual = proximo_cluster_livre
        
        #senao, quer dizer que acabou os clusters livres daquele bloco de clusters livres. Verificar
        # se a qtd_clusters_livres é a qtd total do arquivo, senao for, quer dizer que tem mais
        # clusters livres a frente. Dessa forma, verifica o ponteiro pro proximo e ai atualiza a partir dele.  

        #atualizar BR
        arq.seek(9)
        arq.write(int.to_bytes(prim_cluster_livre_atual, 4, "little"))

    #senao, ir pro proximo cluster livre e ver se tem o suficiente vago

    #setor_livre_atual = setores_prim_bloco_livre
    #setor_bloco_livre = setor_livre_atual + ((proximo_bloco_livre - primeiroClusterLivre) * setoresPorCluster)

    #while(tamanho_blocos_livres < arquivo[0] and proximo_bloco_livre != 16777215):

            #arq.seek(bytesPorSetor*setor_bloco_livre)
            #bloco_livre = arq.read(setor_bloco_livre+7)
            #tamanho_blocos_livres = int.from_bytes(bloco_livre[0:3], "little")
            #proximo_bloco_livre = int.from_bytes(bloco_livre[4:7], "little")
            #setor_livre_atual = setor_bloco_livre
            #setor_bloco_livre = setor_livre_atual

    


    

