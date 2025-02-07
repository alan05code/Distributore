#ifndef RFID_FUNCTIONS_H
#define RFID_FUNCTIONS_H

#include <Arduino.h>
#include <MFRC522.h>
#include "CONFIG.h"

extern MFRC522 rfid;

String getUID();

#endif
