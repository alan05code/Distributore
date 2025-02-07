import socket
import json

import pyfirmata2
import serial
from threading import Timer

import time
import keyboard

####################################################### Terminale

# Terminale ON/OFF (Disabilita la possibilità di visualizzare su terminale gli avvenimenti del distributore)
TERMINALE = True

#### Stili print Terminale
# Definisci uno stile predefinito per il testo
STYLE_DEFAULT = "\033[0m"
STYLE_BOLD = "\033[1m"
STYLE_ITALIC = "\033[3m"
# Funzione per formattare il testo in grassetto
def bold(text):
    return STYLE_BOLD + str(text) + STYLE_DEFAULT
# Funzione per formattare il testo in corsivo
def italic(text):
    return STYLE_ITALIC + str(text) + STYLE_DEFAULT
# Funzione per stampare un messaggio con parte in grassetto e parte in corsivo
def printFormatted(first_text, second_text=""):
    if TERMINALE:
        formatted_text = bold(first_text) + " " + italic(second_text)
        print(formatted_text)

####################################################### CONFIGURAZIONE

#### TEST IN VITA
# TIV ON/OFF
TIV = True
# Pin LED del Test in Vita
PIN_TIV = 13

# Config Simulazione per utilizzo solo PC (avvio automatico in assenza di aduini collegati)
SIMULAZIONE = False

#### BOARD
# PORTA
#PORT_IN_OUT = 'COM5'
PORT_IN_OUT = '/dev/cu.usbmodem141401'
#PORT_RFID_LCD = 'COM6'
PORT_RFID_LCD = '/dev/cu.usbmodem141101'

# Input da tastiera
BUTTON_PIU = "+"
BUTTON_MENO = "-"
BUTTON_CANCEL = "ò"
BUTTON_CONFIRM = "ù"

# Connessio con RFID e LCD
SERIAL_ARDUINO = True

#### Protocolli di comunicazione con ARDUINO_RFID_LCD
# Start
RFID_START_REQUEST = "<START>"
RFID_START_RESPONCE = "<STARTED>"

# RFID
# uid
RFID_UID = "<uid>"

# LCD
# Definizione Richieste LCD
LCD_PRINT = "<lp>"
LCD_CHANGE_LINE = "@"

# Richiamo a Funzioni specifiche
ATTESA_CHIAVETTA = "<attesa>"
LCD_EROGAZIONE = "<erogazione>"

#### Tentativo di Connessione
if not SIMULAZIONE:
    try: 
        # Crea una board
        board_IN_OUT = pyfirmata2.Arduino(PORT_IN_OUT)
        printFormatted("Connessione con Arduino ...")
        # default sampling interval of 19ms
        board_IN_OUT.samplingOn()
        try:
            # Instanza l'oggetto della seriale
            board_RFID_LCD = serial.Serial(port=PORT_RFID_LCD , baudrate=115200, timeout=.1)
        except Exception as e:
            printFormatted("Errore durante la connessione alla Seriale. RFID e LCD non disponibili")
            SERIAL_ARDUINO = False
    except Exception as e:
        printFormatted("Errore durante la connessione all'Arduino")
        printFormatted("Modalità di simulazione attivata. Arduino non connesso.")
        # Configurazione della modalita SIMULAZIONE {False -> Arduino | True -> Tastiera}
        SIMULAZIONE = True
        TERMINALE = True
        SERIAL_ARDUINO = False
else:
    SERIAL_ARDUINO = False

# Configurazione PIN Arduino
# PULSANTI
MENO = 2
PIU = 3
CANCEL = 4
CONFIRM = 5

# LED
# SLOT
LED_BIT_0 = 6
LED_BIT_1 = 7
LED_BIT_2 = 8
LED_BIT_3 = 9
# RGB
LED_RGB_R = 10
LED_RGB_G = 12
LED_RGB_B = 11

# Intervallo del Lampeggio dei LED
INTERVAL = 0.5

# Numero limite delle transazioni visualizzate
LIMITE_TRANSAZIONI = 10

# Slot del Prodotto selezionato di Default
DEFAULT_PRODUCT = 0
# Quantita del Prodotto Default
QUANTITA_MINIMA = 1

nomi_pulsanti = ["MENO", "PIU", "CANCEL", "CONFIRM"]
# Lista Pulsanti
lista_pulsanti = [MENO, PIU, CANCEL, CONFIRM]
# Lista dei pulsanti inizialiazzata con tutti False
pulsanti = {nome_pulsante: False for nome_pulsante in nomi_pulsanti}
# Lista per ultimo stato di ciascun pulsante
last_state_pulsanti = {nome_pulsante: False for nome_pulsante in nomi_pulsanti}

####################################################### Simulazione

#### INPUT
# Funzione per gestire gli eventi della tastiera
def onKeyPress(event):
    global button
    button = event.name
if SIMULAZIONE:
    # Evento di pressione di un tasto
    keyboard.on_press(onKeyPress)
    # Variabile per memorizzare il tasto premuto
    button = None

####################################################### SERVER

