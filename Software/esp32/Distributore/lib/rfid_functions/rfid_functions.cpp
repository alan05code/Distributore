#include "rfid_functions.h"

String getUID() {
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String uid = "";
    for (int i = 0; i < rfid.uid.size; i++) {
      uid += rfid.uid.uidByte[i] < 0x10 ? "0" : "";
      uid += String(rfid.uid.uidByte[i], HEX);
    }
    rfid.PICC_HaltA();
    return uid;
  } else {
    return "";
  }
}
