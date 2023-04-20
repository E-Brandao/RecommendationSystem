import csv
import json
import concurrent.futures
import requests
import content_based
from unidecode import unidecode
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
import prepare_data

# Links
link_livros = 'https://www.skoob.com.br/v1/bookcase/books/{0}/shelf_id:1/page:1/limit:10000/'
link_sinopse = 'https://www.skoob.com.br/v1/book/{0}/user_id:8833239/stats:true/'

# Variáveis globais
dict_livros_arquivo = '../data/recent_readings.csv'
dict_colunas_livros = ['user_id', 'new_id', 'order']
json_sinopse = []
livros_inseridos = []
count_users = 0

# Funções
def escrever_csv(nome_arquivo, colunas, registros):
    with open(nome_arquivo, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = colunas)
        #writer.writeheader()
        writer.writerows(registros)
        csvfile.close()

def recuperar_livros(_usuario_atual):
    global count_users
    global json_sinopse
    global lista_livros

    count_users += 1
    print(count_users)

    response = requests.get(link_livros.format(_usuario_atual))
    json_resposta = response.json()['response']

    for i in range(len(json_resposta)):
        if json_resposta[i]['id'] not in lista_livros:
            lista_livros.append(json_resposta[i]['id'])

def recuperar_sinopse(_livro):
    global count_users
    global json_sinopse

    count_users += 1
    print(count_users)
    _dict_livros = []

    response = requests.get(link_sinopse.format(_livro))
    json_resposta = response.json()['response']

    _id = json_resposta['livro_id']
    _nome = json_resposta['titulo']
    _sinopse = unidecode(json_resposta['sinopse'])
    _sinopse = _sinopse.replace("\n", "").replace("\r", "")
    _dict_sinopse = {'new_id': _id, 'synopsis': _sinopse, 'name': _nome}
    json_sinopse.append(_dict_sinopse)

def recuperar_informacoes(_usuario_atual):
    global count_users
    global json_sinopse

    count_users += 1
    print(count_users)
    #_dict_livros = []

    response = requests.get(link_livros.format(_usuario_atual))
    json_resposta = response.json()['response']

    for i in range(len(json_resposta)):
        _old_id = json_resposta[i]['edicao']['id']
        _id = json_resposta[i]['livro_id']
        _nome = json_resposta[i]['edicao']['titulo']
        _sinopse = unidecode(json_resposta[i]['edicao']['sinopse'])
        _sinopse = _sinopse.replace("\n", "").replace("\r", "")
        _dict_sinopse = {'new_id': _id, 'old_id': _old_id, 'synopsis': _sinopse, 'name': _nome}
        if _id not in livros_inseridos and _sinopse != "":
            json_sinopse.append(_dict_sinopse)
            livros_inseridos.append(_id)

        if i <= 3:
            _dict_livros.append({'user_id': _usuario_atual, 'new_id': _id, 'order': i})

    escrever_csv(dict_livros_arquivo, dict_colunas_livros, _dict_livros)

# Código main
#df_recents = content_based.load_recents()
data = prepare_data.load_data()
#list_recents = df_recents['new_id'].unique()
#list_evaluation = data.df['new_id'].unique()
#list_books = np.append(list_recents, list_evaluation)
#list_books = list_books.astype(str)
#list_books_reduced = np.delete(np.unique(list_books), -1)
users_list = data.df['user_id'].unique().tolist()

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(recuperar_informacoes, users_list)

#with concurrent.futures.ThreadPoolExecutor() as executor:
    #executor.map(recuperar_livros, users_list)

#count_users = 0

#with concurrent.futures.ThreadPoolExecutor() as executor:
    #executor.map(recuperar_informacoes, livros)
    #executor.map(recuperar_sinopse, list_books_reduced)

json_sinopse = [x for x in json_sinopse if x['synopsis'] != ""]
jsonString = json.dumps(json_sinopse)
jsonFile = open("../data/data_books_reduced.json", "w")
jsonFile.write(jsonString)
jsonFile.close()