server_host = 'localhost' # 127.0.0.1
server_port = 4080
### Richiesta
# Funzione per connettersi al server e ricevere i dati
error = False
def serverRequest(query):
    global server_host, server_port, error
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    # Invio della richiesta al server
    client_socket.sendall(query.encode())
    # Ricevi i dati dal server
    received_data = client_socket.recv(4096).decode('utf-8')
    # Decodifica i dati JSON ricevuti
    risposta = json.loads(received_data)

    client_socket.close()

    if risposta == 'Error':
        error = True

    return risposta

####################################################### Arduino

#### INPUT
# Puslanti
if not SIMULAZIONE:
    # Funzione di Callback dei pulsanti
    def pinCallback(data, index):
        pulsanti[nomi_pulsanti[index]] = not data
    # Configura i Pulsanti e associa la funzione di Callback
    board_addr_pulsanti = {}
    for index, pin in enumerate(lista_pulsanti):
        # Setup the digital pin with pullup resistor: "u"
        board_addr_pulsanti[nomi_pulsanti[index]] = board_IN_OUT.get_pin('d:{}:u'.format(pin))
        # Points to the callback with the index as an additional argument
        board_addr_pulsanti[nomi_pulsanti[index]].register_callback(lambda data, index=index: pinCallback(data, index))
        # Switches the callback on
        board_addr_pulsanti[nomi_pulsanti[index]].enable_reporting()

    #### OUTPUT
    # Led
    nomi_led_slot = ["Slot_Bit0", "Slot_Bit1", "Slot_Bit2", "Slot_Bit3"]
    nomi_led_RGB = ["RGB_Red", "RGB_Green", "RGB_Blue"]
    nomi_led = nomi_led_slot + nomi_led_RGB
    # Lista Led
    lista_led_slot = [LED_BIT_0, LED_BIT_1, LED_BIT_2, LED_BIT_3]
    lista_led_RGB = [LED_RGB_R, LED_RGB_G, LED_RGB_B]
    lista_led = lista_led_slot + lista_led_RGB
    # Stato dei leds
    leds = {nome_led: False for nome_led in nomi_led}
    # Configura i Led come Output
    board_addr_led = {}
    for index, pin in enumerate(lista_led):
        board_addr_led[nomi_led[index]] = board_IN_OUT.get_pin('d:{}:o'.format(pin))
    # Funzione per aggiornare lo stato dei LED
    def updateLed(led_name, led_state):
        board_addr_led[led_name].write(led_state)

    # Definisce la classe con la funzione per il lampeggio dei LED
    class Blink():
        def __init__(self, durata):
            # Imposta e setta il Delay
            self.timer = {}
            self.DELAY = durata
        # Callback che cambia lo stato del LED e riavvia il timer
        def blinkCallback(self, led_name):
            # Richiama se stessa per eseguirsi periodicamente
            self.timer[led_name] = Timer(self.DELAY, self.blinkCallback, args=[led_name])
            # Avvia il timer
            self.timer[led_name].start()
            # Cambia lo stato del LED
            led_state = board_addr_led[led_name].read()
            led_state = not led_state
            board_addr_led[led_name].write(led_state)
        # Inizia il lampeggio
        def start(self, led_name):
            # Avvia la funzione di callback
            self.blinkCallback(led_name)
        # Ferma il lampeggio
        def stop(self, led_name):
            # Cancella il timer
            try:
                self.timer[led_name].cancel()
                board_addr_led[led_name].write(0)
            except:
                printFormatted("Tentativo Fallito di Spegnimento del Lampeggio del Led")

#### X LCD
# Scrivi la stringa sulla porta seriale
# ljust => stringa di 16 caratteri esatti
def lcdWrite(linea1, linea2 = "", time_delay = 1):
    if SERIAL_ARDUINO:
        request = LCD_PRINT + str(linea1).ljust(16) + LCD_CHANGE_LINE + str(linea2).ljust(16)
        # Invia il pacchetto
        board_RFID_LCD.write(request.encode())
        # Attendi il completamento dell'invio
        board_RFID_LCD.flush()
        time.sleep(time_delay)
                
#### X RFID
if SERIAL_ARDUINO:
    # Verifica che l'RFID sia connesso
    def RFIDBegin():
        # Invia la Richiesta
        board_RFID_LCD.write(RFID_START_REQUEST.encode())
        time.sleep(1)
        # Attendi il completamento dell'invio
        board_RFID_LCD.flush()
        if board_RFID_LCD.in_waiting > 0:
            # Leggi il dato dalla porta seriale
            if board_RFID_LCD.readline().decode().strip() == RFID_START_RESPONCE:
                return True
            else:
                return False
        else:
            return False

# Funzione per svuotare la seriale
def resetSerial():
    if SERIAL_ARDUINO:    
        while board_RFID_LCD.in_waiting > 0:
            # Leggi il dato dalla porta seriale
            board_RFID_LCD.readline().decode().strip()  # Decodifica i byte in stringa e rimuove i caratteri di newline
# Funzione per verificare la presenza della chiavetta
def checkUID():
    if SERIAL_ARDUINO:
        # Verifica presenza di dato in seriale
        if board_RFID_LCD.in_waiting > 0:
            # Leggi il dato dalla porta seriale
            received = board_RFID_LCD.readline().decode().strip()  # Decodifica i byte in stringa e rimuove i caratteri di newline
            if RFID_UID in received:
                # Rimuovo RFID_UID da uid
                uid = received.replace(RFID_UID, "")
                return uid
            else:
                return False
        else:
            return False
    else:
        uid = input("Inserire numero chiavetta:")
        return uid
