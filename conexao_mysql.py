
import mysql.connector as mysql
import pandas as pd

# Configurações de conexão


class conexao_mysql():

    def __init__(self):
        self.conexao = self.conectar_banco()

    def conectar_banco(self):
        # Configurações de conexão
        host = 'aws.connect.psdb.cloud'
        user = 'wwbc4k1zv19ro5q0apub'
        password = 'pscale_pw_rfQ7Kl5nlC2n5zY8pWghHvtlQHAK2RY2QGRApFwWprF'
        database = 'streamlit-study-db'

        try:
            # Tente estabelecer a conexão
            conexao = mysql.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )

            if conexao.is_connected():
                print("Conexão bem-sucedida ao MySQL!")

        except mysql.Error as e:
            print(f"Erro de conexão ao MySQL: {e}")
        return conexao

    def insert_data(self, connection, tabela, colunas, valores):

        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO {tabela} {colunas} VALUES {valores}")

        connection.commit()
    def update_data(self,
                    connection,
                    tabela,
                    coluna_alterar,
                    coluna_condicao,
                    valor_alterar,
                    valor_condicao):

        cursor = connection.cursor()

        cursor.execute(
            f"UPDATE {tabela} SET {coluna_alterar} = {valor_alterar}  WHERE {coluna_condicao} = {valor_condicao}")

        connection.commit()

    def drop_data(self,
                  connection,
                  tabela,
                  colunas,
                  valores):

        cursor = connection.cursor()

        # Crie uma lista de condições usando list comprehension
        condicoes = [f"{col} = '{val}'" for col, val in zip(colunas, valores)]

        # Use o método join para criar a parte da cláusula WHERE
        condicoes_str = " AND ".join(condicoes)

        # Construa a consulta DELETE completa
        query = f"DELETE FROM {tabela} WHERE {condicoes_str}"

        cursor.execute(query)

        connection.commit()

    def read_data(self, conexao, tabela):

        query = f'SELECT * FROM {tabela}'
        dataset = pd.read_sql(query, conexao)
        return dataset


