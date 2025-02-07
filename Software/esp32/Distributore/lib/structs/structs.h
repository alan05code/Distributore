#ifndef STRUCTS_H
#define STRUCTS_H

#include <Arduino.h>
#include "CONFIG.h"

struct Product {
  int slot;
  String nomeProdotto;
  float prezzo;
  int quantita;
};

struct Transazioni {
  int id_transazione;
  float importo;
  int quantita;
};

extern Product products[MAX_SLOT];
extern Transazioni transazioni[LIMITE_TRANSAZIONI];

// Funzione per resettare le struts
void resetTransazioni();
void resetProducts();

#endif // STRUCTS_H