# Funzione per la verifica dell'autenticazione tramite il DB
def autUID(uid):
    user = serverRequest("""SELECT Nome, Cognome
                            FROM Utenti
                            WHERE CodiceChiavetta = '{}'; """.format(uid))
    if user:
        return user
    else:
        lcdWrite("Creazione", "nuovo Utente...")
        nome = input("Nome: ")
        cognome = input("Cognome: ")
        serverRequest("""INSERT INTO Utenti (CodiceChiavetta, Nome, Cognome)
                         VALUES ('{}', '{}', '{}'); """.format(uid, nome, cognome))
        user = serverRequest("""SELECT Nome, Cognome
                            FROM Utenti
                            WHERE CodiceChiavetta = '{}'; """.format(uid))
    return user

####################################################### X MAS

#### Dichiarazione Stati
# Stati della macchina a stati
STATES = {
    "AttesaChiavetta": ["AutenticazioneChiavetta"],
    "AutenticazioneChiavetta": ["Menu", "AttesaChiavetta", "Error"],

    "Menu": ["RichiestaProdotti", "RichiestaSaldo", "MenuTransazioni", "Reset"],

    "RichiestaProdotti": ["SelezioneProdotto", "Error"],
    "SelezioneProdotto": ["SelezioneQuantita", "Menu"],
    "SelezioneQuantita": ["CheckProdotto", "SelezioneProdotto"],
    "CheckProdotto": ["Erogazione", "SelezioneProdotto", "Error"],
    "Erogazione": ["RichiestaProdotti", "Error"],

    "RichiestaSaldo": ["ModificaSaldo", "Error"],
    "ModificaSaldo": ["AggiornaSaldo", "Menu"],
    "AggiornaSaldo": ["RichiestaSaldo", "Error"],

# Da implementare
    "MenuTransazioni": ["Menu", "RichiestaAcquisti", "RichiestaRicariche"],
    "RichiestaAcquisti": ["MostraAcquisti", "MenuTransazioni", "Error"],
    "MostraAcquisti": ["MenuTransazioni", "VerificaProdotto"],
    "VerificaProdotto": ["RichiestaProdotti", "MostraAcquisti", "Error"],
    "RichiestaRicariche": ["MostraRicariche", "MenuTransazioni", "Error"],
    "MostraRicariche": ["MenuTransazioni", "RipetiRicarica"],
    "RipetiRicarica": ["RichiestaSaldo", "MostraRicariche", "Error"],

    "Error": ["Reset"],
    "Reset": ["AttesaChiavetta"]
}
current_state = "Reset"


#### X Distributore
# Funzione per ottenere i Prodotti nel distributore
def getProducts():
    product_list = serverRequest("""SELECT Slot AS Slot, NomeProdotto AS NomeProdotto, CAST(Prezzo AS FLOAT) AS Prezzo, Quantita AS Quantita 
                                    FROM ContenutoDistributore
                                    WHERE NomeProdotto != 'Vuoto'; """)

    products = []
    for row in product_list:
        product = {
            "Slot": row[0],
            "NomeProdotto": row[1],
            "Prezzo": float(row[2]),  # Assicurati che il prezzo sia un float
            "Quantita": row[3]
        }
        products.append(product)

    return products
# Funzione per stampare la lista dei Prodotti
def printProductList(products_list):
    if TERMINALE:
        print("{:<10} {:<50} {:<10} {:<10}".format("Slot", "Nome Prodotto", "Prezzo", "Quantità"))
        for prodotto in products_list:
            print("{:<10} {:<50} {:<10} {:<10}".format(prodotto["Slot"], prodotto["NomeProdotto"], prodotto["Prezzo"], prodotto["Quantita"]))

#### X Saldo
# Funzione per ottenere il Saldo dell'Utente
def getSaldo(codice_chiavetta):
    saldo = serverRequest("""SELECT CAST(Saldo AS FLOAT) AS Saldo 
                             FROM Utenti 
                             WHERE CodiceChiavetta = '{}'; """.format(codice_chiavetta))
    return saldo[0][0]
# Funzione per aggiornare il Saldo dell'Utente
def updateSaldo(new_saldo, codice_chiavetta):
    # Aggiornamento saldo
    serverRequest("""UPDATE Utenti
                    SET Saldo = {}
                    WHERE CodiceChiavetta = '{}'; """.format(new_saldo, codice_chiavetta))
# Funzione per effettuare ricarica del Saldo
def ricaricaSaldo(new_saldo, codice_chiavetta, importo):
    # Aggiornamento del Saldo
    updateSaldo(new_saldo, codice_chiavetta)

    # Aggiornamento Tabella Transazioni
    serverRequest("""INSERT INTO Transazioni (CodiceChiavetta, TipoTransazione, Importo)
                        VALUES ('{}', 'Ricarica', {}); """.format(codice_chiavetta, importo))

