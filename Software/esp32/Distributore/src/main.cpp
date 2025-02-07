#include "distributore.h"

////////// SETUP
void setup() {
  // Inizializzazione Pins
  pinMode(PIN_MENO, INPUT_PULLUP);
  pinMode(PIN_PIU, INPUT_PULLUP);
  pinMode(PIN_RETURN, INPUT_PULLUP);
  pinMode(PIN_CONFIRM, INPUT_PULLUP);

  pinMode(IN_ISO_1, INPUT);
  pinMode(IN_ISO_2, INPUT);

  pinMode(PIN_LED_RGB_R, OUTPUT);
  pinMode(PIN_LED_RGB_G, OUTPUT);
  pinMode(PIN_LED_RGB_B, OUTPUT);

  pinMode(RELE, OUTPUT);

  // Inizializzazione LCD
  Wire.begin(I2C_SDA, I2C_SCL);
  lcd.init();
  lcd.clear();
  lcd.backlight();

  // Inizializzazione RFID
  SPI.begin(SCK, MISO, MOSI);
  rfid.PCD_Init();

  // Stampo lo stato del Terminale
  if (TERMINALE) {
    Serial.begin(SERIAL_SPEED);
    printToTerminal("\nTerminale di Debug Attivato");
  } else {
    printToTerminal("\nTerminale di Debug Disattivato");
  }

  // Avvio Distributore
  printToTerminal("\nAvvio di Esp32");
  lcdWrite(" Configurazione ", "     ESP32      ");
  
  // Test dei LED
  digitalWrite(PIN_LED_RGB_R, HIGH);
  delay(500);
  digitalWrite(PIN_LED_RGB_R, LOW);
  digitalWrite(PIN_LED_RGB_G, HIGH);
  delay(500);
  digitalWrite(PIN_LED_RGB_G, LOW);
  digitalWrite(PIN_LED_RGB_B, HIGH);
  delay(500);
  digitalWrite(PIN_LED_RGB_B, LOW);

  // Connessione WiFi
  printToTerminal("\nSelezione del Wi-Fi tramite: " + String(ESP32_AP_NAME));
  wifiConnector.begin();
  
  printToTerminal("\n####CONFIG END####");
}

