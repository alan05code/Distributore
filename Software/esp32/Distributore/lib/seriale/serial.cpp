#include "seriale.h"

//// SERIALE
void printToTerminal(String stringa) {
  if (TERMINALE)
    Serial.println(stringa);
}

void printProductList() {
  if (TERMINALE) {
    // Output per verificare i risultati
    for (const auto& product : products) {
      if (product.nomeProdotto != "Vuoto") {
        printToTerminal("Slot: " + String(product.slot) + ", Nome Prodotto: " + String(product.nomeProdotto) + ", Prezzo: " + String(product.prezzo) + ", Quantita: " + String(product.quantita));
      }
    }
  }
}