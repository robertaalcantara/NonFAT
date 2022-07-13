# operacoes = ['Abrir', 'Exportar', 'Adicionar', 'Formatar']

# aux = 0
# print("\nDigite o número da operação abaixo que deseja realizar:")
# for opcao in operacoes:
#     print(f"{aux} - {opcao}")
#     aux += 1
import os.path
nome = 'abre'
ext = '.txt'
path = 'C:\\Users\\leona\\Documents'

nomeCom = os.path.join(path, nome+ext)

with open(nomeCom,"w") as f:
    f.write('aaaaaaabbbbbbbbbbbbaaaaaaa')