////////// DISTRIBUTORE
void loop() {
  // Verifica cambio dello Stato
  if (next_state != current_state) {
    // bEntry per gestione cambio stato
    state_change = true;
    // Verifica che sia possibile effettuare il cambio di stato
    current_state = next_state;
  } else {
    state_change = false;
  }

  // Reset OUTPUTS
  // Leds
  LED_RGB_R = false;
  LED_RGB_G = false;
  LED_RGB_B = false;
  // Relè
  OUT_RELE = false;

  // Lettura INPUT
  // Lettura e aggiornamento dello stato del pulsante PIU
  bool current_PIU = !digitalRead(PIN_PIU);
  if (PIU_old == true && current_PIU == false) {
    PIU = true;
    delay(10); // Debounce
  } else {
    PIU = false;
  }
  PIU_old = current_PIU;

  // Lettura e aggiornamento dello stato del pulsante MENO
  bool current_MENO = !digitalRead(PIN_MENO);
  if (MENO_old == true && current_MENO == false) {
    MENO = true;
    delay(10); // Debounce
  } else {
    MENO = false;
  }
  MENO_old = current_MENO;

  // Lettura e aggiornamento dello stato del pulsante RETURN
  bool current_RETURN = !digitalRead(PIN_RETURN);
  if (RETURN_old == true && current_RETURN == false) {
    RETURN = true;
    delay(10); // Debounce
  } else {
    RETURN = false;
  }
  RETURN_old = current_RETURN;

  // Lettura e aggiornamento dello stato del pulsante CONFIRM
  bool current_CONFIRM = !digitalRead(PIN_CONFIRM);
  if (CONFIRM_old == true && current_CONFIRM == false) {
    CONFIRM = true;
    delay(10); // Debounce
  } else {
    CONFIRM = false;
  }
  CONFIRM_old = current_CONFIRM;

  switch (current_state) {
    case ATTESA_CHIAVETTA:
      if (state_change) {
        printToTerminal("\nStato: ATTESA_CHIAVETTA");
        ID_Chiavetta = "";
        dot_count = 0;
        clear_dots = false;

        // Leggo la temperatura dal Sensore
        LM35 = analogRead(LM35_SENSOR);
        float temperature = (LM35 * 3300.0 / 4096.0) / 10.0;

        // Imposto il Timer di sistema
        intervalMillis = millis();

        // Stampo la temperatura
        lcdWrite("Attesa Chiavetta", "Temp: " + String(temperature) + "'C");

        // Stampo la temperatura nella seriale
        printToTerminal("Temperatura: " + String(temperature) + "°C");
      }
      
      if (millis() - intervalMillis >= SENSOR_INTERVAL) { // Verifica se è passato il tempo necessario
        intervalMillis = millis(); // Aggiorna il tempo dell'ultima operazione

        // Leggo la temperatura dal Sensore
        LM35 = analogRead(LM35_SENSOR);
        float temperature = (LM35 * 3300.0 / 4096.0) / 10.0;
        lcdWrite("Attesa Chiavetta", "Temp: " + String(temperature) + "'C");

        // Stampo la temperatura nella seriale
        printToTerminal("Temperatura: " + String(temperature) + "°C");
      }

      // Verifica la presenza di una Chiavetta
      ID_Chiavetta = getUID();
      
      // Uscita
      if (ID_Chiavetta != "") {
          printToTerminal ("Chiavetta inserita: " + ID_Chiavetta);
          next_state = AUTENTICAZIONE_CHIAVETTA;
      }

      // Alleggerisce il carico in uno stato di inattività
      delay(100);
      break;
    case AUTENTICAZIONE_CHIAVETTA:
      if (state_change) {
        printToTerminal("\nStato: AUTENTICAZIONE_CHIAVETTA");
        lcdWrite(" Autenticazione ", "   Chiavetta!   ");
      }
      
      user = autUID(ID_Chiavetta);

      if (!sqlError) {
        String nome = user[0][0];
        String cognome = user[0][1];
        printToTerminal("Autenticazione avvenuta con successo");
        printToTerminal ("Utente: " + nome + " " + cognome);
        // Ottenimento del Saldo
        float saldo = getSaldo(ID_Chiavetta);

        if (!sqlError) {
          printToTerminal ("Saldo:" + String(saldo));
          // Scorrimento Menù
          selected_option = 0;
          // Scorrimento Prodotti
          next_state = MENU;
          lcdWrite("  Benvenuto/a   ", nome + " " + cognome, 2000);
        }
      }
      break;
    case MENU:
      if (state_change) {
        printToTerminal("\nStato: MENU");
      }

      // Funzione
      if (PIU) {
        if (selected_option < (sizeof(menu_options) / sizeof(menu_options[0])) - 1) {
          selected_option = selected_option + 1;
        }
      }
      if (MENO) {
        if (selected_option > 0) {
          selected_option = selected_option - 1;
        }
      }

      // Aggiornamento OUTPUT
      LED_RGB_R = true;
      LED_RGB_G = true;

      if (PIU || MENO || state_change) {
          lcdWrite("Scegli Modalita:", String(menu_options[selected_option]));
          printToTerminal("Menu:" + String(menu_options[selected_option]));
      }

      // Uscita
      if (RETURN) {
        next_state = RESET;
      }
      if (CONFIRM) {
        if (menu_options[selected_option] == "Distributore") {
          selected_product = DEFAULT_PRODUCT;
          next_state = RICHIESTA_PRODOTTI;
        }
        if (menu_options[selected_option] == "Saldo") {
          delta_saldo = 0;
          next_state = RICHIESTA_SALDO;
        }
        if (menu_options[selected_option] == "Transazioni") {
          selected_type = 0;
          next_state = MENU_TRANSAZIONI;
        }
      }
      break;
    // Continua per tutti gli altri stati
    case RICHIESTA_PRODOTTI:
      if (state_change) {
        printToTerminal("\nStato: RICHIESTA_PRODOTTI");
      }

      // Funzione
      getProducts();
      saldo = getSaldo(ID_Chiavetta);

      if (!sqlError) {
        // Stampa Prodotti
        printProductList();

        // Uscita
        next_state = SELEZIONE_PRODOTTO;
      }
      break;
    case SELEZIONE_PRODOTTO:
      if (state_change) {
        printToTerminal("\nStato: SELEZIONE_PRODOTTO");
      }

      // Funzione
      if (PIU) {
        if (selected_product < (sizeof(products) / sizeof(products[0])) - 1) {
          selected_product += 1;
        }
      }

      if (MENO) {
        if (selected_product > 0) {
          selected_product -= 1;
        }
      }

      // Aggiornamento OUTPUT
      // Terminale
      if (state_change) {
        lcdWrite("Saldo rimanente:", "    " + String(saldo) + "EUR", 2000);
        printToTerminal("Saldo: " + String(saldo));
      }
      if (PIU || MENO || state_change) {
        // Scrivi la stringa sullLCD
        String lcd_line2;
        if (products[selected_product].quantita) {
          if (products[selected_product].quantita == 10) {
            lcd_line2 = "Q:" + String(products[selected_product].quantita) + " |" + String(products[selected_product].slot) + "| P:" + String(products[selected_product].prezzo);
          } else {
            lcd_line2 = "Q:" + String(products[selected_product].quantita) + " |" + String(products[selected_product].slot) + "| P:" + String(products[selected_product].prezzo);
          }
        } else {
          lcd_line2 = "Empty |" + String(products[selected_product].slot) + "| P:" + String(products[selected_product].prezzo);
        }
        lcdWrite(String(products[selected_product].nomeProdotto), lcd_line2);
        printToTerminal("\nSlot:" + String(products[selected_product].slot));
        printToTerminal("Prodotto:" + String(products[selected_product].nomeProdotto));
        printToTerminal("Prezzo:" + String(products[selected_product].prezzo));
        if (products[selected_product].quantita == 0) {
          printToTerminal("Quantita: Esaurito");
        } else {
          printToTerminal("Quantita:" + String(products[selected_product].quantita));
        }
      }

      // Warning Esaurito
      if (products[selected_product].quantita == 0) {
        LED_RGB_R = true;
      } else {
        LED_RGB_G = true;
      }

      if (RETURN) {
        // Ripristino prodotto selezionato di default
        next_state = MENU;
      }
      if (CONFIRM) {
          // Inizializza la variablie per lo Scorrimento della quantità del Prodotto
          selected_quantity = QUANTITA_MINIMA;
          next_state = SELEZIONE_QUANTITA;
      }
      break;
    case SELEZIONE_QUANTITA:
      if (state_change) {
        printToTerminal("\nStato: SELEZIONE_QUANTITA");
        if (products[selected_product].quantita == 0) {
          next_state = SELEZIONE_PRODOTTO;
          lcdWrite("    Prodotto    ", "    Esaurito    ", 1500);
          printToTerminal("Prodotto Selezionato Esaurito");
        } else if (saldo <= products[selected_product].prezzo) {
          next_state = SELEZIONE_PRODOTTO;
          lcdWrite("     Saldo      ", " Insufficente!  ", 1500);
          printToTerminal("Saldo Insufficente");
        } else {
          lcdWrite("  Seleziona la  ", "quantita: " + String(selected_quantity) + "/" + String(products[selected_product].quantita));
          printToTerminal("Quantita Selezionata:" + String(selected_quantity));
        }
      }

      // Funzione
      if (PIU) {
        if (selected_quantity < products[selected_product].quantita) {
            selected_quantity += 1;
        }
      }
      if (MENO) {
        if (selected_quantity > QUANTITA_MINIMA) {
          selected_quantity -= 1;
        }
      }

      // Aggiornamento OUTPUT
      LED_RGB_R = true;
      LED_RGB_B = true;
      if (PIU || MENO) {
        // Scrivi la stringa sull'LCD
        lcdWrite("  Seleziona la  ", "quantita: " + String(selected_quantity) + "/" + String(products[selected_product].quantita));
        printToTerminal("Quantita Selezionata:" + String(selected_quantity));
      }

      // Uscita
      if (RETURN) {
        next_state = SELEZIONE_PRODOTTO;
      }
      if (CONFIRM) {
        next_state = CHECK_PRODOTTO;
      }
      break;
    case CHECK_PRODOTTO:
      if (state_change) {
        printToTerminal("\nStato: CHECK_PRODOTTO");
      }

      // Funzione e Uscita
      if (saldo >= (products[selected_product].prezzo * selected_quantity)) {
        printToTerminal("Prodotto acquistato");
        next_state = EROGAZIONE;
        // Aggiornamento dell'acquisto nel DB
        updateDB(ID_Chiavetta, saldo, products[selected_product], selected_quantity);
      } else {
        printToTerminal("Saldo insufficente");
        lcdWrite("     Saldo      ", "  Insufficente  ", 1500);
        next_state = SELEZIONE_PRODOTTO;
      }
      break;
    case EROGAZIONE:
      if (state_change) {
        printToTerminal("\nStato: EROGAZIONE");
        lcdWrite("IN EROGAZIONE...");
        printToTerminal("In Erogazione");
        intervalMillis = millis();
        endMillis = millis();
      }

      LED_RGB_B = true;
      OUT_RELE = true;

      // Funzione
      // Tempo di attesa per l'erogazione del Prodotto
      if (millis() - intervalMillis >= INTERVAL_EROG) { // Verifica se è passato il tempo necessario
        intervalMillis = millis(); // Aggiorna il tempo dell'ultima operazione

        if (printEqualSigns) { // Stampa "=" per totalColumns - 1 volte
          if (currentColumn < totalColumns - 1) {
              lcd.setCursor(currentColumn, 1);
              lcd.print("=");
              currentColumn++;
          } else { // Dopo aver stampato tutte le "="
              printEqualSigns = false; // Imposta il flag a false per passare alla stampa di ">"
          }
        } else { // Stampa ">"
          lcd.setCursor(totalColumns - 1, 1);
          lcd.print(">");
          printEqualSigns = true; // Imposta il flag a true per tornare alla stampa di "="
          currentColumn = 0; // Reimposta la colonna corrente a 0
        }
      }

      // Uscita
      if (millis() - endMillis >= TIMER_EROGAZIONE) {
        lcdWrite("Erog. Completata", "===============>", 200);
        next_state = RICHIESTA_PRODOTTI;
      }
      break;
    case RICHIESTA_SALDO:
      if (state_change) {
        printToTerminal("\nStato: RICHIESTA_SALDO");
      }

      // Funzione
      saldo = getSaldo(ID_Chiavetta);

      // Uscita
      next_state = MODIFICA_SALDO;
      break;
    case MODIFICA_SALDO:
      if (state_change) {
        printToTerminal("\nStato: MODIFICA_SALDO");
        printToTerminal("Saldo attuale:" + String(saldo));
      }
      
      // Funzione   
      if (PIU) {
        delta_saldo += 0.5;
      }
      if (MENO) {
        if (saldo + delta_saldo - 0.5 > 0) {
          delta_saldo -= 0.5;
        } else {
          delta_saldo = 0 - saldo;
          lcd_error = true;
        }
      }
      new_saldo = saldo + delta_saldo;

      // Aggiornamento OUTPUT
      LED_RGB_B = true;
      LED_RGB_G = true;

      if (PIU || MENO || state_change) {
        // Scrivi la stringa sullLCD
        String lcd_line2;
        if (delta_saldo > 0) {
          lcd_line2 = "Metti: (+" + String(delta_saldo) + ")";
        } else if (delta_saldo < 0) {
          lcd_line2 = "Togli: (" + String(delta_saldo) + ")";
        } else {
          lcd_line2 = "";
        } 
        if (lcd_error) {
          lcd_line2 = "Azzera Saldo";
          lcd_error = false;
        }
        lcdWrite(("Saldo: " + String((saldo * 100) / 100.0) + "EUR"), lcd_line2);
        printToTerminal("Nuovo Saldo:" + String((new_saldo * 100) / 100.0));
      }

      // Uscita
      if (RETURN) {
        next_state = MENU;
      }
      if (CONFIRM) {
        if (delta_saldo != 0 && new_saldo >= 0) {
          next_state = AGGIORNA_SALDO;
        } else {
          printToTerminal("Impossibile aggiornare il Saldo");
        }
      }

      break;
    case AGGIORNA_SALDO:
      if (state_change) {
        printToTerminal("\nStato: AGGIORNA_SALDO");
      }
      
      // Funzione e Uscita
      ricaricaSaldo(new_saldo, ID_Chiavetta, delta_saldo);
      printToTerminal("Saldo aggiornato");
      delta_saldo = 0;
      next_state = RICHIESTA_SALDO;
      break;
    case MENU_TRANSAZIONI:
      if (state_change) {
        printToTerminal("\nStato: MENU_TRANSAZIONI");
      }

      // Funzione
      if (PIU) {
        if (selected_type < (sizeof(menu_Transazioni_options) / sizeof(menu_Transazioni_options[0])) - 1) {
          selected_type = selected_type + 1;
        }
      }
      if (MENO) {
        if (selected_type > 0) {
          selected_type = selected_type - 1;
        }
      }

      // Aggiornamento OUTPUT
      LED_RGB_R = true;

      if (PIU || MENO || state_change) {
        lcdWrite("  Transazioni:  ", "    " + String(menu_Transazioni_options[selected_type]));
        printToTerminal("Tipologia Transazione: " + String(menu_Transazioni_options[selected_type]));
      }

      // Uscita
      if (RETURN) {
        next_state = MENU;
      }
      if (CONFIRM) {
        if (menu_Transazioni_options[selected_type] == "Acquisti") {
          next_state = RICHIESTA_ACQUISTI;
        }
        if (menu_Transazioni_options[selected_type] == "Ricariche") {
          next_state = RICHIESTA_RICARICHE;
        }
      }
      break;
    case RICHIESTA_ACQUISTI:
      if (state_change) {
        printToTerminal("\nStato: RICHIESTA_ACQUISTI");
      }
      
      // Funzione
      getTransazioni(ID_Chiavetta, "Acquisto");
  
      if (!sqlError) {
        // Verifica la Presenza di Transazioni
        if (transazioni[0].id_transazione == -1) {
          printToTerminal("Nessun Acquisto effettuato");
          lcdWrite("     Nessun     ", "    Acquisto    ", 1500);
          next_state = MENU_TRANSAZIONI;
        } else {
          // Uscita
          selected_transazione = 0;
          next_state = MOSTRA_ACQUISTI;
        }
      }
      break;
    case MOSTRA_ACQUISTI:
      if (state_change) {
        printToTerminal("\nStato: MOSTRA_ACQUISTI");
      }
      
      // Aggiornamento OUTPUT
      LED_RGB_R = true;

      // Funzione
      if (PIU) {
        if ((selected_transazione < (sizeof(transazioni) / sizeof(transazioni[0])) - 1) && (transazioni[selected_transazione + 1].id_transazione != -1)) {
          selected_transazione += 1;
        }
      }
      if (MENO) {
        if ((selected_transazione > 0) && (transazioni[selected_transazione - 1].id_transazione != -1)) {
          selected_transazione -= 1;
        }
      }
      
      if (PIU || MENO || state_change) {
        nome_prodotto = getNomeProdotto(transazioni[selected_transazione].id_transazione);
        if (!sqlError) {
          int id_transazione = transazioni[selected_transazione].id_transazione;
          float importo_transazione = transazioni[selected_transazione].importo;
          int quantita_transazione = transazioni[selected_transazione].quantita;
          printToTerminal("ID: " + String(transazioni[selected_transazione].id_transazione));
          printToTerminal("Nome Prodotto: " + nome_prodotto);
          printToTerminal("Importo: " + String(transazioni[selected_transazione].importo));
          printToTerminal("Quantita: " + String(transazioni[selected_transazione].quantita));
          lcdWrite((String(selected_transazione + 1) + "| " + String(nome_prodotto)), "Q: " + String(quantita_transazione) + " |A| I: " + String(importo_transazione));
        }
      }

      // Uscita
      if (RETURN) {
        next_state = MENU_TRANSAZIONI;
      }
      if (CONFIRM) {
        next_state = VERIFICA_PRODOTTO;
      }
      break;
    case VERIFICA_PRODOTTO:
      if (state_change) {
        printToTerminal("\nStato: VERIFICA_PRODOTTO");
        slot = checkProduct(nome_prodotto);
      }   

      // Funzione ed uscita
      if (!sqlError) {
        if (slot != -1) {
          printToTerminal("Slot: " + String(slot));

          // Calcola il selected_product sapendo lo Slot
          getProducts();

          if (!sqlError) {
            int count = 0;  // Inizializza il contatore a 0
            for (const auto& product : products) {
              if (product.slot <= slot && product.nomeProdotto != "Vuoto") {
                count++;
              }
            }
            selected_product = count - 1;
            next_state = RICHIESTA_PRODOTTI;
          }
        } else {
          lcdWrite("  Prodotto non  ", "piu disponibile ", 1500);
          printToTerminal("Il Prodotto richiesto non è piu disponibile nel distributore");
          next_state = MOSTRA_ACQUISTI;
        }
      }
      break;
    case RICHIESTA_RICARICHE:
      if (state_change) {
        printToTerminal("\nStato: RICHIESTA_RICARICHE");
      }
      
      // Funzione
      getTransazioni(ID_Chiavetta, "Ricarica");

      // Verifica la Presenza di Transazioni
      if (!sqlError) {
        // Verifica la Presenza di Transazioni
        if (transazioni[0].id_transazione == -1) {
          printToTerminal("Nessuna Ricarica effettuata");
          lcdWrite("     Nessuna    ", "    Ricarica    ", 1500);
          next_state = MENU_TRANSAZIONI;
        } else {
          // Uscita
          selected_transazione = 0;
          next_state = MOSTRA_RICARICHE;
        }
      }
      break;
    case MOSTRA_RICARICHE:
      if (state_change) {
        printToTerminal("\nStato: MOSTRA_RICARICHE");
      }

      // Aggiornamento OUTPUT
      LED_RGB_R = true;

      // Funzione
      if (PIU) {
        if ((selected_transazione < (sizeof(transazioni) / sizeof(transazioni[0])) - 1) && (transazioni[selected_transazione + 1].id_transazione != -1)) {
          selected_transazione += 1;
        }
      }

      if (MENO) {
        if (selected_transazione > 0 && (transazioni[selected_transazione - 1].id_transazione != -1)) {
          selected_transazione -= 1;
        }
      }

      if (PIU || MENO || state_change) {
        int id_transazione = transazioni[selected_transazione].id_transazione;
        importo_transazione = transazioni[selected_transazione].importo;
        printToTerminal("ID: " + String(id_transazione));
        printToTerminal("Importo: " + String(importo_transazione));
        lcdWrite("Ricarica N." + String(id_transazione), ("|R| I: " + String(importo_transazione) + "EUR"));
      }

      // Uscita
      if (RETURN) {
        next_state = MENU_TRANSAZIONI;
      }

      if (CONFIRM) {
        next_state = RIPETI_RICARICA;
      }
      break;
    case RIPETI_RICARICA:
      if (state_change) {
        printToTerminal("\nStato: RIPETI_RICARICA");
      }

      // Funzione ed uscita
      if (saldo + importo_transazione >= 0) {
        delta_saldo = importo_transazione;
        next_state = RICHIESTA_SALDO;
      } else {
        printToTerminal("Richiesta non Valida");
        lcdWrite("   Richiesta    ", "   non valida   ", 1500);
        next_state = MOSTRA_RICARICHE;
      }
      
      break;
    case ERROR:
      if (state_change) {
        printToTerminal("\nStato: ERROR");
        lcdWrite("#Error on Query#", "  Riavvio MAS   ", 500);
      }

      // Funzione
      printToTerminal("Errore generico nel DB");
      wifiConnector.checkConnection();

      // Uscita
      sqlError = false;
      next_state = RESET;

      break;
    case RESET:
      if (state_change) {
        printToTerminal("\nStato: RESET");
      }
      
      // Funzione
      if (state_change) {
        lcdWrite("    Grazie e    ", " Arrivederci... ", 1000);
      }
      ID_Chiavetta = "";
      saldo = 0;

      // Aggiornamento OUTPUT
      printToTerminal("MAS RESTARTATA");

      // Uscita
      next_state = ATTESA_CHIAVETTA;

      break;
    default:
      // Errore nella macchina a stati
      printToTerminal("ERRORE NEL CAMBIO STATO");

      next_state = RESET;
      break;
  }

  // Gestisco errori nell'invio della query
  if (sqlError) {
    next_state = ERROR;
  }

  // Configuro gli OUTPUT
  digitalWrite(PIN_LED_RGB_R, LED_RGB_R);
  digitalWrite(PIN_LED_RGB_G, LED_RGB_G);
  digitalWrite(PIN_LED_RGB_B, LED_RGB_B);
  digitalWrite(RELE, OUT_RELE);
}