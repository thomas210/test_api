from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'mensagem': 'API online com sucesso!',
        'status': 'ok'
    })

if __name__ == '__main__':
    app.run()
