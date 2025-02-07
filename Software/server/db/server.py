from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Funzione per eseguire la query inviata dal client
def query_execute(query):
    try:
        # Connessione al database MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="webuser",
            passwd="pwd",
            database="Distributore"
        )
        
        # Cursor per eseguire le query
        cursor = conn.cursor()

        # Esegui la query
        cursor.execute(query)
        # Ottieni i dati della Query solo se si tratta di una Richiesta
        try:
            risposta = cursor.fetchall()
        except mysql.connector.Error as err:
            return {"error": str(err)}
        
        # Chiudi la connessione al DB
        conn.commit()
        conn.close()

        # Risposta della query
        return risposta
    except mysql.connector.Error as err:
        return {"error": str(err)}

@app.route('/', methods=['POST'])
def handle_post():
    try:
        # Leggi il corpo della richiesta
        query_request = request.form.get('query')
        if not query_request:
            return jsonify({"error": "Parametro 'query' non trovato nel corpo della richiesta"}), 400
        
        print("Richiesta di query:", query_request)
        
        # Dai una risposta alla richiesta
        risposta = query_execute(query_request)
        return jsonify(risposta)
    except Exception as e:
        print("Errore durante l'elaborazione della richiesta:", str(e))
        return jsonify({"error": "Errore durante l'elaborazione della richiesta"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