#### X Prodotti
# Funzione per acquistare un Prodotto
def updateDB(codice_chiavetta, saldo, product, quantita_selezionata): 
    # Definizione e calcolo delle varibili
    slot = product['Slot']
    nome_prodotto = product['NomeProdotto']
    prezzo = product['Prezzo']
    importo = prezzo * quantita_selezionata
    new_saldo = saldo - importo

    # Aggiornamento del Saldo
    updateSaldo(new_saldo, codice_chiavetta)

    
    # Aggiornamento Totale Acquisti effettuati
    serverRequest("""UPDATE Utenti
                    SET NumeroAcquisti = NumeroAcquisti + 1,
                        TotaleAcquisti = TotaleAcquisti + {}
                    WHERE CodiceChiavetta = '{}'; """.format(importo, codice_chiavetta))
    
    # Aggiornamento Tabella Prodotti
    serverRequest("""UPDATE Prodotti
                    SET QuantitaDisponibile = QuantitaDisponibile - {},
                        QuantitaVenduta = QuantitaVenduta + {}
                    WHERE NomeProdotto = '{}'; """.format(quantita_selezionata, quantita_selezionata, codice_chiavetta))

    # Aggiornamento Tabella Transazioni
    serverRequest("""INSERT INTO Transazioni (CodiceChiavetta, TipoTransazione, Importo, Quantita)
                    VALUES ('{}', 'Acquisto', {}, {}); """.format(codice_chiavetta, importo, quantita_selezionata))

    id_transazione = serverRequest("""SELECT MAX(IDTransazione) FROM Transazioni; """)
    id_transazione = id_transazione[0][0]
    # Aggiornamento Tabella DettagliTrnasazione
    serverRequest("""INSERT INTO DettagliTransazione (IDTransazione, NomeProdotto)
                    VALUES ('{}', '{}'); """.format(id_transazione, nome_prodotto))

    # Aggiornamento Quantita in ContenutoDistributore e imposta Erogazione = TRUE
    serverRequest("""UPDATE ContenutoDistributore
                    SET Erogazione = TRUE,
                        Quantita = Quantita - {}
                    WHERE Slot = {}; """.format(quantita_selezionata, slot))  
        
def resetErogazione(slot):
    serverRequest("""UPDATE ContenutoDistributore
                    SET Erogazione = TRUE
                    WHERE Slot = {}; """.format(slot))

#### X Transazioni
# Funzione per ottenere le ultime 10 Transazioni del tipo specificato
def getTransazioni(codice_Chiavetta, tipologia_transazione):
    lista_transazioni = serverRequest("""SELECT IDTransazione AS IDTransazione, CAST(Importo AS FLOAT) AS Importo, Quantita AS Quantita
                            FROM Transazioni 
                            WHERE CodiceChiavetta = '{}' AND TipoTransazione = '{}'
                            ORDER BY IDTransazione DESC
                            LIMIT {}; """.format(codice_Chiavetta, tipologia_transazione, LIMITE_TRANSAZIONI))

    transazioni = []
    for row in lista_transazioni:
        transazione = {
            "IDTransazione": row[0],
            "Importo": float(row[1]),
            "Quantita": row[2],
        }
        transazioni.append(transazione)

    return transazioni

# Funzione per verificare la presenza di uno specifico Prodotto nel Distribuotre
def checkProduct(nome_prodotto):
    return serverRequest("""SELECT Slot
                            FROM ContenutoDistributore
                            WHERE NomeProdotto = '{}'; """.format(nome_prodotto))

def getNomeProdotto(id_transazione):
    nome_prodotto = serverRequest("""SELECT p.NomeProdotto
                                     FROM DettagliTransazione AS d
                                     JOIN Prodotti AS p ON d.NomeProdotto = p.NomeProdotto
                                     WHERE d.IDTransazione = {}; """.format(id_transazione))
    
    # Controlla se la lista dei risultati non è vuota. In caso lo sia imposta il nomeProdotto su None
    if nome_prodotto:
        return nome_prodotto[0][0]
    else:
        return None


####################################################### Test in Vita

if TIV and not SIMULAZIONE:
    # Configura i Led come Output
    board_addr_led[PIN_TIV] = board_IN_OUT.get_pin('d:{}:o'.format(PIN_TIV))
    tiv = False
    # Funzione test in vita: alterna lo stato del pin PIN_TIV ogni volta che viene chiamata

    def test_in_vita():
        global tiv
        tiv = not tiv
        updateLed(PIN_TIV, tiv)

####################################################### MAS

