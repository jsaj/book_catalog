import requests
import json
import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO

from book_barcode import book_bardcode
from streamlit_image_select import image_select
# Defina o título do aplicativo
st.title("Sistema de Gerenciamento de Livros")

# dataset = pd.DataFrame(columns=['ISBN', 'TITULO', 'CAPA', 'RESERVADO', 'DATA_RESERVA', 'NOME_ALUNO', 'DATA_DEVOLUCAO'])
# dataset.to_csv('C:\\Users\\Jjr_a\\PycharmProjects\\book_read_barcode\\dataset_livros.csv', index=False)

# dataset = pd.read_csv('C:\\Users\\Jjr_a\\PycharmProjects\\book_read_barcode\\dataset_livros.csv')

obj = book_bardcode()

# Crie uma barra lateral com opções
op = st.sidebar.selectbox("Escolha uma opção:",
                          ["Cadastrar livro", "Consultar livro", "Reservar livro", "Devolver livro"])

if op == "Cadastrar livro":
    st.header("Registrar Livro")

    isbn = st.text_input('Digite o ISBN do livro: ')

    if len(isbn) > 1 and len(isbn) <= 13:
        titulo, capa_url = obj.buscar_titulo_e_capa_por_isbn(isbn)
        st.write(titulo)
        if titulo:
            # Exibe os detalhes do livro antes de confirmar o cadastro
            if capa_url:
                image_bytes = requests.get(capa_url).content
                st.image(BytesIO(image_bytes), caption="Capa do Livro", use_column_width=True)
            st.write(f"ISBN: {isbn}")

            if st.button("Cadastrar"):
                obj.registrar_livro(isbn, titulo, capa_url)
                st.success("Livro cadastrado com sucesso!")
        else:
            st.write('ISBN inválido. Tente novamente!')
    else:
        st.write('ISBN inválido. Tente novamente!')
elif op == 'Consultar livro':
    dataset = pd.read_csv('C:\\Users\\Jjr_a\\PycharmProjects\\book_read_barcode\\dataset_livros.csv')
    dataset['ISBN'] = dataset['ISBN'].astype(str)
    isbn = st.text_input('Digite o ISBN do livro: ')

    check_isbn = dataset.loc[dataset['ISBN'] == isbn]
    if len(check_isbn) > 0:
        info_livro = dataset.loc[dataset['ISBN'] == isbn]
        st.subheader(info_livro['TITULO'].values[0])

        # Carregar a imagem como bytes e exibi-la
        if info_livro['CAPA'].values[0]:
            image_bytes = requests.get(info_livro['CAPA'].values[0]).content
            st.image(BytesIO(image_bytes), caption="Capa do Livro", width=200)

    else:
        print('Livro não encontrado. Por favor, verifique o ISBN digitado ou cadastre o livro.')

    st.write()
    gallery_placeholder = st.empty()

    images_list, captions_list = [], []
    for i in dataset['ISBN'].drop_duplicates():
        images_list.append(dataset.loc[dataset['ISBN'] == i, 'CAPA'].values[0])
        captions_list.append(dataset.loc[dataset['ISBN'] == i, 'TITULO'].values[0])

    with gallery_placeholder.container():
        img = image_select(
            label="Selecione um livro",
            images=images_list,
            captions=captions_list,
            use_container_width=True)

    # if not dataset.empty:
    #     st.write("Catálogo de Livros")
    #
    #     # Configuração das colunas
    #     col1, col2, col3, col4 = st.columns(4)
    #
    #     # Loop pelos livros no catálogo
    #     for _, row in dataset.iterrows():
    #         with col1:
    #             st.markdown(f"<h3 style='font-size: 10px'>{row['TITULO']}</h3>", unsafe_allow_html=True)
    #
    #             # Carregar a imagem como bytes e exibi-la
    #             if row['CAPA']:
    #                 image_bytes = requests.get(row['CAPA']).content
    #                 st.image(BytesIO(image_bytes), use_column_width=True)
    #
    #             st.write(f"ISBN: {str(row['ISBN'])}")
    #
    #         col1, col2, col3, col4 = col2, col3, col4, col1  # Alternar entre colunas para exibição horizontal
