import socket
import mysql.connector
import json

client_host = 'localhost' # 127.0.0.1
client_port = 4080

####################################################### Database

# Funzione per eseguire la query inviata dal client
def query_execute(query):

    # Connessione al database MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="Distributore"
    )
    
    # Cursor per eseguire le query
    cursor = conn.cursor()

    # Esegui la query
    cursor.execute(query)
    # Ottieni i dati della Query solo se si tratta di una Richiesta
    try:
        risposta = cursor.fetchall()
    except:
        risposta = None
    
    # Chiudi la connessione al DB
    conn.commit()
    conn.close()

    # Ripsosta della query
    return risposta

####################################################### SERVER

# Funzione per avviare il server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((client_host, client_port))
    server_socket.listen(1) # Limite utenti collegati contemporaneamente (Distributore)
    print("Server in ascolto su {}:{}".format(client_host, client_port))

    while True:
        client_socket, client_address = server_socket.accept()
        print("\n\nConnessione accettata da:", client_address)

        try:
            # Decodifica il messaggio ricevuto 
            query_request = client_socket.recv(1024).decode()
            print ("Richiesta:", query_request)
            # Dai una risposta alla richiesta
            risposta = query_execute(query_request)
        except Exception as e:
            print("Errore durante l'elaborazione della richiesta:", str(e))
            risposta = "Error"

        # Stampa di debug
        print("\nRisposta:", risposta)

        # Invia i dati al client
        client_socket.sendall(json.dumps(risposta).encode('utf-8'))
        client_socket.close()

if __name__ == "__main__":
    start_server()