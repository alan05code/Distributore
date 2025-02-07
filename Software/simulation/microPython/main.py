import time
import re

from machine import Pin, SoftI2C, SoftSPI, Timer
import network
import urequests
import ujson

from i2c_lcd import I2cLcd
from mfrc522 import MFRC522

################################################################ DEFINIZIONE CLASSI

class Pulsante:
    def __init__(self, pin_number, nome):
        self.pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)
        self.nome = nome
        self.stato_precedente = False

    def read_stato(self):
        return self.pin.value()

class Led:
    def __init__(self, pin_number, nome):
        self.pin = Pin(pin_number, Pin.OUT)
        self.nome = nome
        self.pin.value(True)

    def set_valore(self, nuovo_valore):
        if isinstance(nuovo_valore, bool):
            self.pin.value(not nuovo_valore)
        else:
            raise ValueError("Il nuovo valore deve essere booleano")

class Blink:
    def __init__(self, durata):
        # Imposta e setta il Delay
        self.timer = {}
        self.DELAY = durata

    # Callback che cambia lo stato del LED e riavvia il timer
    def blinkCallback(self, led):
        # Richiama se stessa per eseguirsi periodicamente
        self.timer[led] = Timer(-1)
        self.timer[led].init(period=self.DELAY, mode=Timer.PERIODIC, callback=lambda t: self.toggleLED(led))

    # Cambia lo stato del LED
    def toggleLED(self, led):
        led.set_valore(not led.pin.value())  # Inverte lo stato del LED

    # Inizia il lampeggio
    def start(self, led):
        # Avvia la funzione di callback
        self.blinkCallback(led)

    # Ferma il lampeggio
    def stop(self, led):
        # Cancella il timer
        try:
            self.timer[led].deinit()
            led.set_valore(False)  # Spegni il LED
        except:
            print("Tentativo Fallito di Spegnimento del Lampeggio del Led")

################################################################ CONFIGURAZIONE DISTRIBUTORE

####################################################### WI-FI

SSID = "iPhone di Alan" # "iPhone di Alan"
PASSWORD = "password" # "password"

####################################################### SERVER

SERVER_IP = "172.20.10.7"
SERVER_PORT = 8080

####################################################### Modalità

# Terminale ON/OFF (Disabilita la possibilità di visualizzare su terminale gli avvenimenti del distributore)
TERMINALE = True

# Connessione con RFID e LCD
SERIAL_ARDUINO = True

####################################################### Pin Arduino

#### Configurazione PIN Arduino
# PULSANTI
PIN_MENO = 23
PIN_PIU = 32
PIN_CANCEL = 33
PIN_CONFIRM = 25

# LED
# SLOT DISTRIBUTORE
PIN_LED_BIT_0 = 19
PIN_LED_BIT_1 = 21
PIN_LED_BIT_2 = 22
PIN_LED_BIT_3 = 23
# RGB
PIN_LED_RGB_R = 2
PIN_LED_RGB_G = 4
PIN_LED_RGB_B = 15

# Monitor LCD
I2C_SCL = 18
I2C_SDA = 5

# RFID
SCK = 12
MOSI = 14
MISO = 27
RST = 26
CS = 13

####################################################### Test in Vita

# TIV ON/OFF
TIV = False
# Pin LED del Test in Vita
PIN_TIV = 2

################################################################ Distributore

# Intervallo del Lampeggio dei LED in ms
INTERVAL = 500

# Numero limite delle transazioni visualizzate
LIMITE_TRANSAZIONI = 10

# Slot del Prodotto selezionato di Default
DEFAULT_PRODUCT = 0
# Quantita del Prodotto Default
QUANTITA_MINIMA = 1

############################################################### Terminale

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

################################################################ Wi-Fi

# Attivazione della rete Wi-Fi
sta_if = network.WLAN(network.STA_IF); sta_if.active(True)

# Funzione per connettersi al Wi-Fi
def wifi_connect():
    printFormatted ("\nTentativo di connessione a:", SSID)
    while not sta_if.isconnected():
        sta_if.scan()
        try:
            sta_if.connect(SSID, PASSWORD)
        except:
            printFormatted ("Tentativo Fallito")
            time.sleep(3)
    printFormatted ("Connessione Effettuata")