# Funzione per la macchina a stati
def stateMachine():
    global error
    global button
    global current_state
    global pulsanti
    global last_state_pulsanti
    next_state = "AttesaChiavetta"

    # Opzioni del Menu
    menu_options = ["Distributore", "Saldo", "Transazioni"]
    menu_Transazioni_options = ["Acquisti", "Ricariche"]

    # Prodotto selezionato di Default
    selected_product = DEFAULT_PRODUCT

    if not SIMULAZIONE:
        lampeggio = Blink(INTERVAL)

        for i , led_name in enumerate(leds):
            updateLed(led_name, True)
            if i < len(lista_led_slot):
                time.sleep(0.5)

        time.sleep(0.250)

    RFID_LCD_Connected = False
    if SERIAL_ARDUINO:
        printFormatted("Attendo Connessione con ARDUINO_RFID_LCD")
        while RFID_LCD_Connected == 0:
            RFID_LCD_Connected = RFIDBegin()
        printFormatted("Connessione con ARDUINO_RFID_LCD Effettuata")

    while True:
        # Verifica cambio dello Stato
        if next_state != current_state:
            # Verifica che sia possibile effettuare il cambio di stato
            if next_state in STATES[current_state]:
                current_state = next_state
                printFormatted ("\nStato:", current_state)
                # bEntry per gestione cambio stato
                state_change = True
            else:
                print ("Stato richiesto non assegnabile")
                current_state = "Reset"
        else:
            state_change = False

        # Reset LED
        if not SIMULAZIONE:
            # Array per salvare ogni bit
            slot_leds = [0] * len(nomi_led_slot) # Inizializzazione a False

            # Resetto i Led
            leds["RGB_Red"] = False
            leds["RGB_Green"] = False
            leds["RGB_Blue"] = False
            for i in range(len(slot_leds)):
                leds[nomi_led[i]] = slot_leds[i]

        # Gestione INPUT
        if SIMULAZIONE:
            if button == BUTTON_PIU:
                PIU = True
            else:
                PIU = False
            if button == BUTTON_MENO:
                MENO = True
            else:
                MENO = False
            if button == BUTTON_CANCEL:
                CANCEL = True
            else:
                CANCEL = False
            if button == BUTTON_CONFIRM:
                CONFIRM = True
            else:
                CONFIRM = False
            button = None
        else:
            # Fronti di Discesa
            if pulsanti['PIU'] == False and last_state_pulsanti['PIU'] == True:
                PIU = True
            else:
                PIU = False
            if pulsanti['MENO'] == False and last_state_pulsanti['MENO'] == True:
                MENO = True
            else:
                MENO = False
            if pulsanti['CANCEL'] == False and last_state_pulsanti['CANCEL'] == True:
                CANCEL = True
            else:
                CANCEL = False
            if pulsanti['CONFIRM'] == False and last_state_pulsanti['CONFIRM'] == True:
                CONFIRM = True
            else:
                CONFIRM = False

#### Macchina a Stati
################################ Attesa

        if current_state == "AttesaChiavetta":
            # Svuota la Seriale
            if not SIMULAZIONE:
                if state_change:
                    resetSerial()
                    ID_Chiavetta = ''

            # Alleggerisce il carico in uno stato di inattività
            time.sleep(0.5)

            # Aggiornamento OUTPUT
            if state_change:
                lcdWrite("Attesa Chiavetta".center(16), ATTESA_CHIAVETTA)
                printFormatted ("Attesa Chiavetta...")

            # Funzione e Uscita
            # Verifica la presenza e salva la Chiavetta (uid ricevuto)
            ID_Chiavetta = checkUID()
            if ID_Chiavetta:
                printFormatted ("Chiavetta inserita:", ID_Chiavetta)
                next_state = "AutenticazioneChiavetta"
            
        elif (current_state == "AutenticazioneChiavetta"):
            # Funzione e Uscita
            # Verifico la Chiavetta
            user = autUID(ID_Chiavetta)

            nome = user[0][0]
            cognome = user[0][1]
            printFormatted("Autenticazione avvenuta con successo")
            if TERMINALE:
                print(bold("Utente:"), italic(nome), italic(cognome))
            # Ottenimento del Saldo
            saldo = getSaldo(ID_Chiavetta)

            printFormatted ("Saldo:", saldo)
            # Scorrimento Menù
            selected_option = 0
            # Scorrimento Prodotti
            next_state = "Menu"
            lcdWrite("Benvenuto".center(16), str(nome + " " + cognome).center(16), 2)

################################ Menu
            
        elif (current_state == "Menu"):
            # Funzione
            if PIU:
                if selected_option < len(menu_options) - 1:
                    selected_option = selected_option + 1
            if MENO:
                if selected_option > 0:
                    selected_option = selected_option - 1
            
            # Aggiornamento OUTPUT
            if not SIMULAZIONE:
                leds["RGB_Red"] = True
                leds["RGB_Green"] = True

            if PIU or MENO or state_change:
                lcdWrite("Scegli Modalita:".center(16), str(menu_options[selected_option]).center(16))
                printFormatted("Menu:", menu_options[selected_option])

            # Uscita
            if CANCEL:
                next_state = "Reset"
            if CONFIRM:
                if menu_options[selected_option] == "Distributore":
                    selected_product = DEFAULT_PRODUCT
                    next_state = "RichiestaProdotti"
                if menu_options[selected_option] == "Saldo":
                    delta_saldo = 0
                    next_state = "RichiestaSaldo"
                if menu_options[selected_option] == "Transazioni":
                    selected_type = 0
                    next_state = "MenuTransazioni"
            
