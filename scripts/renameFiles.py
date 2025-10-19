import os

def renomear_fotos(caminho_da_pasta):
    """
    Renomeia todos os arquivos em uma pasta sequencialmente como Imagem01, Imagem02, etc.

    :param caminho_da_pasta: O caminho para a pasta que contém as imagens.
    """
    # Verifica se o caminho da pasta existe
    if not os.path.isdir(caminho_da_pasta):
        print(f"Erro: A pasta '{caminho_da_pasta}' não foi encontrada.")
        return

    # Lista todos os arquivos na pasta
    try:
        arquivos = os.listdir(caminho_da_pasta)
    except OSError as e:
        print(f"Erro ao acessar a pasta: {e}")
        return

    # Filtra para incluir apenas os tipos de imagem mais comuns (opcional)
    extensoes_de_imagem = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
    imagens = [arquivo for arquivo in arquivos if arquivo.lower().endswith(extensoes_de_imagem)]

    # Ordena os arquivos para garantir uma nomeação consistente
    imagens.sort()

    contador = 1
    for nome_antigo in imagens:
        # Pega a extensão do arquivo
        extensao = os.path.splitext(nome_antigo)[1]

        # Formata o novo nome com um zero à esquerda para números de 1 a 9
        novo_nome = f"Imagem{contador:02d}{extensao}"

        # Monta o caminho completo para o arquivo antigo e o novo
        caminho_antigo = os.path.join(caminho_da_pasta, nome_antigo)
        caminho_novo = os.path.join(caminho_da_pasta, novo_nome)

        # Renomeia o arquivo
        try:
            os.rename(caminho_antigo, caminho_novo)
            print(f"Renomeado: '{nome_antigo}' para '{novo_nome}'")
            contador += 1
        except OSError as e:
            print(f"Erro ao renomear o arquivo {nome_antigo}: {e}")

# --- Como usar o script ---
if __name__ == "__main__":
    # IMPORTANTE: Substitua "C:/Caminho/Para/Sua/PastaDeFotos" pelo caminho real da sua pasta.
    # Exemplo para Windows: "C:\\Users\\SeuUsuario\\Desktop\\Fotos"
    # Exemplo para macOS/Linux: "/home/SeuUsuario/Imagens/Viagem"
    pasta_de_fotos = "/home/gustavo/Projects/trabalhoaps/dados/chave_inglesa"

    renomear_fotos(pasta_de_fotos)