################################################################ QUERY REQUEST

### Richiesta
# Funzione per connettersi al server e ricevere i dati
error = False
MAX_RETRIES = 3
def send_query(query):
    global SERVER_IP, SERVER_PORT, error
    if sta_if.isconnected():
        # Converti per metodo GET
        query = re.sub(r'\s+', ' ', query.replace('\n', ' ')).strip()
        query = query.replace("+", "%2B") # Sotituisce "+"
        query = query.replace("-", "%2D") # Sotituisce "-"
        query = query.replace(" ", "%20") # Sotituisce " "

        # Costruisci l'URL della richiesta GET con la query SQL
        url = "http://{}:{}/?query={}".format(SERVER_IP, SERVER_PORT, query)

        # Esegui una richiesta GET corretta al server
        try:
            # Esegui la richiesta GET al server
            response = urequests.get(url)

            # Controlla il codice di stato HTTP
            if response.status_code == 200:
                # Leggi il contenuto della risposta e decodificalo come JSON
                query_result = ujson.loads(response.text)
                
                # Ritorna la Risposta
                if query_result:
                    return query_result
                else:
                    return ""

            else:
                printFormatted ("La query ha restituito un Errore", response.status_code)
            
            # Chiudi la connessione
            if response:
                response.close()
                
        except Exception as e:
            printFormatted ("Errore durante la connessione al Server:", e)
            error = True
            return "Error"
            
    else:
        printFormatted ("Nessuna Connessione")
        error = True
        wifi_connect() 
        return ""

################################################################ ESP32

#### INPUT
# Lista pulsanti
nomi_pulsanti = ["MENO", "PIU", "CANCEL", "CONFIRM"]
lista_pulsanti = [PIN_MENO, PIN_PIU, PIN_CANCEL, PIN_CONFIRM]

# Configurazione Pulsanti
puls_MENO = Pulsante(pin_number=PIN_MENO, nome="MENO")
puls_PIU = Pulsante(pin_number=PIN_PIU, nome="PIU")
puls_CANCEL = Pulsante(pin_number=PIN_CANCEL, nome="CANCEL")
puls_CONFIRM = Pulsante(pin_number=PIN_CONFIRM, nome="CONFIRM")


#### OUTPUT
# Lista Led
nomi_led_slot = ["Slot_Bit0", "Slot_Bit1", "Slot_Bit2", "Slot_Bit3"]
nomi_led_RGB = ["RGB_Red", "RGB_Green", "RGB_Blue"]
nomi_led = nomi_led_slot + nomi_led_RGB
lista_led_slot = [PIN_LED_BIT_0, PIN_LED_BIT_1, PIN_LED_BIT_2, PIN_LED_BIT_3]
lista_led_RGB = [PIN_LED_RGB_R, PIN_LED_RGB_G, PIN_LED_RGB_B]
lista_led = lista_led_slot + lista_led_RGB

# Configurazione Leds
Slot_Bit0 = Led(pin_number=PIN_LED_BIT_0, nome="Slot_Bit0")
Slot_Bit1 = Led(pin_number=PIN_LED_BIT_1, nome="Slot_Bit1")
Slot_Bit2 = Led(pin_number=PIN_LED_BIT_2, nome="Slot_Bit2")
Slot_Bit3 = Led(pin_number=PIN_LED_BIT_3, nome="Slot_Bit3")
RGB_Red = Led(pin_number=PIN_LED_RGB_R, nome="RGB_Red")
RGB_Green = Led(pin_number=PIN_LED_RGB_G, nome="RGB_Green")
RGB_Blue = Led(pin_number=PIN_LED_RGB_B, nome="RGB_Blue")

#### Monitor LCD
I2C_ADDR = 0x20
totalRows = 2
totalColumns = 16

i2c = SoftI2C(scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=10000)
lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)
lcd.clear()
lcd.hal_backlight_on()

#### RFID
spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=SCK, mosi=MOSI, miso=MISO)
spi.init()
rdr = MFRC522(sck=SCK, mosi=MOSI, miso=MISO, rst=RST, cs=CS)


#### X LCD
# Scrivi la stringa sulla porta seriale
# ljust => stringa di 16 caratteri esatti
def lcdWrite(linea1, linea2 = "", time_delay = 0):
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(str(linea1))
    lcd.move_to(0, 1)
    lcd.putstr(str(linea2))
    time.sleep(time_delay)

