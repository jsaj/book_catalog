
import mysql.connector as mysql
import pandas as pd

# Configurações de conexão


class conexao_mysql():

    # def conectar_banco(self):
    #     # Configurações de conexão
    #     host = 'aws.connect.psdb.cloud'
    #     user = 'glijhrkku43houa3oewn'
    #     password = 'pscale_pw_k5HpOePAQkXH0XNiUNBLnDqaVTlS2jvfdKd62S61zMc'
    #     database = 'streamlit-study-db'
    #
    #     # Tente estabelecer a conexão
    #     conexao = mysql.connect(
    #         host=host,
    #         user=user,
    #         password=password,
    #         database=database
    #     )
    #
    #     return conexao
    def conectar_banco(self):
        # Defina as informações de conexão
        host = "sql10.freesqldatabase.com"
        database = "sql10649389"
        user = "sql10649389"
        password = "J6UTmuFcCR"
        port = 3306

            # Conecte-se ao banco de dados
        connection = mysql.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port)

        return connection
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


