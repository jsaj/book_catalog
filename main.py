import requests
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from io import BytesIO

from catalog_creation import catalog_creation

from conexao_mysql import conexao_mysql
import datetime

#conexão com o banco
conector_db = conexao_mysql()
conexao = conector_db.conectar_banco()

# Defina o título do aplicativo
st.title("Sistema de Gerenciamento de Livros")

obj = catalog_creation()

# Crie uma barra lateral com opções
op = st.sidebar.selectbox("Escolha uma opção:",
                          ["Catálogo", "Cadastrar livro", "Reservar livro", "Devolver livro"])

if op == "Cadastrar livro":
    st.header("Registrar Livro")

    isbn = st.text_input('Digite o ISBN do livro: ')
    if len(isbn) > 1 and len(isbn) <= 13:
        try:
            titulo, capa_url = obj.find_url_book(isbn)
            if not titulo:
                titulo = st.text_input('Informe o título do livro: ')

            # isbn_10, titulo, authors = obj.get_book_info_from_google_books(isbn)
            # if isbn_10 == None and titulo == None and authors == None:
            #     titulo = st.text_input('Informe o título do livro: ')
            #     capa_url = 'https://raw.githubusercontent.com/jsaj/book_catalog/master/images/sem-capa.jpg'
            # else:
            #     # capa_url = obj.find_url_book(isbn_10, titulo, authors)
            #     if capa_url == None and titulo != None:
            #         capa_url = 'https://raw.githubusercontent.com/jsaj/book_catalog/master/images/sem-capa.jpg'
            #     elif titulo == None:
            #         titulo = st.text_input('Informe o título do livro: ')

            qtd_disponivel = st.text_input('Informe a quantidade disponível: ')

            if titulo and titulo.strip():
                st.write('Título: ', titulo)
            image_bytes = requests.get(capa_url).content
            st.image(BytesIO(image_bytes), width=150)

            if st.button("Cadastrar"):
                colunas = '(isbn, titulo, capa, qt_disponivel)'
                valores = f"('{isbn}', '{titulo}', '{capa_url}', '{qtd_disponivel}')"
                conector_db.insert_data(conexao, 'catalogo_livros', colunas, valores)

                st.success("Livro cadastrado com sucesso!")
        except Exception as e:
            st.write(f"Ocorreu um erro: {str(e)}")
    else:
        st.write('Preencha os campos solicitados!')

