# BLE mesh projekti
- Yleiskuvaus
Projektissa toteutetaan BLE mesh -verkko, joka välittää lämpötila- ja ilmankosteusdataa.
Verkko muodostuu ESP32-moduuleihin perustuvista solmuista,
joissa käytetään SHTC3-sensoria lämpötilan ja ilmankosteuden mittaamiseen.
Solmut välittävät mittausdatan pääsolmulle, jonka kautta data siirretään Raspberry Pi:lle. 
Raspberry Pi toimii gatewayna ja tallentaa datan tietokantaan, josta mittaustietoja voidaan lukea web-käyttöliittymän kautta.

- Lohkokaavio

