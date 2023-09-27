from PIL import Image
import streamlit as st
import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
import io
from io import BytesIO
import streamlit as st
import av
import numpy as np

from streamlit_webrtc import webrtc_streamer
class catalog_creation():
    # def identificar_codigo_barra(self, path):
    #
    #     # Carregue a imagem do print ou capture-a usando uma biblioteca como o OpenCV
    #     # imagem = cv2.imread(path)  # Substitua 'print.png' pelo caminho da sua imagem de print
    #     imagem = Image.open(path)
    #
    #     # Converta a imagem para tons de cinza para facilitar o processamento
    #     # imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    #
    #     # Use a função decode da biblioteca pyzbar para decodificar os códigos de barras
    #     resultados = decode(imagem)
    #
    #     # Verifique se algum código de barras foi encontrado
    #     if resultados:
    #         for resultado in resultados:
    #             codigo = resultado.data.decode('utf-8')
    #             return codigo
    #     else:
    #         print('Nenhum código de barras encontrado na imagem do print.')
    #         return '0'

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

                    # Se a URL da capa não estiver disponível, use a URL pública do GitHub para uma imagem de capa padrão
                    if not capa_url:
                        capa_url = 'https://raw.githubusercontent.com/jsaj/book_catalog/d468412eaa4a651c553096bf4e7b467e43aa41d0/images/sem-capa.jpg?token=GHSAT0AAAAAACH5BCCHVLYZUML5MUJZJWRYZINXCMQ'

                    return titulo, capa_url
                else:
                    st.write("Nenhum resultado encontrado. Verifique o ISBN informado ou cadastre manualmente!")
                    return None, None
            else:
                return f"Erro na solicitação: Código de status {response.status_code}", None
        except Exception as e:
            # Em caso de erro, use a URL pública do GitHub para uma imagem de capa padrão
            capa_url = 'https://raw.githubusercontent.com/jsaj/book_catalog/master/images/sem-capa.jpg'
            return f"Erro ao buscar título: {str(e)}", capa_url
    # def find_url_book(self, isbn_10, titulo, authors, max_attempts=10):
    #
    #     if isbn_10 != None:
    #         if ' ' in titulo:
    #             titulo = titulo.replace(' ', '-')
    #         if ' ' in authors[0]:
    #             authors = authors[0].replace(' ', '-')
    #
    #         url = "https://www.amazon.com.br/{}-{}/dp/{}".format(titulo, authors, isbn_10)
    #
    #         for _ in range(max_attempts):
    #
    #             response = requests.get(url)
    #             soup = BeautifulSoup(response.text, "html.parser")
    #
    #             # Use uma expressão regular para encontrar o link
    #             padrao = r'data-a-dynamic-image=\'{\"(https://[^"]+)\"'
    #             correspondencias = re.search(padrao, str(soup))
    #
    #             # Verifique se houve correspondência e obtenha o primeiro link
    #             if correspondencias:
    #                 primeiro_link = correspondencias.group(1)
    #                 return primeiro_link
    #         #     else:
    #         #         # st.write("Tentativa sem sucesso. Tentando novamente...")
    #         #
    #         # st.write(f"Nenhum link encontrado após {max_attempts} tentativas.")
    #         return None
    def find_url_book(self, isbn, max_attempts=10):
        url = f'https://www.amazon.com.br/s?i=stripbooks&rh=p_66%3A{isbn}&s=relevanceexprank&Adv-Srch-Books-Submit.x=0&Adv-Srch-Books-Submit.y=0&unfiltered=1&ref=sr_adv_b'

        titulo, capa_url = None, None
        for _ in range(max_attempts):

            response = requests.get(url)

            # Verifica se a solicitação foi bem-sucedida.
            if response.status_code != 200:
                print('Erro ao acessar a página da Amazon.')
            else:
                try:
                    html_string = BeautifulSoup(response.text, 'html.parser')

                    # Encontre a tag 'img' dentro da tag 'div' com a classe específica
                    img_tag = html_string.find('div', class_='a-section aok-relative s-image-fixed-height').find('img')

                    # Encontre o elemento HTML que contém o título do livro (pode variar na estrutura da página).
                    titulo = img_tag['alt']

                    # Obtenha o valor do atributo 'src' da tag 'img'
                    capa_url = img_tag['src']
                except Exception as e:
                    capa_url = None

            if capa_url:
                break


        if titulo and capa_url:
            return titulo, capa_url
        elif titulo and not capa_url:
            st.write('Capa do livro NÃO encontrada!')
            capa_url = 'https://raw.githubusercontent.com/jsaj/book_catalog/master/images/sem-capa.jpg'
            return titulo, capa_url
        elif not titulo and not capa_url:
            st.write('Título e capa do livro NÃO encontrados!')
            capa_url = 'https://raw.githubusercontent.com/jsaj/book_catalog/master/images/sem-capa.jpg'
            return None, capa_url

    def get_book_info_from_google_books(self, isbn):
        """
        Encontra informações sobre o livro com base no ISBN.

        Args:
            isbn: O ISBN do livro.

        Returns:
            Um dicionário com informações sobre o livro, ou None se o livro não for encontrado.
        """

        url = "https://www.googleapis.com/books/v1/volumes?q=isbn:{}".format(isbn)
        response = requests.get(url)

        # Verifica se a solicitação foi bem-sucedida.
        if response.status_code != 200:
            return None

        # Obtém as informações do livro.
        json_data = response.json()
        if "items" not in json_data:
            st.write("Nenhum resultado encontrado. Verifique o ISBN informado ou cadastre manualmente!")
            return None, None, None
        else:
            # Retorna as informações do livro.
            isbn_10 = json_data["items"][0]['volumeInfo']['industryIdentifiers'][0]['identifier']
            titulo = json_data["items"][0]['volumeInfo']['title']
            authors = json_data["items"][0]['volumeInfo']['authors']
            return isbn_10, titulo, authors
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

    # def registrar_livro(self,  banco, table, columns, values):
    #
    #     columns = '(isbn, titulo, capa,quantidade_disponivel, reservado, data_reserva, nome_aluno, data_devolucao)'
    #     values = "('123456789xyz', 'livro01', 'xxx', 1, 'NAO', '', '', '')"
    #
    #     dataset = pd.read_csv('C:\\Users\\Jjr_a\\PycharmProjects\\book_catalog\\dataset_livros.csv')
    #     dataset['ISBN'] = dataset['ISBN'].astype(str)
    #
    #     check_cod = dataset.loc[dataset['ISBN'] == isbn]
    #
    #     if len(check_cod) == 0:
    #         # Crie uma nova linha como um dicionário de dados
    #         nova_linha = {'ISBN': isbn,
    #                       "TITULO": titulo,
    #                       "CAPA": capa_url,
    #                       'RESERVADO': 'NÃO',
    #                       'DATA_RESERVA': '',
    #                       'NOME_ALUNO': '',
    #                       'DATA_DEVOLUCAO': ''}
    #
    #         # Use o método append para adicionar a nova linha ao DataFrame
    #         dataset = dataset.append(nova_linha, ignore_index=True)
    #         dataset.to_csv('C:\\Users\\Jjr_a\\PycharmProjects\\book_catalog\\dataset_livros.csv', index=False)
    #         st.write('Livro registrado!')
    #     else:
    #         st.write('Código de barras já registrado!')

    def reservar_livro(self, codigo_de_barra, nome_aluno):
        dataset = pd.read_csv('C:\\Users\\Jjr_a\\PycharmProjects\\book_catalog\\dataset_livros.csv')
        dataset['codigo_de_barra'] = dataset['codigo_de_barra'].astype(str)

        check = dataset[dataset['codigo_de_barra'] == codigo_de_barra]

        if len(check) == 0:
            print('Livro não cadastrado ou falha na leitura do código de barras.')
            print('Tente novamente!')
        else:
            # Use loc para definir os valores com base na condição
            dataset.loc[dataset['codigo_de_barra'] == codigo_de_barra, 'reservado'] = 'Sim'
            dataset.loc[dataset['codigo_de_barra'] == codigo_de_barra, 'identificacao'] = nome_aluno

            dataset.to_csv('C:\\Users\\Jjr_a\\PycharmProjects\\book_catalog\\dataset_livros.csv', index=False)

        st.table(dataset)

    def consultar_livro(self, info_livro):
        num_columns = 3  # Defina o número de colunas desejado
        num_books = len(info_livro)
        num_rows = (num_books - 1) // num_columns + 1

        image_width = 200  # Defina a largura desejada para as imagens
        image_height = 300  # Defina a altura desejada para as imagens

        for row in range(num_rows):
            columns = st.columns(num_columns)
            for col in range(num_columns):
                index = row * num_columns + col
                if index < num_books:
                    isbn = info_livro.iloc[index]['isbn']
                    titulo = info_livro.iloc[index]['titulo']
                    capa_url = info_livro.iloc[index]['capa']

                    # Baixar a imagem do URL e redimensioná-la
                    response = requests.get(capa_url)
                    if response.status_code == 200:
                        capa_bytes = BytesIO(response.content)
                        capa = Image.open(capa_bytes)
                        capa = capa.resize((image_width, image_height))

                        # Exibir a imagem redimensionada
                        columns[col].write(f"<p style='font-size: 14px;'>ISBN: {isbn}</p>", unsafe_allow_html=True)
                        columns[col].image(capa, caption=titulo, use_column_width=True)

    def atualizar_capa(self, op, df):
        if op == 'Sim':

            # Widget de upload de arquivo
            uploaded_file = st.file_uploader("Escolha uma imagem...", type=["jpg", "jpeg", "png"])

            # Verificar se um arquivo foi carregado
            if uploaded_file is not None:
                # Exibir a imagem carregada
                st.image(uploaded_file, caption="Imagem Carregada", use_column_width=True)

                # Você também pode salvar a imagem ou realizar outras operações com ela
                # Por exemplo, para salvar a imagem carregada em um arquivo:
                # with open("imagem_carregada.jpg", "wb") as f:
                #     f.write(uploaded_file.read())
                #
                # st.success("Imagem carregada e salva com sucesso!")

            # Nota informativa
            st.info("Faça o upload de uma imagem nos formatos JPG, JPEG, PNG ou GIF.")

        else:
            return df['capa'].values[0]