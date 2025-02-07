import pyfirmata2
from threading import Timer
import time

####################################################### ARDUINO

#### CONFIG
## Configurazione PIN
# Puslanti
nomi_pulsanti = ["MENO", "PIU", "CANCEL", "CONFIRM"]
MENO = 2
PIU = 3
CANCEL = 4
CONFIRM = 5
# Lista Pulsanti
lista_pulsanti = [MENO, PIU, CANCEL, CONFIRM]

# Imposta la porta di comunicazione con Arduino
# PORT = pyfirmata2.Arduino.AUTODETECT
PORT = 'COM5'
# Crea una board
board = pyfirmata2.Arduino(PORT)
print("Connessione con Arduino ...")
# default sampling interval of 19ms
board.samplingOn()

# Lista dei pulsanti inizialiazzata con tutti False
pulsanti = {}
# Funzione di Callback dei pulsanti
def pinCallback(data, index):
    pulsanti[nomi_pulsanti[index]] = not data
    #print("{}: {}".format(nomi_pulsanti[index], pulsanti[nomi_pulsanti[index]]))

# Configura i Pulsanti e associa la funzione di Callback
board_addr_pulsanti = {}
for index, pin in enumerate(lista_pulsanti):
    # Setup the digital pin with pullup resistor: "u"
    board_addr_pulsanti[nomi_pulsanti[index]] = board.get_pin('d:{}:u'.format(pin))
    # Points to the callback with the index as an additional argument
    board_addr_pulsanti[nomi_pulsanti[index]].register_callback(lambda data, index=index: pinCallback(data, index))
    # Switches the callback on
    board_addr_pulsanti[nomi_pulsanti[index]].enable_reporting()

####################################################### LED

# Configuazione LED
nomi_led = ["LED_BIT_0", "LED_BIT_1", "LED_BIT_2", "LED_BIT_3", "LED_RGB_G", "LED_RGB_B", "LED_RGB_R"]
LED_BIT_0 = 6
LED_BIT_1 = 7
LED_BIT_2 = 8
LED_BIT_3 = 9
LED_RGB_G = 11
LED_RGB_B = 12
LED_RGB_R = 13
# Lista Led
lista_led = [LED_BIT_0, LED_BIT_1, LED_BIT_2, LED_BIT_3, LED_RGB_G, LED_RGB_B, LED_RGB_R]

# Intervallo del Lampeggio dei LED
INTERVAL = 0.5

# Configura i Led come Output
board_addr_led = {}
for index, pin in enumerate(lista_led):
    board_addr_led[nomi_led[index]] = board.get_pin('d:{}:o'.format(pin))

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
            print("Tentativo Fallito di Spegnimento del Lampeggio del Led")

###################################################### MAIN

# Loop principale
try:
    lampeggio = Blink(INTERVAL)

    lampeggio.stop('LED_BIT_2')

    lampeggio.start('LED_BIT_1')
    lampeggio.start('LED_BIT_2')
    
    lampeggio.stop('LED_BIT_2')

    print("To stop the program press return.")
    # Just blocking here to do nothing.
    input()

    lampeggio.stop('LED_BIT_2')

    # close the serial connection
    board.exit()
except KeyboardInterrupt:
    print("\nProgramma terminato dall'utente.")
    board.exit()