#### X RFID
# Funzione per verificare la presenza della chiavetta
def checkUID():
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    if stat == rdr.OK:
        (stat, raw_uid) = rdr.anticoll()
        if stat == rdr.OK:
            card_id = "%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
            return card_id
        else:
            return False
    else:
        return False

# Funzione per la verifica dell'autenticazione tramite il DB
def autUID(uid):
    user = send_query("""SELECT Nome, Cognome
                            FROM Utenti
                            WHERE CodiceChiavetta = '{}'; """.format(uid))
    if user == "Error":
        return ""
    elif user:
        return user
    else:
        lcdWrite("Creazione", "nuovo Utente...")
        nome = input("Nome: ")
        cognome = input("Cognome: ")
        send_query("""INSERT INTO Utenti (CodiceChiavetta, Nome, Cognome)
                         VALUES ('{}', '{}', '{}'); """.format(uid, nome, cognome))
        user = send_query("""SELECT Nome, Cognome
                            FROM Utenti
                            WHERE CodiceChiavetta = '{}'; """.format(uid))
    return user

################################################################ X MAS

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
    product_list = send_query("""SELECT Slot AS Slot, NomeProdotto AS NomeProdotto, CAST(Prezzo AS FLOAT) AS Prezzo, Quantita AS Quantita
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
    saldo = send_query("""SELECT CAST(Saldo AS FLOAT) AS Saldo
                             FROM Utenti
                             WHERE CodiceChiavetta = '{}'; """.format(codice_chiavetta))
    return saldo[0][0]
# Funzione per aggiornare il Saldo dell'Utente
def updateSaldo(new_saldo, codice_chiavetta):
    # Aggiornamento saldo
    send_query("""UPDATE Utenti
                    SET Saldo = {}
                    WHERE CodiceChiavetta = '{}'; """.format(new_saldo, codice_chiavetta))
# Funzione per effettuare ricarica del Saldo
def ricaricaSaldo(new_saldo, codice_chiavetta, importo):
    # Aggiornamento del Saldo
    updateSaldo(new_saldo, codice_chiavetta)

    # Aggiornamento Tabella Transazioni
    send_query("""INSERT INTO Transazioni (CodiceChiavetta, TipoTransazione, Importo)
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
    send_query("""UPDATE Utenti
                    SET NumeroAcquisti = NumeroAcquisti + 1,
                        TotaleAcquisti = TotaleAcquisti + {}
                    WHERE CodiceChiavetta = '{}'; """.format(importo, codice_chiavetta))

    # Aggiornamento Tabella Prodotti
    send_query("""UPDATE Prodotti
                    SET QuantitaDisponibile = QuantitaDisponibile - {},
                        QuantitaVenduta = QuantitaVenduta + {}
                    WHERE NomeProdotto = '{}'; """.format(quantita_selezionata, quantita_selezionata, nome_prodotto))

    # Aggiornamento Tabella Transazioni
    send_query("""INSERT INTO Transazioni (CodiceChiavetta, TipoTransazione, Importo, Quantita)
                    VALUES ('{}', 'Acquisto', {}, {}); """.format(codice_chiavetta, importo, quantita_selezionata))

    id_transazione = send_query("""SELECT MAX(IDTransazione) FROM Transazioni; """)
    id_transazione = id_transazione[0][0]
    # Aggiornamento Tabella DettagliTrnasazione
    send_query("""INSERT INTO DettagliTransazione (IDTransazione, NomeProdotto)
                    VALUES ('{}', '{}'); """.format(id_transazione, nome_prodotto))

    # Aggiornamento Quantita in ContenutoDistributore e imposta Erogazione = TRUE
    send_query("""UPDATE ContenutoDistributore
                    SET Erogazione = TRUE,
                        Quantita = Quantita - {}
                    WHERE Slot = {}; """.format(quantita_selezionata, slot))

def resetErogazione(slot):
    send_query("""UPDATE ContenutoDistributore
                    SET Erogazione = FALSE
                    WHERE Slot = {}; """.format(slot))

#### X Transazioni
# Funzione per ottenere le ultime 10 Transazioni del tipo specificato
def getTransazioni(codice_Chiavetta, tipologia_transazione):
    lista_transazioni = send_query("""SELECT IDTransazione AS IDTransazione, CAST(Importo AS FLOAT) AS Importo, Quantita AS Quantita
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
    return send_query("""SELECT Slot
                            FROM ContenutoDistributore
                            WHERE NomeProdotto = '{}'; """.format(nome_prodotto))

def getNomeProdotto(id_transazione):
    nome_prodotto = send_query("""SELECT p.NomeProdotto
                                     FROM DettagliTransazione AS d
                                     JOIN Prodotti AS p ON d.NomeProdotto = p.NomeProdotto
                                     WHERE d.IDTransazione = {}; """.format(id_transazione))

    # Controlla se la lista dei risultati non è vuota. In caso lo sia imposta il nomeProdotto su None
    if nome_prodotto:
        return nome_prodotto[0][0]
    else:
        return None


################################################################ Test in Vita

if TIV:
    # Configura i Led come Output
    test_in_vita = Led(pin_number=PIN_TIV, nome="TestInVita")
    tiv = False

    # Funzione test in vita: alterna lo stato del pin PIN_TIV ogni volta che viene chiamata
    def testInVita():
        global tiv
        tiv = not tiv
        test_in_vita.set_valore = tiv

################################################################ MAS

# Funzione per la macchina a stati
def stateMachine():
    global error
    global current_state
    next_state = "AttesaChiavetta"

    # Inizializzazione a False
    leds = {nome: False for nome in nomi_led}
    dot_count = 0
    clear_dots = False

    # Opzioni del Menu
    menu_options = ["Distributore", "Saldo", "Transazioni"]
    menu_Transazioni_options = ["Acquisti", "Ricariche"]

    # Prodotto selezionato di Default
    selected_product = DEFAULT_PRODUCT

    # Instazio la Classe per il lampeggio dei led
    lampeggio = Blink(INTERVAL)

    # Connessione al Wifi
    wifi_connect()

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
                printFormatted ("Stato richiesto non assegnabile")
                current_state = "Reset"
        else:
            state_change = False

        # Reset LED
        for led in leds:
            leds[led] = False
        # Array per salvare ogni bit
        slot_leds = [0] * len(nomi_led_slot) # Inizializzazione a False

        # Resetto i Led
        Slot_Bit0.set_valore(False)
        Slot_Bit1.set_valore(False)
        Slot_Bit2.set_valore(False)
        Slot_Bit3.set_valore(False)
        RGB_Red.set_valore(False)
        RGB_Green.set_valore(False)
        RGB_Blue.set_valore(False)

        leds[""] = False

        # Gestione INPUT
        # Fronti di Discesa
        if puls_PIU.read_stato() == False and puls_PIU.stato_precedente == True:
            PIU = True
        else:
            PIU = False
        if puls_MENO.read_stato() == False and puls_MENO.stato_precedente == True:
            MENO = True
        else:
            MENO = False
        if puls_CANCEL.read_stato() == False and puls_CANCEL.stato_precedente == True:
            CANCEL = True
        else:
            CANCEL = False
        if puls_CONFIRM.read_stato() == False and puls_CONFIRM.stato_precedente == True:
            CONFIRM = True
        else:
            CONFIRM = False

#### Macchina a Stati
################################ Attesa

        if current_state == "AttesaChiavetta":
            # Svuota la Seriale
            if state_change:
                ID_Chiavetta = ''
                dot_count = 0
                clear_dots = False

            # Alleggerisce il carico in uno stato di inattività
            time.sleep(0.1)

            # Aggiornamento OUTPUT
            if state_change:
                lcdWrite("Attesa Chiavetta".center(16))
                printFormatted ("Attesa Chiavetta...")
            
            # Funzione
            if not clear_dots:
                lcd.move_to(dot_count, 1)
                lcd.putstr(".")
                dot_count += 1

                if dot_count == 16:
                    clear_dots = True
            else:
                lcd.move_to(16 - dot_count, 1)
                lcd.putstr(" ")
                dot_count -= 1

                if dot_count == 0:
                    clear_dots = False
            # Verifica la presenza e salva la Chiavetta (uid ricevuto)
            ID_Chiavetta = checkUID()
            
            # Uscita
            if ID_Chiavetta:
                printFormatted ("Chiavetta inserita:", ID_Chiavetta)
                next_state = "AutenticazioneChiavetta"

        elif (current_state == "AutenticazioneChiavetta"):
            # Funzione e Uscita
            # Verifico la Chiavetta
            # Aggiornamento OUTPUT
            if state_change:
                lcdWrite("Autenticazione".center(16), "Chiavetta".center(16))
                printFormatted ("Autenticazione Chiavetta")
                
            user = autUID(ID_Chiavetta)
            
            if user:
                nome = user[0][0]
                cognome = user[0][1]
                printFormatted("Autenticazione avvenuta con successo")
                printFormatted ("Utente:", (nome + " " + cognome))
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

            # Stampa prodotti
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
                # Scrivi la stringa sull'LCD
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
                printFormatted("Prodotto acquistato")
                next_state = "Erogazione"
            else:
                printFormatted("Saldo insufficente")
                lcdWrite("Saldo".center(16), "Insufficente".center(16), 2.5)
                next_state = "SelezioneProdotto"

        elif (current_state == "Erogazione"):
            if state_change:
                lcdWrite("IN EROGAZIONE...")
            # Funzione
            # Lampeggio LED
            # Aggiorno le variabili dei LED
            for i in range(lunghezza_binario):
                slot_leds[len(nomi_led_slot) - 1 - i] = int(bin_leds[lunghezza_binario - 1 - i])
            for i in range(len(slot_leds)):
                leds[nomi_led[i]] = slot_leds[i]

            if state_change:
                # Avvio Lampeggio Led
                lampeggio.start(RGB_Blue)

            # Aggiornamento dell'acquisto nel DB
            updateDB(ID_Chiavetta, saldo, products[selected_product], selected_quantity)

            printFormatted("In Erogazione")
            
            # Funzione
            # Tempo di attesa per l'erogazione del Prodotto
            for index in range(15):
                lcd.move_to(index, 1)
                lcd.putstr("=")
                time.sleep(0.250)
            lcd.move_to(15, 1)
            lcd.putstr(">")
            time.sleep(0.500)

            #Reset della condizione di Erogazione nel DB
            resetErogazione(products[selected_product]["Slot"])

            printFormatted("Erogazione Completata")
            # Termine Lampeggio Led
            lampeggio.stop(RGB_Blue)
            
            # Uscita
            next_state = "RichiestaProdotti"

################################ Saldo

        elif (current_state == "RichiestaSaldo"):
            # Funzione
            saldo = getSaldo(ID_Chiavetta)
            next_state = "ModificaSaldo"

        elif (current_state == "ModificaSaldo"):
            # Funzione
            if state_change:
                printFormatted("Saldo attuale:" , saldo)
            
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

        elif current_state == "VerificaProdotto":
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
                lcdWrite("Arrivederci...")
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
        puls_PIU.stato_precedente = puls_PIU.read_stato()
        puls_MENO.stato_precedente = puls_MENO.read_stato()
        puls_CANCEL.stato_precedente = puls_CANCEL.read_stato()
        puls_CONFIRM.stato_precedente = puls_CONFIRM.read_stato()

        # Aggiornamento degli Outputs
        RGB_Red.set_valore(leds["RGB_Red"])
        RGB_Green.set_valore(leds["RGB_Green"])
        RGB_Blue.set_valore(leds["RGB_Blue"])

        # Ripristina l'errore generico per l'LCD
        lcd_error = False

        if error:
            next_state = "Error"

        # Test in Vita
        if TIV:
            testInVita()

        # Ritardo per evitare di occupare troppe risorse del PC
        time.sleep(0.1)

################################################################

#### MAIN
if __name__ == "__main__":
    #### Tentativo di Connessione
    printFormatted ("Avvio di Esp32")

    # Stampo lo stato del Terminale
    printFormatted ("\nTerminale impostato su:", TERMINALE)

    # Stampo lo stato del Test in Vita
    printFormatted ("\nTest in Vita impostato su:", TIV)
    if TIV:
        printFormatted ("Test in Vita attivo nel PIN:", PIN_TIV)

    # Avvio della Macchina a Stati
    stateMachine()