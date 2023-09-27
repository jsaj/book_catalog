
# import mysql.connector as mysql
import pandas as pd
import psycopg2
# Configurações de conexão


class conexao_banco():
    def conectar_banco(self):
        # Defina as informações de conexão
        # host = "sql10.freesqldatabase.com"
        # database = "sql10649389"
        # user = "sql10649389"
        # password = "J6UTmuFcCR"
        # port = 3306
        #
        #     # Conecte-se ao banco de dados
        # connection = mysql.connect(
        #     host=host,
        #     database=database,
        #     user=user,
        #     password=password,
        #     port=port)


        # Defina a string de conexão com o banco de dados PostgreSQL
        CONNSTR = f'postgresql://j.jr.avelino:FNOwP1MzaZ8h@ep-black-credit-89791997.us-west-2.aws.neon.tech/neondb'

        # Conecte-se ao banco de dados PostgreSQL usando psycopg2
        connection = psycopg2.connect(CONNSTR)

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


