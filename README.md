## Overview

Resonant scanning is essential for high-speed and *in vivo* laser scanning microscopy. However, resonant scanners are susceptible to jitter due to a mismatch between the mirror's mechanical oscillation and the data acquisition system's pixel sampling clock. If the digitizer samples at a fixed rate, the pixels on one line land in slightly different positions than on the next and the raw data appears shifted from line to line.

Our solution is to generate the digitizer sample clock **from the resonant scanner's own sync signal** using a PLL. Every line is then sampled at the same scanner phase, so the pixel grid follows the scanner rather than drifting against it. The method runs in real time, is entirely electrical and requires no software changes, so it can be easily incorporated into most existing microscopy systems. 

This approach is described and validated in:

> Ching-Roa VD, Huang CZ, Giacomelli MG. **Suppression of Subpixel Jitter in Resonant Scanning Systems With Phase-locked Sampling.** *IEEE Transactions on Medical Imaging* 43(6):2159–2168, 2024. [doi:10.1109/TMI.2024.3358191](https://doi.org/10.1109/TMI.2024.3358191) · [PubMed 38265914](https://pubmed.ncbi.nlm.nih.gov/38265914/)

The repository is organized into separate folders: PLL_AD9544 contains the KiCAD design files for the board, Configuration Files contains the AD9544 register configurations and a script to convert them into EEPROM images, and EEPROM_writer together with PLL_EEPROM_upload.m are used to program the configuration onto the board.

## AD9544 PLL Board 
This PCB receives the resonant scanner sync signal, locks to it using an Analog Devices AD9544 clock generator, and outputs a phase-locked sample clock for the digitizer and a line trigger. The AD9544 is referenced to a 52 MHz crystal, and its configuration is stored in a 24AA16 I2C EEPROM, which the AD9544 loads automatically at power-up. A SAMD21 microcontroller receives commands over USB and is used to program the EEPROM. Power is supplied over USB and regulated down to 3.3 V and 1.8 V, and a PLL LOCK LED indicates when the PLL has locked to the reference.

- **J1 (USB):** power and EEPROM programming
- **J3 (output):** phase-locked pixel sample clock to the digitizer
- **J4 (output):** line trigger at the scanner frequency
- **J5 (input):** resonant scanner sync signal (8 kHz or 12 kHz)


See: [PLL_AD9544](PLL_AD9544). [Bill of materials](https://htmlpreview.github.io/?https://github.com/tikagergaia/PLL/blob/main/PLL_AD9544/ibom.html)

![PLL Board](https://github.com/tikagergaia/PLL/blob/main/PLL_AD9544/pll_ad9544.jpg)

## Configuration files
1. The AD9544 is configured through its registers, which are designed using the [Analysis|Control|Evaluation(ACE) Software Version 1.10.2671.1118](https://swdownloads.analog.com/ACE/ACEInstall_1.10.2671.1118.exe). *Do not update it to newer versions as they are not tested with the AD9544 plug-in module.* In ACE, set up the reference input, DPLL, output frequencies, and loop bandwidth. The ACE session can then be exported as a `.cso` file for the register settings.

   ![ACE Software](https://github.com/tikagergaia/PLL/blob/assets/ACE.png)

   The PLL LOCK LED is driven by the AD9544's M0 multifunction pin (M-pin), which is set up in ACE as a lock status output:

   ![LED_config](https://github.com/tikagergaia/PLL/blob/assets/LED_config.png)

2. Use the `ad9545_create_eeprom_bin.py` script to generate bin files for EEPROM. Set `fn` in the script to your `.cso` file and run it from inside the `Configuration Files` folder (it needs `bitarray.py` and `defaults.txt`, which are in the same folder). It writes a `.bin` file with the same name as the `.cso`.

Sample files for 8 kHz and 12 kHz scanners are available in the `Configuration Files` folder (both `.cso` and ready-to-upload `.bin` files are included).

The approach does not depend on the AD9544. Other clock chips (for example, the AD9545) can do the same job. They need their own configuration files and EEPROM image, but the principle stays the same.

## Programming EEPROM
The EEPROM_writer folder contains the Arduino sketch for the SAMD21 microcontroller, which requires the [I2C_eeprom](https://github.com/RobTillaart/I2C_EEPROM) library. On startup, the sketch reports the EEPROM size and the scanner frequency currently stored in it.

To program a configuration onto the board:

1. Upload `EEPROM_writer/EEPROM_writer.ino` to the SAMD21 using the Arduino IDE.
2. Open `PLL_EEPROM_upload.m` in MATLAB, set the path to your `.bin` file (e.g. `Configuration Files/12kHz_LED.bin`) and the board's COM port (`'COMX'`), and run the script. It sends the `program` command followed by the 1280-byte image, reads the EEPROM contents back and compares checksums. "Checksum of file matches uploaded data." means the upload succeeded.
3. Power-cycle the board. The AD9544 loads its configuration from the EEPROM, and the PLL LOCK LED lights once a valid reference is connected.

## Ordering boards

Go to https://jlcpcb.com, https://www.seeedstudio.com/fusion_pcb.html or the service of your choice, upload the Gerber files, and pay.

Gerber files can be generated from KiCAD using 'File -> Plot' or using the JLCPCB Fabrication Toolkit plugin (settings are included in `PLL_AD9544/fabrication-toolkit-options.json`).

## Board assembly

The easiest way to assemble this board is using solder paste and a reflow oven or hotplate. The AD9544 comes in a 48-lead LFCSP package with an exposed ground pad, and most of the passives are 0402, so reflow is strongly recommended over hand soldering. If you're going to make several boards, paying for assembly of the passive and common components might be worthwhile.