#ifndef QUERY_FUNCTIONS_H
#define QUERY_FUNCTIONS_H

#include <Arduino.h>
#include "CONFIG.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "lcd_functions.h"
#include "structs.h"
#include "seriale.h"
#include "WiFiConnector.h"

extern bool sqlError;
extern const int MAX_RETRIES;

JsonDocument send_query(String query);
JsonDocument autUID(String uid);
void getProducts();
float getSaldo(String codice_chiavetta);
void updateSaldo(float new_saldo, String codice_chiavetta);
void ricaricaSaldo(float new_saldo, String codice_chiavetta, float importo);
void updateDB(String codice_chiavetta, float saldo, Product product, int quantita_selezionata);
void resetErogazione(int slot);
void getTransazioni(String codice_Chiavetta, String tipologia_transazione);
int checkProduct(String nome_prodotto);
String getNomeProdotto(int id_transazione);

#endif
