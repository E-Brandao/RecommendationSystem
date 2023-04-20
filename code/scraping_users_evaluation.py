import csv
import concurrent.futures
import requests

# Links
link_livros = 'https://www.skoob.com.br/v1/bookcase/books/%/shelf_id:1/page:1/limit:10000/'


# Variáveis globais
usuario_inicial = 150001
usuario_final = 200000
usuarios = []

dict_notas_arquivo = 'evaluation.csv'
dict_colunas_notas = ['user_id', 'book_id', 'evaluation']

dict_favoritos_arquivo = 'favorites.csv'
dict_colunas_favoritos = ['user_id', 'book_id']

dict_desejados_arquivo = 'to_read.csv'
dict_colunas_desejados = ['user_id', 'book_id']


# Funções

def escrever_csv(nome_arquivo, colunas, registros):
    with open(nome_arquivo, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = colunas)
        #writer.writeheader()
        writer.writerows(registros)
        csvfile.close()

def recuperar_informacoes(_usuario_atual):
    _dict_notas = []
    _dict_favoritos = []
    _dict_desejados = []

    response = requests.get(link_livros.replace('%', _usuario_atual))
    json_resposta = response.json()['response']

    if len(json_resposta) < 20:
        return
    
    for livro in json_resposta:
        _id_livro = livro['livro_id']
        _nota_livro = livro['ranking']
        _favorito = livro['favorito']
        _desejado = livro['desejado']

        if _nota_livro > 0:
            _dict_notas.append({'user_id': _usuario_atual, 'book_id': _id_livro, 'evaluation': _nota_livro})
        if _favorito != 0:
            _dict_favoritos.append({'user_id': _usuario_atual, 'book_id': _id_livro})
        if _desejado != 0:
            _dict_desejados.append({'user_id': _usuario_atual, 'book_id': _id_livro})
    
    escrever_csv(dict_notas_arquivo, dict_colunas_notas, _dict_notas)
    escrever_csv(dict_favoritos_arquivo, dict_colunas_favoritos, _dict_favoritos)
    escrever_csv(dict_desejados_arquivo, dict_colunas_desejados, _dict_desejados)


# Código main

for i in range(usuario_inicial, usuario_final+1):
    usuarios.append(str(i))

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(recuperar_informacoes, usuarios)