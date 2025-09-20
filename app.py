from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pandas as pd
import random
import pandasql as psql
import psycopg2
import os

app = Flask(__name__)

# Lê a URL de conexão do ambiente (docker-compose.yml)
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Cria uma conexão com o banco de dados."""
    return psycopg2.connect(DATABASE_URL)

def create_table():
    """Cria a tabela de dados se ela não existir."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dados_api (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            value INT,
            modifiedDate TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Chama a função para criar a tabela ao iniciar a aplicação
# Isso garante que a tabela existe antes de qualquer operação
with app.app_context():
    create_table()

# Rota para popular o banco de dados
# checar no docker: docker compose exec db psql -U user mydatabase
# \dt
@app.route('/seed', methods=['GET'])
def seed_database():

    # Lista para armazenar os registros
    data = []

    """Gera dados e insere no banco de dados."""
    try:
        
        # --- 1.000 registros para 14/08/2025 ---
        # Escolhe um dia aleatório entre 10 e 14
        day = random.randint(10, 14)
        base_date_random = datetime(2025, 8, day)
        for i in range(1000):
            record = {
                "id": i + 1,
                "name": f"Registro-{i+1}",
                "modifiedDate": (base_date_random + timedelta(seconds=random.randint(0, 86399))).strftime("%Y-%m-%d %H:%M:%S"),
                "value": random.randint(1, 1000)
            }
            data.append(record)

        # --- 3000 registros para 15/08/2025 ---
        base_date_15 = datetime(2025, 8, 15)
        for i in range(600, 3600):
            record = {
                "id": i + 1,
                "name": f"Registro-{i+1}",
                "modifiedDate": (base_date_15 + timedelta(seconds=random.randint(0, 86399))).strftime("%Y-%m-%d %H:%M:%S"),
                "value": random.randint(1, 1000)
            }
            data.append(record)

        # Cria o DataFrame
        df = pd.DataFrame(data)

        conn = get_db_connection()
        cur = conn.cursor()

        # Insere os dados do DataFrame no banco de dados
        for index, row in df.iterrows():
            cur.execute(
                "INSERT INTO dados_api (name, value, modifiedDate) VALUES (%s, %s, %s)",
                (row['name'], row['value'], row['modifiedDate'])
            )
        
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Banco de dados populado com sucesso!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# # Rota para consultar os dados (exemplo)
# @app.route('/data', methods=['GET'])
# def get_data():
#     """Consulta e retorna os dados do banco de dados."""
#     try:
#         conn = get_db_connection()
#         cur = conn.cursor()
#         cur.execute("SELECT * FROM dados_api;")
#         data = cur.fetchall()
#         cur.close()
#         conn.close()
        
#         # Converte o resultado para um formato JSON
#         columns = ['id', 'nome', 'valor', 'data_hora']
#         result = [dict(zip(columns, row)) for row in data]
        
#         return jsonify(result), 200
    
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
    
# Rota para consultar os dados (exemplo)
@app.route('/api/records', methods=['GET'])
def get_records():
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    sort_param = request.args.get('sort', 'id asc')
    where_param = request.args.get('where', '1=1')  # default sem filtro

    # Valida parâmetros
    if limit < 1 or limit > 100:
        return jsonify({"error": "limit deve estar entre 1 e 100"}), 400
    if offset < 0 or offset > 1000:
        return jsonify({"error": "offset deve estar entre 0 e 1000"}), 400
    
    print("############################################################")

    # Monta query SQL sobre o DataFrame
    query = f"""
    SELECT * 
    FROM dados_api
    WHERE {where_param}
    ORDER BY {sort_param}
    LIMIT {limit} OFFSET {offset}
    """

    """Consulta e retorna os dados do banco de dados."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query)
        data = cur.fetchall()
        cur.close()
        conn.close()
        
        # Converte o resultado para um formato JSON
        columns = ['id', 'name', 'value', 'modifiedDate']
        result_df = [dict(zip(columns, row)) for row in data]

        return jsonify({
            "count": len(result_df),
            "limit": limit,
            "offset": offset,
            "records": result_df#.to_dict(orient='records')
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({
        'mensagem': 'API online com sucesso!',
        'status': 'ok'
    })