################################ Distributore

        elif (current_state == "RichiestaProdotti"):
            # Funzione
            products = getProducts()
            saldo = getSaldo(ID_Chiavetta)
            
            printProductList(products)

            # Uscita
            next_state = "SelezioneProdotto"
            
        elif (current_state == "SelezioneProdotto"):
            # Funzione
            if PIU:
                if selected_product < len(products) - 1:
                    selected_product += 1

            if MENO:
                if selected_product > 0:
                    selected_product -= 1

            # Aggiornamento OUTPUT
            # Terminale
            if state_change:
                lcdWrite("Saldo rimanente:", (str(saldo) + "EUR").center(16), 2)
                printFormatted("Saldo: ", saldo)
            if PIU or MENO or state_change:
                if SERIAL_ARDUINO:
                    # Scrivi la stringa sullLCD
                    if products[selected_product]["Quantita"]:
                        if products[selected_product]["Quantita"] == 10:
                            lcd_line2 = "Q:{}  |{}| P:{:.2f}".format(products[selected_product]["Quantita"], products[selected_product]["Slot"], products[selected_product]["Prezzo"])
                        else:
                            lcd_line2 = "Q:{}   |{}| P:{:.2f}".format(products[selected_product]["Quantita"], products[selected_product]["Slot"], products[selected_product]["Prezzo"])
                    else:
                        lcd_line2 = "Empty |{}| P:{:.2f}".format(products[selected_product]["Slot"], products[selected_product]["Prezzo"])
                    lcdWrite(str(products[selected_product]["NomeProdotto"]).center(16), lcd_line2)
                printFormatted("\nSlot:", products[selected_product]["Slot"])
                printFormatted("Prodotto:", products[selected_product]["NomeProdotto"])
                printFormatted("Prezzo:", products[selected_product]["Prezzo"])
                if products[selected_product]["Quantita"] == 0:
                    printFormatted("Quantita:", "Esaurito")
                else:
                    printFormatted("Quantita:", products[selected_product]["Quantita"])

            if not SIMULAZIONE:
                # Conversione in binario
                bin_leds = bin(selected_product + 1)[2:]  # Rimuovi il prefisso '0b'
                # Riempimento dell'array con i bit
                lunghezza_binario = len(bin_leds)
                for i in range(lunghezza_binario):
                    slot_leds[len(nomi_led_slot) - 1 - i] = int(bin_leds[lunghezza_binario - 1 - i])
                # Aggiorno le variabili dei LED
                for i in range(len(slot_leds)):
                    leds[nomi_led[i]] = slot_leds[i]

                # Warning Esaurito
                if products[selected_product]["Quantita"] == 0:
                    leds["RGB_Red"] = True
                else:
                    leds["RGB_Green"] = True

            if CANCEL:
                # Ripristino prodotto selezionato di default
                next_state = "Menu"
            if CONFIRM:
                # Inizializza la variablie per lo Scorrimento della quantità del Prodotto
                selected_quantity = QUANTITA_MINIMA
                next_state = "SelezioneQuantita"
        
        elif (current_state == "SelezioneQuantita"):
            # Funzione
            if PIU:
                if selected_quantity < products[selected_product]["Quantita"]:
                    selected_quantity += 1
            if MENO:
                if selected_quantity > QUANTITA_MINIMA:
                    selected_quantity -= 1

            # Aggiornamento OUTPUT
            if not SIMULAZIONE:
                # Aggiorno le variabili dei LED
                for i in range(lunghezza_binario):
                    slot_leds[len(nomi_led_slot) - 1 - i] = int(bin_leds[lunghezza_binario - 1 - i])
                for i in range(len(slot_leds)):
                    leds[nomi_led[i]] = slot_leds[i]

                leds["RGB_Red"] = True
                leds["RGB_Blue"] = True

            if state_change:
                if products[selected_product]["Quantita"] == 0:
                    next_state = "SelezioneProdotto"
                    lcdWrite("Prodotto".center(16), "Esaurito!".center(16))
                    printFormatted("Prodotto Selezionato Esaurito")
                elif (saldo <= products[selected_product]["Prezzo"]):
                    next_state = "SelezioneProdotto"
                    lcdWrite("Saldo".center(16), "Insufficente!".center(16))
                    printFormatted("Saldo Insufficente")
                else:
                    lcdWrite("Seleziona la".center(16), ("quantita: " + str(selected_quantity) + "/" + str(products[selected_product]["Quantita"])).center(16))
                    printFormatted("Quantita Selezionata:", selected_quantity)
            if PIU or MENO:
                if SERIAL_ARDUINO:
                    # Scrivi la stringa sullLCD
                    lcdWrite("Seleziona la".center(16), ("quantita: " + str(selected_quantity) + "/" + str(products[selected_product]["Quantita"])).center(16))
                printFormatted("Quantita Selezionata:", selected_quantity)

            # Uscita
            if CANCEL:
                next_state = "SelezioneProdotto"
            if CONFIRM:
                next_state = "CheckProdotto"

        elif (current_state == "CheckProdotto"):
            # Funzione e Uscita
            prezzo = products[selected_product]["Prezzo"]
            importo = prezzo * selected_quantity
            if saldo >= importo:
                updateSaldo(saldo - importo, ID_Chiavetta)
                printFormatted("Prodotto acquistato")
                next_state = "Erogazione"
            else:
                printFormatted("Saldo insufficente")
                lcdWrite("Saldo".center(16), "Insufficente".center(16), 2.5)
                next_state = "SelezioneProdotto"

        elif (current_state == "Erogazione"):
            if state_change:
                lcdWrite("IN EROGAZIONE...", LCD_EROGAZIONE)
            # Funzione
            # Lampeggio LED
            if not SIMULAZIONE:
                # Aggiorno le variabili dei LED
                for i in range(lunghezza_binario):
                    slot_leds[len(nomi_led_slot) - 1 - i] = int(bin_leds[lunghezza_binario - 1 - i])
                for i in range(len(slot_leds)):
                    leds[nomi_led[i]] = slot_leds[i]

                if state_change:
                    if not SIMULAZIONE:
                        # Avvio Lampeggio Led
                        lampeggio.start("RGB_Blue")
                    
            # Aggiornamento dell'acquisto nel DB
            updateDB(ID_Chiavetta, saldo, products[selected_product], selected_quantity)

            printFormatted("In Erogazione")
            # Tempo di attesa per l'erogazione del Prodotto
            time.sleep(5)
            #Reset della condizione di Erogazione nel DB
            resetErogazione(products[selected_product]["Slot"])

            if not SIMULAZIONE:
                # Termine Lampeggio Led
                lampeggio.stop("RGB_Blue")
            printFormatted("Erogazione Completata")
            # Uscita
            next_state = "RichiestaProdotti"