elif op == 'Catálogo':
    # Carregar o catálogo de livros
    df_catalogo = conector_db.read_data(conexao, 'catalogo_livros')

    entrada_isbn_titulo = st.text_input('Digite o ISBN ou título do livro: ')

    if st.button("Consultar"):
        try:
            check_isbn = df_catalogo.loc[
                (df_catalogo['isbn'].astype(str).str.contains(entrada_isbn_titulo, case=False))
                | (df_catalogo['titulo'].str.contains(entrada_isbn_titulo, case=False))].reset_index(drop=True)

            if not check_isbn.empty:
                obj.consultar_livro(check_isbn)
            else:
                st.write('Livro não encontrado!')
        except Exception as e:
            st.write(f"Ocorreu um erro: {str(e)}")

    else:
        st.markdown("---")  # Adiciona uma linha de separação
        st.subheader('Catálogo de livros')

        num_columns = 3  # Defina o número de colunas desejado
        num_books = len(df_catalogo)
        num_rows = (num_books - 1) // num_columns + 1

        image_width = 200  # Defina a largura desejada para as imagens
        image_height = 250  # Defina a altura desejada para as imagens

        for row in range(num_rows):
            columns = st.columns(num_columns)
            for col in range(num_columns):
                index = row * num_columns + col
                if index < num_books:
                    isbn = df_catalogo.iloc[index]['isbn']
                    titulo = df_catalogo.iloc[index]['titulo']
                    capa_url = df_catalogo.iloc[index]['capa']
                    quantidade_disponivel = df_catalogo.iloc[index]['qt_disponivel']

                    try:
                        # Baixar a imagem do URL e redimensioná-la
                        response = requests.get(capa_url)
                        response.raise_for_status()

                        capa_bytes = BytesIO(response.content)
                        capa = Image.open(capa_bytes)
                        capa = capa.resize((image_width, image_height))

                        # Verificar a quantidade disponível e adicionar a marca "X" se for igual a 0
                        if quantidade_disponivel == 0:
                            draw = ImageDraw.Draw(capa)
                            x_mark_color = (255, 0, 0)  # Cor vermelha
                            x_mark_thickness = 5  # Espessura da linha da marca "X"

                            # Obter as coordenadas do centro da imagem
                            center_x, center_y = capa.size[0] // 2, capa.size[1] // 2

                            # Desenhar a marca "X" de canto a canto
                            draw.line([(0, 0), (capa.size[0], capa.size[1])], fill=x_mark_color, width=x_mark_thickness)
                            draw.line([(0, capa.size[1]), (capa.size[0], 0)], fill=x_mark_color, width=x_mark_thickness)

                            # Adicionar o texto "Indisponível" no centro da imagem em uma caixa de fundo branco
                            text = "Indisponível"
                            font = ImageFont.truetype("arial.ttf", 36)  # Escolha uma fonte e tamanho adequados
                            text_width, text_height = draw.textsize(text, font)
                            text_x = center_x - text_width // 2
                            text_y = center_y - text_height // 2

                            # Desenhar a caixa de fundo branca
                            draw.rectangle([(text_x, text_y), (text_x + text_width, text_y + text_height)],
                                           fill="white")

                            # Adicionar o texto no centro da caixa
                            draw.text((text_x, text_y), text, fill="black", font=font)


                        # Exibir a imagem redimensionada com a marca "X" e texto, se aplicável
                        columns[col].write(f"<p style='font-size: 14px; margin-bottom: 0px;'>ISBN: {isbn}</p>", unsafe_allow_html=True)
                        qt_disponivel = df_catalogo.loc[df_catalogo['isbn'] == isbn, 'qt_disponivel'].values[0]
                        # if qt_disponivel > 1:
                        #     columns[col].write(f"<p style='font-size: 14px;'>{qt_disponivel} Exemplares</p>", unsafe_allow_html=True)
                        # elif qt_disponivel == 1:
                        #     columns[col].write(f"<p style='font-size: 14px;'>{qt_disponivel} Exemplar</p>",
                        #                        unsafe_allow_html=True)
                        # else:
                        #     columns[col].write(f"<p style='font-size: 14px;'>Indisponível</p>",
                        #                        unsafe_allow_html=True)
                        columns[col].image(capa, caption=titulo, use_column_width=True)

                    except Exception as e:
                        st.write(f"Ocorreu um erro ao processar a imagem: {str(e)}")

elif op == 'Reservar livro':
    st.header("Reservar Livro")
    df_catalogo = conector_db.read_data(conexao, 'catalogo_livros')

    entrada_isbn_titulo = st.text_input('Digite o ISBN ou título do livro: ')

    try:
        check_isbn = df_catalogo.loc[
            (df_catalogo['isbn'].str.contains(entrada_isbn_titulo))
            | (df_catalogo['titulo'].str.contains(entrada_isbn_titulo))]

        if entrada_isbn_titulo != '' and len(check_isbn) > 0:
            qt_disponivel = check_isbn['qt_disponivel'].values[0]

            if qt_disponivel >= 1:
                if qt_disponivel > 1:
                    st.success(f'Há {qt_disponivel} exemplares deste livro disponíveis para reserva.')
                else:
                    st.success(f'Há {qt_disponivel} exemplar deste livro disponível para reserva.')

                form_info = st.form('Informação da reserva')

                with form_info:
                    st.markdown(
                        f'<h1 style="text-align:center;">Informação da reserva</h1>',
                        unsafe_allow_html=True
                    )
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"ISBN: {check_isbn['isbn'].values[0]}")
                        st.write(f"Título: {check_isbn['titulo'].values[0]}")
                        nome_aluno = st.text_input('Digite o nome do aluno:', value="")
                        st.text("")  # Adiciona um espaço em branco para ajustar a altura

                    with col2:
                        capa_url = check_isbn['capa'].values[0]
                        image_width = 200
                        image_height = 200

                        response = requests.get(capa_url)
                        if response.status_code == 200:
                            capa_bytes = BytesIO(response.content)
                            capa = Image.open(capa_bytes)
                            capa = capa.resize((image_width, image_height))
                            st.image(capa)

                    if form_info.form_submit_button('Confirmar reserva'):
                        data_reserva = datetime.datetime.now().strftime("%d-%m-%Y")

                        colunas = '(isbn, nome_aluno, data_reserva)'
                        valores = f"('{check_isbn['isbn'].values[0]}', '{nome_aluno}', '{data_reserva}')"
                        conector_db.insert_data(conexao, 'reserva_livros', colunas, valores)
                        form_info.success(f'Livro reservado com sucesso!')

                        conector_db.update_data(conexao,
                                                'catalogo_livros',
                                                'qt_disponivel',
                                                'isbn',
                                                qt_disponivel - 1,
                                                check_isbn['isbn'].values[0])
                        st.experimental_rerun()

            else:
                st.success(f'Não há exemplares deste livro disponíveis para reserva.')

        else:
            st.write('Preencha os campos solicitados!')

    except Exception as e:
        st.error(f"Ocorreu um erro: {str(e)}")

