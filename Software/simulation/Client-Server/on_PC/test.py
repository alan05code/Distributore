import time
import serial

# Configura la porta seriale
PORT_RFID_LCD = 'COM6'
board_RFID_LCD = serial.Serial(port=PORT_RFID_LCD , baudrate=115200, timeout=.1)
# Aspetta un dato e stampalo quando arriva
if __name__ == "__main__":
    print("Avvio Monitoraggio Seriale in:", PORT_RFID_LCD)
    
    while True:
        if board_RFID_LCD.in_waiting > 0:
            # Leggi il dato dalla porta seriale
            response = board_RFID_LCD.readline().decode().strip()  # Decodifica i byte in stringa e rimuove i caratteri di newline
            
            # Stampa il dato
            print("Dato ricevuto:", response)
        
        time.sleep(0.1)

    # Chiudi la porta seriale
    board_RFID_LCD.close()