################################ Saldo

        elif (current_state == "RichiestaSaldo"):
            # Funzione
            saldo = getSaldo(ID_Chiavetta)
            waiting_key = False
            next_state = "ModificaSaldo"
            
        elif (current_state == "ModificaSaldo"):
            # Funzione
            if state_change:
                printFormatted("Saldo attuale:" , saldo)
            if SIMULAZIONE:
                if waiting_key == False:
                    # Verifica che new_saldo sia un numero
                    new_saldo = input(bold("Nuovo Saldo: "))
                    while not new_saldo.isnumeric():
                        print(bold("INSERIRE UN NUMERO INTERO!!!"))
                        new_saldo = input(italic("Nuovo Saldo: "))
                    new_saldo = int(new_saldo)
                    delta_saldo = new_saldo - saldo
                    printFormatted("Conferma: ", BUTTON_CONFIRM)
                    printFormatted("Annulla: ", BUTTON_CANCEL)
                    # Aspetta decisione dell'utente
                    waiting_key = True
            else:
                if PIU:
                    delta_saldo += 0.5
                if MENO:
                    if saldo + delta_saldo - 0.5 > 0:
                        delta_saldo -= 0.5
                    else:
                        delta_saldo = 0 - saldo
                        lcd_error = True
                new_saldo = saldo + delta_saldo

                # Aggiornamento OUTPUT
                leds["RGB_Blue"] = True
                leds["RGB_Green"] = True

                if PIU or MENO or state_change:
                    if SERIAL_ARDUINO:
                        # Scrivi la stringa sullLCD
                        if delta_saldo > 0:
                            lcd_line2 = "Metti: (+" + str(delta_saldo) + ")"
                        elif (delta_saldo < 0):
                            lcd_line2 = "Togli: (" + str(delta_saldo) + ")"
                        else:
                            lcd_line2 = ""
                        if lcd_error:
                            lcd_line2 = "Azzera Saldo"
                        lcdWrite(("Saldo: " + str(round(saldo, 2)) + "EUR"), lcd_line2)
                    printFormatted("Nuovo Saldo:" , round(new_saldo, 2))

            # Uscita
            if CANCEL:
                waiting_key = False
                next_state = "Menu"
            if CONFIRM:
                if delta_saldo != 0 and new_saldo >= 0:
                    next_state = "AggiornaSaldo"
                else:
                    printFormatted("Impossibile aggiornare il Saldo")
            
        elif (current_state == "AggiornaSaldo"):
            # Funzione e Uscita
            ricaricaSaldo(new_saldo, ID_Chiavetta, delta_saldo)
            printFormatted("Saldo aggiornato")
            delta_saldo = 0
            next_state = "RichiestaSaldo" 
        
