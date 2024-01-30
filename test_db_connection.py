#! /usr/bin/python3
import db
import sys
import logging

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Expected table name as argument")
        sys.exit(1)

    # Configurar o logging para imprimir mensagens de depuração
    logging.basicConfig(level=logging.DEBUG)

    # Conectar ao banco de dados
    logging.debug("Connecting to the database...")
    db.connect()

    # Nome da tabela fornecido como argumento de linha de comando
    table_name = sys.argv[1]

    logging.debug("Executing SQL query for table %s..." % table_name)

    # Executar a consulta SQL
    data = db.execute('SELECT * FROM ' + table_name).fetchall()

    # Imprimir resultados
    logging.info("%d results ..." % len(data))
    for d in data:
        logging.debug([ (c,d[c]) for c in d.keys()])

    # Fechar a conexão com o banco de dados
    logging.debug("Closing the database connection...")
    db.close()