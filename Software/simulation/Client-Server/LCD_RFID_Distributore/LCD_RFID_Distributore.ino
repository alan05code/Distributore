/*
 * Typical pin layout used:
 * -----------------------------------------------------------------------------------------
 *             MFRC522      Arduino       Arduino   Arduino    Arduino          Arduino
 *             Reader/PCD   Uno/101       Mega      Nano v3    Leonardo/Micro   Pro Micro
 * Signal      Pin          Pin           Pin       Pin        Pin              Pin
 * -----------------------------------------------------------------------------------------
 * RST/Reset   RST          9             5         D9         RESET/ICSP-5     RST
 * SPI SS      SDA(SS)      10            53        D10        10               10
 * SPI MOSI    MOSI         11 / ICSP-4   51        D11        ICSP-4           16
 * SPI MISO    MISO         12 / ICSP-1   50        D12        ICSP-1           14
 * SPI SCK     SCK          13 / ICSP-3   52        D13        ICSP-3           15

 * Monitor LCD
 * VCC                      5V
 * GND                      GND
 * SCL                      A5
 * SDA                      A4
 */

#include <MFRC522.h>
#include <Wire.h>   

#include <LiquidCrystal_I2C.h>

////////////////////////////////////////////////// CONFIGURAZIONE

// Start Arduino
#define RFID_START_REQUEST "<START>"
#define RFID_START_RESPONCE "<STARTED>"
bool connected = false;

// invio uid
#define RFID_UID "<uid>"

// Definisco il protocollo per identificare la richiesta di stampa sull'LCD
#define LCD_PRINT "<lp>"
#define LCD_CHANGE_LINE "@"

// Dichiarazione richieste specifiche
#define LCD_ATTESA_CHIAVETTA "<attesa>"
bool attesa_chiavetta = false;
#define LCD_EROGAZIONE "<erogazione>"

////////////////////////////////////////////////// LCD

// Definizione di LCD
LiquidCrystal_I2C lcd(0x27,20,4);

////////////////////////////////////////////////// RFID

// Definizione di RFID
MFRC522 rfid(10, 9);

// Funzione per leggere l'UID 
void getUID() {
  String uid = "";
  for(int i = 0; i < rfid.uid.size; i++){
    uid += rfid.uid.uidByte[i] < 0x10 ? "0" : "";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  rfid.PICC_HaltA();
  // Stampo in seriale con il protocollo
  Serial.println(RFID_UID + uid);
}

////////////////////////////////////////////////// SETUP

void setup() {
  // Inizializzazione Seriale
  Serial.begin(115200);
  Serial.flush();

  // Inizializzazione RFID
  SPI.begin();
  rfid.PCD_Init();

  // Inizializzazione LCD
  lcd.init();
  lcd.backlight();
  lcd.clear();
  //lcd.autoscroll();

  // Stampa di Benvenuto
  char welcome_line0[16] = "  Caricamento   ";
  char welcome_line1[16] = "Distributore....";
  lcd.setCursor(0, 0);
  for (int i = 0; i < 16; i++) {
    lcd.print(welcome_line0[i]);
    delay(50);
  }
  lcd.setCursor(0, 1);
  for (int i = 0; i < 16; i++) {
    lcd.print(welcome_line1[i]);
    delay(50);
  }
}

////////////////////////////////////////////////// LOOP

// Variabile per la funzione Attesa Chiavetta
#define ac_char_interval 25
unsigned long ac_new_char = 0;
int dot_count = 0;
bool clear_dots = false;

void loop() {
  // Verifica presenza di nuovo RFID
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()){
    getUID();
    attesa_chiavetta = false;
  }

  // Funzioni specifiche del client
  if (attesa_chiavetta) {
    unsigned long current_time = millis();

    if (current_time - ac_new_char >= ac_char_interval) {
      ac_new_char = current_time;

      if (!clear_dots) {
        lcd.setCursor(dot_count, 1);
        lcd.print(".");
        dot_count++;

        if (dot_count == 16) {
            clear_dots = true;
        }
      } else {
        lcd.setCursor(16 - dot_count, 1);
        lcd.print(" ");
        dot_count--;

        if (dot_count == 0) {
            clear_dots = false;
        }
      }
    }
  }

  // Controllo Seriale
  if (Serial.available()){
    String request = Serial.readString();

    if (request.indexOf(RFID_START_REQUEST) != -1) {
      Serial.println(RFID_START_RESPONCE);
      connected = true;
    } 
    
    // Verfica che sia collegato alla scheda
    if (connected) {
      // Controllo che sia una richiesta valida
      if (request.indexOf(LCD_PRINT) != -1) {
        lcd.clear();
        request.replace(LCD_PRINT, "");

        // Trova la posizione del delimitatore
        int delimiterPos = request.indexOf(LCD_CHANGE_LINE);
        if (delimiterPos != -1) {
          // Estrai le due stringhe separate
          String linea1 = request.substring(0, delimiterPos);
          String linea2 = request.substring(delimiterPos + 1);
          
          // Stampo nell'LCD la prima linea
          lcd.setCursor(0, 0);
          lcd.print(linea1);

          // Controllo richieste specifiche
          if (linea2.indexOf(LCD_ATTESA_CHIAVETTA) != -1) {
            attesa_chiavetta = true;
          } else
          if (linea2.indexOf(LCD_EROGAZIONE) != -1) {
            lcd.setCursor(0, 0);
            lcd.print(request);
            lcd.setCursor(0, 1);
            for (int i = 0; i < 15; i++) {
              lcd.print("=");
              delay(300);
            }
            lcd.print(">");
          } else {
            // Stampo nell'LCD la seconda linea
            lcd.setCursor(0, 1);
            lcd.print(linea2);
          }
        }
      }
    } else {
      delay (100);
    }
  }
}