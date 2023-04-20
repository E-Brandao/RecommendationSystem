import csv
import concurrent.futures
import requests
import pandas as pd
from unidecode import unidecode
import os
import json

# Links
link_livros = 'https://www.skoob.com.br/v1/book/%/user_id:2439910/stats:true/'


# Variáveis globais
json_sinopse = []

dict_livros_arquivo = 'books_synopsis.csv'
dict_colunas_livros = ['book_id', 'synopsis', 'name']
dict_livros_arquivo_2 = 'info_books_2.csv'
dict_colunas_livros_2 = ['book_id', 'synopsis', 'name', 'new_id']

# Funções

def escrever_csv(nome_arquivo, colunas, registros):
    with open(nome_arquivo, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = colunas)
        #writer.writeheader()
        writer.writerows(registros)
        csvfile.close()

def recuperar_2(_livro_atual):
    global json_sinopse

    _dict_livros = []

    response = requests.get(link_livros.replace('%', _livro_atual))
    json_resposta = response.json()['response']

    if len(json_resposta) == 0:
        return

    if int(json_resposta['estatisticas']['qt_avaliadores']) < 1000 or json_resposta['idioma'] != 'br':
        return

    if json_resposta['sinopse'] == '':
        return

    sinopse = unidecode(json_resposta['sinopse'])
    sinopse = sinopse.replace("\n", "").replace("\r", "")
    nome = unidecode(json_resposta['titulo'])
    new_id = json_resposta['livro_id']

    json_sinopse.append({'book_id': _livro_atual, 'synopsis': sinopse, 'name': nome, 'new_id': new_id})
    #_dict_livros.append({'book_id': _livro_atual, 'synopsis': sinopse, 'name': nome, 'new_id': new_id})
    #escrever_csv(dict_livros_arquivo_2, dict_colunas_livros_2, _dict_livros)

def recuperar_informacoes(_livro_atual):
    _dict_livros = []

    response = requests.get(link_livros.replace('%', _livro_atual))
    json_resposta = response.json()['response']

    if len(json_resposta) == 0:
        return

    if int(json_resposta['estatisticas']['qt_avaliadores']) < 1000 or json_resposta['idioma'] != 'br':
        return

    sinopse = unidecode(json_resposta['sinopse'])
    sinopse = sinopse.replace("\n", "").replace("\r", "")
    nome = unidecode(json_resposta['titulo'])

    _dict_livros.append({'book_id': _livro_atual, 'synopsis': sinopse, 'name': nome})
    escrever_csv(dict_livros_arquivo, dict_colunas_livros, _dict_livros)


# Código main
maior_id = 1219305
livros = [str(x) for x in range(1, maior_id)]

#df_books = pd.read_csv('info_books_2.csv', on_bad_lines='skip')
#id_livros = df_books['book_id'].values.tolist()
#id_livros = [x.split(',')[0] for x in id_livros]

with concurrent.futures.ThreadPoolExecutor() as executor:
    #executor.map(recuperar_informacoes, livros)
    executor.map(recuperar_2, livros)

jsonString = json.dumps(json_sinopse)
jsonFile = open("data_livros.json", "w")
jsonFile.write(jsonString)
jsonFile.close()