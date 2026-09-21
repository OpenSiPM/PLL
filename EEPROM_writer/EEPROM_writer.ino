#include "Wire.h"
#include "I2C_eeprom.h"

// updated November 13, 2025

I2C_eeprom ee(0x50, I2C_DEVICESIZE_24LC16);  // Define eeprom model

char msgbuf[1280];  // Create message buffer

uint32_t start, diff = 0;

void setup() {

  Serial.begin(115200);  //Open Serial library
  while (!Serial);    //Wait for Serial port to connect
  Serial.println(__FILE__);  //Print file location
  //Print eeprom version
  Serial.print("I2C_EEPROM_VERSION: ");
  Serial.println(I2C_EEPROM_VERSION);

  Wire.begin();  //Open Wire library

  ee.begin();  //Initalize eeprom

  //Determine connection status
  if (!ee.isConnected()) {
    Serial.println("ERROR: Can't find eeprom\nstopped...");
    while (1);
  }
  Serial.print("isConnected:\t");
  Serial.println(ee.isConnected());

  //Determine size of eeprom
  Serial.println("\nTEST: determine size");
  start = micros();
  uint32_t size = ee.determineSize(true);
  diff = micros() - start;
  //Print time to determine size
  Serial.print("TIME: ");
  Serial.println(diff);
  if (size > 0) {
    Serial.print("SIZE: ");  //Print size
    Serial.print(size);
    Serial.println(" Bytes");  //Print number of bytes
  } else if (size == 0) {
    Serial.println("WARNING: Can't determine eeprom size");
  } else {
    Serial.println("ERROR: Can't find eeprom\nstopped...");
    while (1)
      ;
  }

  // Determine the frequency
  /* read in the refb clock period, which is the number of attoseconds (1E-18) per
     resonant scanner cycle.  This is a 6 byte number, but the last two bytes are
     irrelevant at the kHz frequency resolution.
  */
  uint32_t period;
  ee.readBlock(0x9E, (uint8_t *)&period, 4);

  //period is now in 65536 * attoseconds, convert to microseconds
  // uint8_t period_us = period *  6.5536e-08; // 65536/1E+12
  float period_us = period * 6.5536e-08;  // 65536/1E+12
  Serial.print("PERIOD: ");
  Serial.print(period_us);
  Serial.print(" us\n");

  // calculate the frequency in kHz
  float freq = 1000.0 / period_us;
  Serial.print("FREQ: ");
  Serial.print(freq);
  Serial.print(" kHz");
}

void loop() {

  if (Serial.available())
    Serial.read();
  {
    while (!Serial.available()) {}

    //check for command and abort loop if a valid one is not received

    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    char *str = (char *)cmd.c_str();

    if (strcmp(str, "program") != 0) {
      Serial.print("Invalid command:");
      Serial.print(str);
      Serial.print("!");
      return;
    }

    else { //so we don't keep erasing the EEPROM
      int bytes = 0;
      char romBuf[1280];                       //creates character array size of eeprom
      bytes = Serial.readBytes(romBuf, 1280);  //reads the rom into the array


      if (bytes < 1280)
        return;

      ee.writeBlock(0, (uint8_t *)romBuf, 1280);  //writes all bytes into eeprom
      // verify written correctly,into msg buffer
      char readBuffer[1280];
      ee.readBlock(0, (uint8_t *)readBuffer, 1280);
      for (size_t i = 0; i < 1280; i++) {
        sprintf(msgbuf, "%d ", readBuffer[i]);
        Serial.write(msgbuf);  //sends value of bytes to serial monitor
      }
    }
  }
}
