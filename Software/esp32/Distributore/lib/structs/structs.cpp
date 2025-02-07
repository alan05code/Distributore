#include "structs.h"

Product products[MAX_SLOT];
Transazioni transazioni[LIMITE_TRANSAZIONI];

// Funzione per resettare la struct Prodotti
void resetProducts() {
    for (int i = 0; i < MAX_SLOT; i++) {
        products[i].nomeProdotto = "Vuoto";
    }
}

// Funzione per resettare la struct Transazioni
void resetTransazioni() {
    for (int i = 0; i < LIMITE_TRANSAZIONI; i++) {
        transazioni[i].id_transazione = -1;
    }
}