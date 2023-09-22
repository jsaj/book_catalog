from PIL import Image
from pyzbar.pyzbar import decode
import streamlit as st
import cv2
import pandas as pd
import numpy as np
import requests
import json
from bs4 import BeautifulSoup
import io

class catalog_creation:

    def identificar_codigo_barra(self, path):

        # Carregue a imagem do print ou capture-a usando uma biblioteca como o OpenCV
        # imagem = cv2.imread(path)  # Substitua 'print.png' pelo caminho da sua imagem de print
        imagem = Image.open(path)

        # Converta a imagem para tons de cinza para facilitar o processamento
        # imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

        # Use a função decode da biblioteca pyzbar para decodificar os códigos de barras
        resultados = decode(imagem)

        # Verifique se algum código de barras foi encontrado
        if resultados:
            for resultado in resultados:
                codigo = resultado.data.decode('utf-8')
                return codigo
        else:
            print('Nenhum código de barras encontrado na imagem do print.')
            return '0'

    def buscar_titulo_e_capa_por_isbn(self, isbn):
        # URL da API do Google Books
        url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}'

        try:
            # Faz uma solicitação GET para a API do Google Books
            response = requests.get(url)

            # Verifica se a solicitação foi bem-sucedida
            if response.status_code == 200:
                # Parseia a resposta JSON
                data = json.loads(response.text)

                # Verifica se há resultados
                if 'items' in data:
                    # Obtém o título do primeiro resultado
                    primeiro_resultado = data['items'][0]
                    titulo = primeiro_resultado['volumeInfo']['title']

                    # Tenta obter a URL da imagem da capa da API do Google Books
                    if 'imageLinks' in primeiro_resultado['volumeInfo']:
                        capa_url = primeiro_resultado['volumeInfo']['imageLinks']['thumbnail']
                    else:
                        capa_url = None

                    # Se a URL da capa não estiver disponível, tente fontes alternativas
                    if not capa_url:
                        capa_url = self.buscar_capa_em_fontes_alternativas(isbn)
                        # if not capa_url:


                    return titulo, capa_url
                else:
                    return "Nenhum resultado encontrado. Verifique o ISBN informado e tente novamente!", None
            else:
                return f"Erro na solicitação: Código de status {response.status_code}", None
        except Exception as e:
            return f"Erro ao buscar título: {str(e)}", None

    def buscar_capa_em_fontes_alternativas(self, isbn):

        """
           Encontra a capa do livro com base no ISBN.

           Args:
               isbn: O ISBN do livro.

           Returns:
               A imagem da capa do livro.
           """

        # Obtém a URL da capa do livro.
        url = "https://openlibrary.org/api/covers/get?format=jpg&identifier={}".format(isbn)
        response = requests.get(url)

        # Verifica se a solicitação foi bem-sucedida.
        if response.status_code != 200:
            raise Exception("Não foi possível encontrar a capa do livro.")

        # Obtém a imagem da capa do livro.
        image_data = response.content

        # Cria uma imagem a partir dos dados da imagem.
        image = Image.open(io.BytesIO(image_data))

        return image

    def registrar_livro(self, isbn, titulo, capa_url):
        dataset = pd.read_csv('C:\\Users\\Jjr_a\\PycharmProjects\\book_read_barcode\\dataset_livros.csv')
        dataset['ISBN'] = dataset['ISBN'].astype(str)

        st.write(dataset['ISBN'])
        check_cod = dataset.loc[dataset['ISBN'] == isbn]

        if len(check_cod) == 0:
            # Crie uma nova linha como um dicionário de dados
            nova_linha = {'ISBN': isbn,
                          "TITULO": titulo,
                          "CAPA": capa_url,
                          'RESERVADO': 'NÃO',
                          'DATA_RESERVA': '',
                          'NOME_ALUNO': '',
                          'DATA_DEVOLUCAO': ''}

            # Use o método append para adicionar a nova linha ao DataFrame
            dataset = dataset.append(nova_linha, ignore_index=True)
            st.table(dataset)
            dataset.to_csv('C:\\Users\\Jjr_a\\PycharmProjects\\book_read_barcode\\dataset_livros.csv', index=False)
            st.write('Livro Registrado!')
        else:
            st.write('Código de barras já registrado!')

    def reservar_livro(self, codigo_de_barra, nome_aluno):
        dataset = pd.read_csv('C:\\Users\\Jjr_a\\PycharmProjects\\book_read_barcode\\dataset_livros.csv')
        dataset['codigo_de_barra'] = dataset['codigo_de_barra'].astype(str)

        check = dataset[dataset['codigo_de_barra'] == codigo_de_barra]

        if len(check) == 0:
            print('Livro não cadastrado ou falha na leitura do código de barras.')
            print('Tente novamente!')
        else:
            # Use loc para definir os valores com base na condição
            dataset.loc[dataset['codigo_de_barra'] == codigo_de_barra, 'reservado'] = 'Sim'
            dataset.loc[dataset['codigo_de_barra'] == codigo_de_barra, 'identificacao'] = nome_aluno

            dataset.to_csv('C:\\Users\\Jjr_a\\PycharmProjects\\book_read_barcode\\dataset_livros.csv', index=False)

        st.table(dataset)


    def consultar_livro(self, codigo_de_barra, op):
        return 0