#include "query_functions.h"

// Funzione per codificare URL
String urlEncode(String str) {
  String encodedString = "";
  char c;
  char code0;
  char code1;
  char code2;
  for (int i = 0; i < str.length(); i++) {
    c = str.charAt(i);
    if (c == ' ') {
      encodedString += '+';
    } else if (isalnum(c)) {
      encodedString += c;
    } else {
      code1 = (c & 0xf) + '0';
      if ((c & 0xf) > 9) {
        code1 = (c & 0xf) - 10 + 'A';
      }
      c = (c >> 4) & 0xf;
      code0 = c + '0';
      if (c > 9) {
        code0 = c - 10 + 'A';
      }
      code2 = '\0';
      encodedString += '%';
      encodedString += code0;
      encodedString += code1;
    }
    yield();
  }
  return encodedString;
}

////////// QUERY REQUEST

JsonDocument send_query(String sqlQuery) {
  String serverName = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT);
  
  JsonDocument doc;

  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;

    // Configura l'URL del server
    http.begin(serverName);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    // Query SQL da inviare
    String httpPost = "query=" + urlEncode(sqlQuery);

    // Invia la richiesta POST
    int httpResponseCode = http.POST(httpPost);
    
    if (httpResponseCode > 0) {
      String response = http.getString();

      // Parsing del JSON
      DeserializationError error = deserializeJson(doc, response);

      // Controlla se ci sono errori nella parsificazione
      if (error) {
        printToTerminal("Errore nella parsificazione JSON: " + String(error.f_str()));
        sqlError = true;
      } else {
        // Check for an error in the JSON response
        if (doc.containsKey("error")) {
          printToTerminal("Errore nel risultato SQL: " + String(doc["error"].as<String>()));
          sqlError = true;
        } else {
          sqlError = false;
        }
      }

      return doc;
    } else {
      printToTerminal("Errore nella richiesta POST: " + String(httpResponseCode));
      sqlError = true;
      return doc;
    }

    // Chiudi la connessione
    http.end();
  } else {
    printToTerminal("Connessione Persa");
    sqlError = true;
    return doc;
  }
}


//// FUNCTIONS TO SEND QUERY

// Funzione per la verifica dell'autenticazione tramite il DB
JsonDocument autUID(String uid) {
  JsonDocument user = send_query("SELECT Nome, Cognome FROM Utenti WHERE CodiceChiavetta = '" + uid + "'; ");

  if (!sqlError) {
    if (user.size() == 0) {
      String nome = "";
      String cognome = "";
      if (TERMINALE) {
        Serial.println("Creazione nuovo Utente...");
        lcdWrite("Creazione", "nuovo Utente...");

        // Leggi il nome
        Serial.print("\nInserisci il nome del nuovo utente: ");
        while (true) {
          if (Serial.available()) {
            char c = Serial.read();
            if (c == '\n') break;
            if (c != '\r' && isAlpha(c) && nome.length() < 50) nome += c;  // Ignora '\r' e aggiungi solo lettere fino ad un massimo di 50 caratteri
          }
        }

        // Leggi il cognome
        Serial.print("\nInserisci il cognome del nuovo utente: ");
        while (true) {
          if (Serial.available()) {
            char c = Serial.read();
            if (c == '\n') break;
            if (c != '\r' && isAlpha(c) && nome.length() < 50) cognome += c;  // Ignora '\r' e aggiungi solo lettere fino ad un massimo di 50 caratteri
          }
        }

      } else {
        nome = "nome";
        cognome = "cognome";
      }
      send_query("INSERT INTO Utenti (CodiceChiavetta, Nome, Cognome) VALUES ('" + uid + "', '" + nome + "', '" + cognome + "'); ");
      user = send_query("SELECT Nome, Cognome FROM Utenti WHERE CodiceChiavetta = '" + uid + "'; ");

      return user; 
    } else {
      return user;
    }
  } else {
    return user;
  }
}

//// X Distributore
// Funzione per ottenere i Prodotti nel distributore
void getProducts() {
  JsonDocument products_json = send_query("SELECT Slot AS Slot, NomeProdotto AS NomeProdotto, CAST(Prezzo AS FLOAT) AS Prezzo, Quantita AS Quantita FROM ContenutoDistributore WHERE NomeProdotto != 'Vuoto'; ");
  
  resetProducts();  

  // Converte il documento JSON in un array JSON
  JsonArray lista_prodotti = products_json.as<JsonArray>();
  
  // Contatore delle Transazioni
  int prodottiCount = 0;
  // Itera attraverso gli elementi dell'array principale
  for (JsonVariant subArray : lista_prodotti) {
    // Assicurati che ogni elemento sia un array di 3 elementi
    if (subArray.is<JsonArray>() && subArray.size() == 4) {
      JsonArray innerArray = subArray.as<JsonArray>();

      int slot = innerArray[0];
      String nome_prodotto = innerArray[1];
      float prezzo = innerArray[2];
      int quantita = innerArray[3];

      // Salva i valori nella struttura Transazioni
      products[prodottiCount].slot = slot;
      products[prodottiCount].nomeProdotto = nome_prodotto;
      products[prodottiCount].prezzo = prezzo;
      products[prodottiCount].quantita = quantita;
      prodottiCount++;
    } else {
      printToTerminal("Errore nella Parsificazione del JSON");
    }
  }
}

float getSaldo(String codice_chiavetta) {
  JsonDocument saldo_JSON = send_query("SELECT CAST(Saldo AS FLOAT) AS Saldo FROM Utenti WHERE CodiceChiavetta = '" + String(codice_chiavetta) + "'; ");

  if (!sqlError) {
    float saldo = saldo_JSON[0][0];
    return saldo;
  } else {
    return 0,00;
  }
}

