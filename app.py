from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pandas as pd
import random
import pandasql as psql

app = Flask(__name__)

# Lista para armazenar os registros
data = []

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

# Verificar a contagem por dia
print(df['modifiedDate'].str[:10].value_counts())

@app.route('/')
def home():
    return jsonify({
        'mensagem': 'API online com sucesso!',
        'status': 'ok'
    })

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
    FROM df
    WHERE {where_param}
    ORDER BY {sort_param}
    LIMIT {limit} OFFSET {offset}
    """

    result_df = psql.sqldf(query, globals())

    return jsonify({
        "count": len(result_df) if where_param != '1=1' else len(df),
        "limit": limit,
        "offset": offset,
        "records": result_df.to_dict(orient='records')
    })

if __name__ == '__main__':
    app.run(debug=True)
