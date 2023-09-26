import requests
import json
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from io import BytesIO
from streamlit_modal import Modal

from catalog_creation import catalog_creation
from streamlit_image_select import image_select
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
        isbn_10, titulo, authors = obj.get_book_info_from_google_books(isbn)
        if isbn_10 == None and titulo == None and authors == None:
            titulo = st.text_input('Informe o título do livro: ')
            capa_url = 'https://raw.githubusercontent.com/jsaj/book_catalog/master/images/sem-capa.jpg'
        else:
            capa_url = obj.find_url_book(isbn_10, titulo, authors)
            if capa_url == None and titulo != None:
                capa_url = 'https://raw.githubusercontent.com/jsaj/book_catalog/master/images/sem-capa.jpg'
            elif titulo == None:
                titulo = st.text_input('Informe o título do livro: ')

        qtd_disponivel = st.text_input('Informe a quantidade disponível: ')

        if titulo != None and titulo != ' ':
            st.write('Título: ', titulo)
        image_bytes = requests.get(capa_url).content
        st.image(BytesIO(image_bytes), width=150)

        if st.button("Cadastrar"):
            colunas = '(isbn, titulo, capa,quantidade_disponivel, reservado, data_reserva, nome_aluno, data_devolucao)'
            valores = f"('{isbn}', '{titulo}', '{capa_url}', {qtd_disponivel}, 'NAO', '', '', '')"
            conector_db.insert_data(conexao, 'catalog_book', colunas, valores)
            # obj.registrar_livro(isbn, titulo, capa_url)
            st.success("Livro cadastrado com sucesso!")
    else:
        st.write('ISBN inválido. Tente novamente!')

elif op == 'Catálogo':
    df_catalogo = conector_db.read_data(conexao, 'catalog_book')
    st.write(df_catalogo)

    entrada_isbn_titulo = st.text_input('Digite o ISBN ou título do livro: ')

    if st.button("Consultar"):
        check_isbn = df_catalogo.loc[
            (df_catalogo['isbn'].str.contains(entrada_isbn_titulo))
            | (df_catalogo['titulo'].str.contains(entrada_isbn_titulo))].reset_index(drop=True)
        if len(check_isbn) > 0:
            obj.consultar_livro(check_isbn)
        else:
            st.write('Livro não encontrado!')

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
                    quantidade_disponivel = df_catalogo.iloc[index]['quantidade_disponivel']

                    # Baixar a imagem do URL e redimensioná-la
                    response = requests.get(capa_url)
                    if response.status_code == 200:
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
                        columns[col].write(f"<p style='font-size: 14px;'>ISBN: {isbn}</p>", unsafe_allow_html=True)
                        columns[col].image(capa, caption=titulo, use_column_width=True)