void updateSaldo(float new_saldo, String codice_chiavetta) {
  // Aggiornamento saldo
  send_query("UPDATE Utenti SET Saldo = " + String(new_saldo) + " WHERE CodiceChiavetta = '" + String(codice_chiavetta) + "'; ");
}

void ricaricaSaldo(float new_saldo, String codice_chiavetta, float importo) {
  // Aggiornamento del Saldo
  updateSaldo(new_saldo, codice_chiavetta);

  // Aggiornamento Tabella Transazioni
  send_query("INSERT INTO Transazioni (CodiceChiavetta, TipoTransazione, Importo) VALUES ('" + codice_chiavetta + "', 'Ricarica', " + importo + "); ");

}

void updateDB(String codice_chiavetta, float saldo, Product product, int quantita_selezionata) {
  // Definizione e calcolo delle varibili
  int slot = product.slot;
  String nome_prodotto = product.nomeProdotto;
  float prezzo = product.prezzo;
  float importo = prezzo * quantita_selezionata;
  float new_saldo = saldo - importo;

  // Aggiornamento del Saldo
  updateSaldo(new_saldo, codice_chiavetta);

  // Aggiornamento Totale Acquisti effettuati
  send_query("UPDATE Utenti SET NumeroAcquisti = NumeroAcquisti + 1, TotaleAcquisti = TotaleAcquisti + " + String(importo) + " WHERE CodiceChiavetta = '" + String(codice_chiavetta) + "'; ");

  // Aggiornamento Tabella Prodotti
  send_query("UPDATE Prodotti SET QuantitaDisponibile = QuantitaDisponibile - " + String(quantita_selezionata) + ", QuantitaVenduta = QuantitaVenduta + " + String(quantita_selezionata) + " WHERE NomeProdotto = '" + String(nome_prodotto) + "'; ");

  // Aggiornamento Tabella Transazioni
  send_query("INSERT INTO Transazioni (CodiceChiavetta, TipoTransazione, Importo, Quantita) VALUES ('" + String(codice_chiavetta) + "', 'Acquisto', " + String(importo) + ", " + String(quantita_selezionata) + "); ");

//DA VERIFICARE
  JsonDocument id_transazione_JSON = send_query("SELECT MAX(IDTransazione) FROM Transazioni; ");
  int id_transazione = id_transazione_JSON[0][0];
  // Aggiornamento Tabella DettagliTrnasazione
  send_query("INSERT INTO DettagliTransazione (IDTransazione, NomeProdotto) VALUES ('" + String(id_transazione) + "', '" + String(nome_prodotto) + "'); ");

  // Aggiornamento Quantita in ContenutoDistributore e imposta Erogazione = TRUE
  send_query("UPDATE ContenutoDistributore SET Erogazione = TRUE, Quantita = Quantita - " + String(quantita_selezionata) + " WHERE Slot = " + String(slot) + "; ");
}

void resetErogazione(int slot) {
  send_query("UPDATE ContenutoDistributore SET Erogazione = FALSE WHERE Slot = " + String(slot) + "; ");
}

void getTransazioni(String codice_Chiavetta, String tipologia_transazione) {
  JsonDocument transazioni_json = send_query("SELECT IDTransazione AS IDTransazione, CAST(Importo AS FLOAT) AS Importo, Quantita AS Quantita FROM Transazioni WHERE CodiceChiavetta = '" + codice_Chiavetta + "' AND TipoTransazione = '" + tipologia_transazione + "' ORDER BY IDTransazione DESC LIMIT " + LIMITE_TRANSAZIONI + ";");
  
  resetTransazioni();  

  // Converte il documento JSON in un array JSON
  JsonArray lista_transazioni = transazioni_json.as<JsonArray>();
  
  // Contatore delle Transazioni
  int transazioneCount = 0;
  // Itera attraverso gli elementi dell'array principale
  for (JsonVariant subArray : lista_transazioni) {
    // Assicurati che ogni elemento sia un array di 3 elementi
    if (subArray.is<JsonArray>() && subArray.size() == 3) {
      JsonArray innerArray = subArray.as<JsonArray>();

      int id = innerArray[0];
      float importo = innerArray[1];
      int quantita = innerArray[2];

      // Salva i valori nella struttura Transazioni
      transazioni[transazioneCount].id_transazione = id;
      transazioni[transazioneCount].importo = importo;
      transazioni[transazioneCount].quantita = quantita;
      transazioneCount++;
    } else {
      printToTerminal("Errore nella Parsificazione del JSON");
    }
  }
}

int checkProduct(String nome_prodotto) {
  JsonDocument slot_JSON = send_query("SELECT Slot FROM ContenutoDistributore WHERE NomeProdotto = '" + String(nome_prodotto) + "'; ");

  if (!sqlError) {
    if (slot_JSON.size() == 0) {
      return -1;
    } else {
      int slot = slot_JSON[0][0];
      return slot;
    }
  }

  return 0;
}

String getNomeProdotto(int id_transazione) {
  JsonDocument nome_prodotto_JSON = send_query("SELECT p.NomeProdotto FROM DettagliTransazione AS d JOIN Prodotti AS p ON d.NomeProdotto = p.NomeProdotto WHERE d.IDTransazione = " + String(id_transazione) + "; ");

  // Controlla se la lista dei risultati non è vuota. In caso lo sia imposta il nomeProdotto su None
  if (!sqlError) {
    String nome_prodotto = nome_prodotto_JSON[0][0];
    return nome_prodotto;
  }

  return "";
}
