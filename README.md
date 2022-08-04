# LTE_Search
## Overview
This is the codebase for my LTE Project using a Raspberry Pi 3b+ and a LTE_Hat with a Telit Cellular Modem. I will try my best to describe my code so other can leverage the same ideas. For details on the project check it out on my website:
https://ewf-engineering.com/lte-cell-search-w-raspberry-pi-and-mpice-lte-modem/

The only main files are:
 * Search.py
 * GPSMain.py
 * LTEMain.py
 * Display.py

# File Descriptions
## Search.py
Search is the main file used to start the others. After setup each is spawned as a subprocess and access the mysql database to share data and resources. Im not sure if this was the best way to "share" data, but if felt the smoothest for my time in development.

The main goal is to setup the SQL database and enable to serial streams. The Telit modem has 2 stream USB1 which will be used for AT COMMANDS and USB2 which is used for GPS NEMA format streams. After the setup has been validated, we spawn the other processes. 

## GPSMain.py
Here we read and parse the NEMA formatted messages and send them to the SQL database. We set write to be no contest if the LTEMain function is currently writing. The idea that GPS is not changing as much as the cells, and that GPS is 1 per second and the CellSearch command from the modem takes about 20s to complete.

## LTEMain.py
This call the Cell Search function from the Telit modem. We take the data, parse it, and write it to the SQL database. For information about the AT Commands refer to the Telit documentation

## Display.py
Here we just pull/read whatever data is being writting to the SQL database and pull some other stuff like time/temp/cpu usage whatever. Formatting the display took longer than expected. I'm not a UI sort of guy. We also read any button presses here if they are used. 

## Other.py files
The other files are used as referece to test functions.I used these to test the files individually because I wasn't able to figure out how to call each file as a subprocess and also as an individual file too.... w/e 

# Sequence Diagram
![PlantUML model](http://plantuml.com:80/plantuml/svg/VP4_JyCm4CNtVegR41r0AcC6L4Y1fPKAQJUMQt85I_vZ-MnGlptNn0gnLF1qrdltydlnaYE6c8oUoV4ogbPvj14Qmj1-tleJ80Ftbq9Vxvusg6msw4Y5-h9j9kg7vq9TAVOQJrdjXblXCAVcTTsB6F60J48tGC3DFUIfSfxiwFXBRoWerF1kQsSjjL4vot2zkBgRJpQ47ofWZzyME1ryS2qnJmnIuNz3Rd799E6_twX9wsRO-b883xjwinAUVVCuW2xcsJyM0wZsNZliuDabs_K9F1EWaIkGY9OC0aUPpIHEMegbYAkW8TlLAGGQNWfM8iroWR9Bd_osLQ3iqGM3vxzNE7De1JvftTEW8BPdH3W6Pq1qJNmXlOBaPPt6zp-VfP0bety0)
![LTE_Search](https://user-images.githubusercontent.com/4984563/182913063-ad019f31-ad4d-4325-964e-6ff6a7786024.jpg)
