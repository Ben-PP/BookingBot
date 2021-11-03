# BookingBot v2

Varausbotti booking järjestelmään.

Botti kykenee varaamaan vuoroja järjestelmästä haluamani päivänä ja kellonaikana
sekä lisää onnistuneen varauksen omaan google kalenteriini.

Miksi?

Idea tähän lähti keväällä 2021 kun aloin jälleen aktiivisesti käymään
salilla ja totesin, että taloyhtiöni omaan saliin oli mahdoton saada vuoroja
vaikkei kukaan ikinä salia käyttänyt. Vuoroja varailtiin siis "varmuuden vuoksi"
ja yleensä jätettiin käyttämättä.
	
ärjestelmä
	
Salivuoroja varataan KOAS Booking järjestelmässä joka on
verkkosivupohjainen. Järjestelmässä voi vuoroja varata korkeintaan 14 vuorokauden
päähän. Uusi päivä aukeaa varattavaksi aina kello 00:00.
	
BookingBot
	
Ratkaisuna tähän, ettei minun tarvitse joka päivä kello 23:59 olla
kuluttamassa F5 näppäintä näitä varmuudenvuoksivarailijoita vastaan, lähdin
miettimään olisiko tähän mahdollista tehdä jotakin automaattista ratkaisua. Yhden
vaihtoehdon tarjosi Selenium framework. Tämä oli tarjolla minulle tutuille
kielille kuten Java ja C#, mutta päädyin toteuttamaan tätä käyttäen Pythonia.
Tähän päädyin koska Python on pyörinyt pitkään todo listalla kielistä joita
tahtoisin opetella sekä se vaikutti todella helpolta käyttää yhdessä linuxin
kanssa. Seleniumin ja Pythonin käyttöön sattui myös löytymään todella hyviä
ohjeita ja videoita, joten valinta ei ollut vaikea.

Näin alkoi tutkimusmatka Pythoniin, Seleniumiin ja botteihin. Botti lähti
rakentumaan todella sutjakkaasti ja päädyin tutustumaan myös Google Calendar API:n
käyttöön, jotta sain merkattua salivuorot automaattisesti omaan kalenteriini.
Toteutus on suhteellisen suoraviivainen ja ronski. Tästä aivan varmasti näkyy,
että kyseessä on elämäni ensimmäinen kosketus Pythoniin ja muihin teknologioihin
joita käytettiin. Pyrin rakentamaan bottia vauhista ja ratkaisemaan aina ongelman
kerrallaa, kun niitä tuli.
	
Rakenne ja toiminta

Simppeli scripti joka ajetaan aina uudelleen joka kerta kun halutaan kokeilla
varata vuoroa.
	
Päätapahtumat
1. 	Muutama muuttuja joita voi olla tarpeen muuttaa joskus.
2. 	Webdriverin käynnistys.
3. 	Luodaan tarvittavat päivämäärä muuttujat.
4. 	Luodaan logitiedosto jonne kirjataan tapahtumia pitkin ajoa myöhempää
	tarkastelua varten.
5.	Tunnistaudutaan googlelle(OAUTH2).
6.	Kirjaudutaan sisälle Booking palveluun
7.	Navigoidaan oikealle sivulle ja aloitetaan päivittämään sivua kunnes
	oikean päivän sivu on latautunut
8.	Varataan vuoro oikeasta kellonajasta jossei kyseessä ole lepopäivä
	ja lisätään kalenterimerkintä
9.	Tallennetaan logitiedosto, poistetaan riittävän vanhat logitiedostot ja
	suljetaan ohjelma.

Huomiot ja opit
	
Tämä projekti opetti todella paljon niin Pythonista, Seleniumista, Google
Kalenterista ja Booking-järjestelmän tyyppisistä palveluista sekä niiden
heikkouksista ja ongelmista.

Ensinnäkin Python tuli tutuksi tämän avulla ja opin ainakin alkeet hyvin.
Parannettavaa löytyy todella paljon ja matka on vielä pitkä, että Python sujuu
luontevasti ja monimutkaisemmat ohjelmat alkavat rakentua järkevästi ja oikein.

Toinen huomio mikä projektin aikana tuli tehtyä on se, että kuinka ei
tehdä varauspalvelua, jossa on tärkeää pystyä rajoittamaan käyttäjän
mahdollisuuksia varata jotakin. Booking palvelusta paljastui esimerkiksi, että
vuorojen varaaminen kuinka pitkälle tulevaisuuteen tahansa on mahdollista
muokkaamalla varauksen tekemiseen käytettävää URL-osoitetta.

Seuraavaksi?
	
Seuraavaksi lähden toteuttamaan samaista toiminnallisuutta Javan puolella
ja graafisella käyttöliittymällä. Myös joka kerta uudelleen ajettavan ohjelman
sijasta koitan seuraavalla kerralla tehdä kokoajan päällä olevan ohjelman, joka
tietyin ajoin käy varaamassa vuoron.

Seuraavaan versioon parannettavaa löytyy myös esimerkiksi salasanan ja
käyttäjätunnuksen käsittelystä. Sitä on parannettava ja tehtävä
tietoturvallisemmaksi. Myös Googlen kalenteri API:n implementoinnin koitan ensi
versioon tehdä kokonaiseksi ja monipuolisemmaksi. Myös yleisesti koodin rakenteen
koitan tehdä selkeämmäksi ja olio-ohjelmoinnin mukaiseksi. Tämä tulee olemaan
hieman helpompaa Javalla, sillä siitä löytyy kokemusta hieman enemmän.