elif 'Devolver livro':

    try:
        st.header("Reservar Livro")

        df_reserva = conector_db.read_data(conexao, 'reserva_livros')
        df_catalogo = conector_db.read_data(conexao, 'catalogo_livros')

        entrada_isbn = st.text_input('Digite o ISBN do livro: ')
        entrada_aluno = st.text_input('Digite o nome do aluno: ')

        quantidade_disponivel = 0
        check_isbn = pd.DataFrame()
        if entrada_isbn:
            entrada_isbn = entrada_isbn.lower()

        if entrada_isbn and not entrada_aluno:
            check_isbn = df_reserva.loc[
                df_reserva['isbn'].str.lower().str.contains(entrada_isbn)].reset_index(drop=True)

            if not check_isbn.empty:
                quantidade_disponivel = \
                df_catalogo.loc[df_catalogo['isbn'] == entrada_isbn, 'qt_disponivel'].values[0]

        elif entrada_isbn and entrada_aluno:
            entrada_aluno = entrada_aluno.lower()
            check_isbn = df_reserva.loc[
                (df_reserva['isbn'].str.lower().str.contains(entrada_isbn))
                & (df_reserva['nome_aluno'].str.lower().str.contains(entrada_aluno))].reset_index(drop=True)

            if not check_isbn.empty:
                quantidade_disponivel = \
                df_catalogo.loc[df_catalogo['isbn'] == entrada_isbn, 'qt_disponivel'].values[0]

        if not entrada_isbn and not entrada_aluno:
            st.write('Preencha os campos solicitados!')

        elif not check_isbn.empty:
            # Exibir os detalhes dos livros lado a lado
            columns = st.columns(len(check_isbn))

            for index, row in check_isbn.iterrows():
                isbn = row['isbn']
                titulo = df_catalogo.loc[df_catalogo['isbn'] == isbn, 'titulo'].values[0]
                capa_url = df_catalogo.loc[df_catalogo['isbn'] == isbn, 'capa'].values[0]
                nome_aluno = row['nome_aluno']
                data_reserva = row['data_reserva']

                try:
                    # Baixar a imagem do URL e redimensioná-la
                    response = requests.get(capa_url)
                    if response.status_code == 200:
                        capa_bytes = BytesIO(response.content)
                        capa = Image.open(capa_bytes)
                        image_width = 150  # Defina a largura desejada para as imagens
                        image_height = 200  # Defina a altura desejada para as imagens
                        capa = capa.resize((image_width, image_height))

                        # Exibir a imagem redimensionada com a marca "X" e texto, se aplicável
                        with columns[index]:
                            html_code = f"""
                            <div style="margin-bottom: 0px;">ISBN: {isbn}</div>
                            <div style="margin-bottom: 0px;">Aluno: {nome_aluno}</div>
                            <div>Data da reserva: {data_reserva}</div>
                            """

                            st.markdown(html_code, unsafe_allow_html=True)

                            st.image(capa, caption=titulo, use_column_width=False)

                except Exception as e:
                    st.error(f"Erro ao carregar a imagem: {e}")

            if len(check_isbn) == 1:
                if st.button('Fazer devolução'):
                    try:
                        data_devolucao = datetime.datetime.now().strftime("%d-%m-%Y")

                        colunas = '(isbn, nome_aluno, data_devolucao)'
                        valores = f"('{check_isbn['isbn'].values[0]}', '{check_isbn['nome_aluno'].values[0]}', '{data_devolucao}')"
                        conector_db.insert_data(conexao, 'devolucao_livros', colunas, valores)

                        colunas = ['isbn', 'nome_aluno']
                        valores = [check_isbn['isbn'].values[0], check_isbn['nome_aluno'].values[0]]
                        conector_db.drop_data(conexao, 'reserva_livros', colunas, valores)

                        st.success(f'Devolução realizada com sucesso!')

                        conector_db.update_data(conexao,
                                                'catalogo_livros',
                                                'qt_disponivel',
                                                'isbn',
                                                quantidade_disponivel + 1,
                                                check_isbn['isbn'].values[0])
                    except Exception as e:
                        st.error(f"Erro ao fazer a devolução: {e}")

    except Exception as e:
        st.error(f"Erro: {e}")