elif op == 'Reservar livro':
    st.header("Reservar Livro")
    df_catalogo = conector_db.read_data(conexao, 'catalog_book')
    st.write(df_catalogo)

    entrada_isbn_titulo = st.text_input('Digite o ISBN ou título do livro: ')

    check_isbn = df_catalogo.loc[
        (df_catalogo['isbn'].str.contains(entrada_isbn_titulo))
        | (df_catalogo['titulo'].str.contains(entrada_isbn_titulo))]
    # Botão para abrir o modal
    if st.button("Consultar"):
        st.markdown(
            """
            <style>
            /* Estilo para esconder o modal inicialmente */
            .modal {
                display: none;
                background-color: rgba(0,0,0,0.0);
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 999;
            }

            /* Estilo para o conteúdo do modal */
            .modal-content {
                background-color: #fefefe;
                color: black; /* Cor do texto */
                border: 1px solid #888;
                width: 40%; /* Largura do modal */
                height: 50%; /* Altura do modal */
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                text-align: center;
                position: relative;
            }
            </style>
            <div class="modal" id="myModal">
                <div class="modal-content">
                    <span style="position: absolute; top: 10px; right: 20px; font-size: 24px; cursor: pointer;" onclick="closeModal()">&times;</span>
                    <h2>Informações da Reserva</h2>
                    <p>ISBN: 123456789</p>
                    <p>Título: Livro XYZ</p>
                    <p>Nome do Aluno: [Digite o nome aqui]</p>
                    <button onclick="confirmReserva()">Confirmar Reserva</button>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        # # Botão para abrir o modal
        # if st.button("Reservar"):
        #     st.markdown(
        #         """
        #         <div style="background-color: rgba(0,0,0,0.7); position: fixed; top: 0; left: 0; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; z-index: 999;">
        #             <div style="background-color: #fefefe; padding: 20px; border: 1px solid #888; width: 50%; box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2); text-align: center; position: relative; color: black;">
        #                 <span style="position: absolute; top: 10px; right: 20px; font-size: 24px; cursor: pointer;" onclick="closeModal()">&times;</span>
        #                 <h2 style="color: black;">Informações da Reserva</h2>
        #                 <p style="color: black;"> <b>ISBN:</b> 123456789</p>
        #                 <p style="color: black;">Título: Livro XYZ</p>
        #                 <p style="color: black;">Nome do Aluno: <span style="color: black;">[Digite o nome aqui]</span></p>
        #                 <button onclick="confirmReserva()">Confirmar Reserva</button>
        #             </div>
        #         </div>
        #         <script>
        #             // Função para fechar o modal
        #             function closeModal() {
        #                 var modal = document.querySelector(".modal");
        #                 modal.style.display = "none";
        #             }
        #
        #             // Função para confirmar a reserva
        #             function confirmReserva() {
        #                 alert("Reserva confirmada!");
        #                 closeModal();
        #             }
        #         </script>
        #         """
        #         , unsafe_allow_html=True
        #     )
    # # Botão para abrir o modal
    # if st.button("Reservar"):
    #     st.markdown(
    #         """
    #         <script>
    #             openModal(); // Abre o modal ao clicar no botão
    #         </script>
    #         """
    #         , unsafe_allow_html=True
    #     )

# elif op == 'Reservar livro':
#     st.header("Reservar Livro")
#     df_catalogo = conector_db.read_data(conexao, 'catalog_book')
#     st.write(df_catalogo)
#
#     entrada_isbn_titulo = st.text_input('Digite o ISBN ou título do livro: ')
#
#     check_isbn = df_catalogo.loc[
#         (df_catalogo['isbn'].str.contains(entrada_isbn_titulo))
#         | (df_catalogo['titulo'].str.contains(entrada_isbn_titulo))]
#
#     open_modal = st.button("Reservar livro")
#
#     if open_modal and len(check_isbn) > 0 and entrada_isbn_titulo != '':
#         qt_disponivel = check_isbn['quantidade_disponivel'].values[0]
#         st.write(qt_disponivel)
#         # if qt_disponivel => 1:
#         #     st.write(f'Há {qt_disponivel} exemplares deste livro disponíveis')
#
#         modal = Modal(key='exemplo', title='')
#         modal.open()
#
#         with modal.container():
#             # Exibir a imagem do livro à direita das informações
#             st.write("<style>div.Modal div[role='dialog'] { background-color: white; }</style>",
#                      unsafe_allow_html=True)
#
#             col1, col2 = st.columns([1, 2])
#             col1.image(check_isbn.iloc[0]['capa'], use_column_width='auto')
#             col2.write("<h2 style='color: black;'>Informações da reserva</h2>", unsafe_allow_html=True)
#             col2.write(f"<span style='color: black;'><b>ISBN:</b> {check_isbn.iloc[0]['isbn']}</span>",
#                        unsafe_allow_html=True)
#             col2.write(f"<span style='color: black;'><b>Título:</b> {check_isbn.iloc[0]['titulo']}</span>",
#                        unsafe_allow_html=True)
#             col2.write("<span style='color: black; margin-top: -20px'><b>Preencha com o nome do aluno:</b></span>",
#                        unsafe_allow_html=True)
#             nome_aluno = col2.text_input("")
#
#             if col2.button('Confirmar Reserva'):
#                 isbn = check_isbn['isbn'].drop_duplicates().values[0]
#                 data_reserva = datetime.datetime.now().strftime("%d-%m-%Y")
#                 colunas = '(isbn, nome_aluno, data_reserva)'
#                 valores = f"('{isbn}', '{nome_aluno}', '{data_reserva}')"
#
#                 conector_db.insert_data(conexao, 'reserva_livro', colunas, valores)
#
#                 tabela = 'catalog_book'
#                 coluna_alterar = 'quantidade_disponivel'
#                 coluna_condicao = 'isbn'
#                 valor_condicao = isbn
#
#                 valor_alterar = qt_disponivel - 1
#
#                 conector_db.update_data(conexao, tabela, coluna_alterar, coluna_condicao, valor_alterar)
            #     col2.write(f"<span style='color: black;'>Reserva confirmada para {nome_aluno}</span>",
            #                unsafe_allow_html=True)
            #     modal.close()
            #
            #     # modal.close()
            # obj.consultar_livro(check_isbn)

    #
    #     else:
    #         st.write(f'Não há exemplar deste livro disponível')
    #
    #     st.markdown("---")  # Adiciona uma linha de separação
    #
    #
    #
    # elif open_modal and entrada_isbn_titulo == '':
    #     st.write('Valor informado não aceito. Tente novamente!')
    #
    # elif open_modal and len(check_isbn) < 1:
    #     st.write('Livro não encontrato ou não está disponível para reserva. Tente novamente!')

# elif 'Devolver livro':
#     st.header("Devolver Livro")
#
#     isbn = st.text_input('Digite o ISBN do livro: ', value='')
#     nome_aluno = st.text_input('Digite o nome do aluno: ', value='')
#
#     dataset = conector_db.read_data(conexao, 'reserva_livro')
#
#     check_isbn = dataset.loc[
#         (dataset['isbn'].str.contains(isbn))
#         | (dataset['nome_aluno'].str.contains(nome_aluno))]
#
#     open_modal = st.button("Verificar reserva")
#     st.markdown("---")  # Adiciona uma linha de separação
#
#     st.table(check_isbn)
#
#     if open_modal and len(check_isbn) > 0:
#         st.write('modal')
#         modal = Modal(key='exemplo', title='')
#         modal.open()
#
#         if modal.is_open():
#             with modal.container():
#                 # Exibir a imagem do livro à direita das informações
#                 st.write("<style>div.Modal div[role='dialog'] { background-color: white; }</style>",
#                          unsafe_allow_html=True)
#
#                 col1, col2 = st.columns([1, 2])
#                 # col1.image(check_isbn.iloc[0]['capa'], use_column_width='auto')
#                 col2.write("<h2 style='color: black;'>Informações da reserva</h2>", unsafe_allow_html=True)
#                 col2.write(f"<span style='color: black;'><b>ISBN:</b> {check_isbn.iloc[0]['isbn']}</span>",
#                            unsafe_allow_html=True)
#                 col2.write(
#                     f"<span style='color: black;'><b>Nome do aluno:</b> {check_isbn.iloc[0]['nome_aluno']}</span>",
#                     unsafe_allow_html=True)
#     elif open_modal and len(isbn) != 13:
#         st.write('Reserva não encontrada. Tente novamente!')
#