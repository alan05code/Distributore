#ifndef LCD_FUNCTIONS_H
#define LCD_FUNCTIONS_H

#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

extern LiquidCrystal_I2C lcd;

void lcdWrite(String linea1, String linea2 = "", int time_delay = 0);

#endif
