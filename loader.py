import os

def get_games():
    pasta = "games"
    arquivos = []
    nomes = []
    for nome_arquivo in os.listdir(pasta):
        caminho_completo = os.path.join(pasta, nome_arquivo)
        if os.path.isfile(caminho_completo):
            arquivos.append(caminho_completo)
            nomes.append(nome_arquivo)
    return arquivos, nomes


def choose_game():
    try:
        arquivos, nomes = get_games()
        for i, nome in enumerate(nomes):
            print(i+1, ":", nome)

        escolha = int(input("digite o indice do jogo que quer jogar: "))
        return arquivos[escolha-1]
    
    except:
        print("crie uma pasta games e adicione as roms la")
        exit()