################################ Transazioni
            
        elif current_state == "MenuTransazioni":
            # Funzione
            if PIU:
                if selected_type < len(menu_Transazioni_options) - 1:
                    selected_type = selected_type + 1
            if MENO:
                if selected_type > 0:
                    selected_type = selected_type - 1
            
            # Aggiornamento OUTPUT
            if not SIMULAZIONE:
                leds["RGB_Red"] = True

            if PIU or MENO or state_change:
                lcdWrite("Transazioni:".center(16), str(menu_Transazioni_options[selected_type]).center(16))
                printFormatted("Tipologia Transazione:", menu_Transazioni_options[selected_type])

            # Uscita
            if CANCEL:
                next_state = "Menu"
            if CONFIRM:
                if menu_Transazioni_options[selected_type] == "Acquisti":
                    next_state = "RichiestaAcquisti"
                if menu_Transazioni_options[selected_type] == "Ricariche":
                    next_state = "RichiestaRicariche"

        elif current_state == "RichiestaAcquisti":
            # Funzione
            transazioni = getTransazioni(ID_Chiavetta, "Acquisto") 
            
            # Verifica la Presenza di Transazioni
            if transazioni:
                # Uscita
                selected_transazione = 0
                next_state = "MostraAcquisti"
            else:
                printFormatted("Nessun Acquisto effettuato")
                lcdWrite("Nessun".center(16), "Acquisto".center(16))
                next_state = "MenuTransazioni"

        elif current_state == "MostraAcquisti":
            # Aggiornamento OUTPUT
            if not SIMULAZIONE:
                leds["RGB_Red"] = True
            
            # Funzione
            if PIU:
                if selected_transazione < len(transazioni) - 1:
                    selected_transazione += 1

            if MENO:
                if selected_transazione > 0:
                    selected_transazione -= 1

            if PIU or MENO or state_change:
                id_transazione = transazioni[selected_transazione]["IDTransazione"]
                importo_transazione = transazioni[selected_transazione]["Importo"]
                quantita_transazione = transazioni[selected_transazione]["Quantita"]
                nome_prodotto = getNomeProdotto(transazioni[selected_transazione]["IDTransazione"])
                printFormatted("ID: ", id_transazione)
                printFormatted("Nome Prodotto: ", nome_prodotto)
                printFormatted("Importo: ", importo_transazione)
                printFormatted("Quantita: ", quantita_transazione)
                lcdWrite("{}| {}".format(selected_transazione + 1, nome_prodotto), ("Q: {} |A| I: {}".format(quantita_transazione, importo_transazione)).center(16))

            # Uscita
            if CANCEL:
                next_state = "MenuTransazioni"
            
            if CONFIRM:
                next_state = "VerificaProdotto"

        elif current_state == "VerificaProdotto": ################################################################################################ WORK IN PROGRESS
            if state_change:
                slot = checkProduct(nome_prodotto)     

            # Funzione ed uscita
            if slot:
                slot = slot[0][0]
                printFormatted("Slot: ", slot)

                # Calcola il selected_product sapendo lo Slot
                products = getProducts()
                count = 0
                for product in products:
                    if product["Slot"] <= slot and product["NomeProdotto"] != "Vuoto":
                        count += 1
                selected_product = count - 1
                next_state = "RichiestaProdotti"
            else:
                lcdWrite("Prodotto non".center(16), "piu disponibile".center(16))
                printFormatted("Il Prodotto richiesto non è piu disponibile nel distributore")
                next_state = "MostraAcquisti"

        elif current_state == "RichiestaRicariche":
            # Funzione
            transazioni = getTransazioni(ID_Chiavetta, "Ricarica")

            # Verifica la Presenza di Transazioni
            if transazioni:
                # Uscita
                selected_transazione = 0
                next_state = "MostraRicariche"
            else:
                printFormatted("Nessuna Ricarica effettuata")
                lcdWrite("Nessuna".center(16), "Ricarica".center(16))
                next_state = "MenuTransazioni"

        elif current_state == "MostraRicariche":
            # Aggiornamento OUTPUT
            if not SIMULAZIONE:
                leds["RGB_Red"] = True
            
            # Funzione
            if PIU:
                if selected_transazione < len(transazioni) - 1:
                    selected_transazione += 1

            if MENO:
                if selected_transazione > 0:
                    selected_transazione -= 1

            if PIU or MENO or state_change:
                id_transazione = transazioni[selected_transazione]["IDTransazione"]
                importo_transazione = transazioni[selected_transazione]["Importo"]
                printFormatted("ID: ", id_transazione)
                printFormatted("Importo: ", importo_transazione)
                lcdWrite("Ricarica N.{}".format(id_transazione).center(16), ("|R| I: {}EUR".format(importo_transazione)))

            # Uscita
            if CANCEL:
                next_state = "MenuTransazioni"
            
            if CONFIRM:
                next_state = "RipetiRicarica"
        
        elif current_state == "RipetiRicarica":
            # Funzione ed uscita
            if saldo - importo_transazione >= 0:
                delta_saldo = importo_transazione
                next_state = "RichiestaSaldo"
            else:
                printFormatted("Richiesta non Valida")
                next_state = "RichiestaSaldo"
            
################################ Restart MAS

        elif (current_state == "Error"):
            if state_change:
                lcdWrite("#Error on Query#".center(16), "Riavvio MAS".center(16))
            # Funzione
            printFormatted("Errore generico nel DB")

            # Uscita
            error = False
            next_state = "Reset"

        elif (current_state == "Reset"):
            # Funzione
            if state_change:
                lcdWrite("Resetting MAS...")
            ID_Chiavetta = ""
            saldo = ""

            # Aggiornamento OUTPUT
            printFormatted("MAS RESTARTATA")

            # Uscita
            next_state = "AttesaChiavetta"

        else:
            # Errore nella macchina a stati
            printFormatted("ERRORE NEL CAMBIO STATO")

            next_state = "Reset"

        # Aggiorniamo lo stato precedente dopo aver effettuato la lettura
        last_state_pulsanti = pulsanti.copy()

        # Aggiornamento degli Outputs
        if not SIMULAZIONE:
            for i , led_name in enumerate(leds):
                updateLed(led_name, leds[led_name])

        # Ripristina l'errore generico per l'LCD
        lcd_error = False

        if error:
            next_state = "Error"
        
        # Ritardo per evitare di occupare troppe risorse del PC
        time.sleep(0.1)

        if TIV and not SIMULAZIONE:
            test_in_vita()

#######################################################
            
#### MAIN
if __name__ == "__main__":
    # MAS
    stateMachine()

    # Chiusura della porta seriale
    board_RFID_LCD.close()