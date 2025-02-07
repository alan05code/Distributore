#include "lcd_functions.h"

void lcdWrite(String linea1, String linea2, int time_delay) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(linea1);
  if (linea2 != "") {
    lcd.setCursor(0, 1);
    lcd.print(linea2);
  }
  if (time_delay > 0) {
    delay(time_delay);
  }
}
