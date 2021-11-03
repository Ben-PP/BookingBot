#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from datetime import date
from datetime import timedelta
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import datetime
import time
import os
import sys

#------Tiedot joita voi joutua muokkaamaan-----------------------------------

#---Kirjautuminen-----------------
#Sähköposti
POSTI = #Tähän oma sposti stringinä
#Salasana
SANA = #Tähän oma salasana stringinä
#---------------------------------

#Kuinka monta päivää tulevaisuuteen näkee
VARAUSJAKSONPITUUS = 14

#Mitkä päivät ovat lepopäiviä jolloin ei vuoroa varata?
LEPOPAIVAT = ["Tiistai", "Lauantai", "Sunnuntai"]
#Montaako tuntia vuoronajasta eteenpäin kokeillaan varata
VUOROJENMAARA = 2
#Mistä tunnista lähtien tarkistetaan vapaat vuorot?
#1 on päivän ensimmäinen vuoro eli 06:00 paitsi Ti, La ja su jolloin 07:00
VUORONAIKA = 1
#Montako rinnakkaista vuoroa on varattavissa yhdelle tunnille
PAIKKOJENMAARA = 2
#Millä nimellä varaus näkyy. Jos nimeä ei haluta niin laita tyhjä string.
VARAUSNIMI = ""

#Kuinka monta kertaa sivu yritetään ladata uudelleen päivämäärän ollessa väärä
YRITYKSET = 100
#Kuinka kauan odotetaan uudelleenlatauksen välissä sekunteina
SEKUNNIT = 0.5

#Montako päivää logeja säilytetään
LOGIENSAILYTYS = 15
#Polku jonne logikansio halutaan (luo sijaintiin kansion /BBLogs jonne luondaan logitiedosto)
LOGFILEPATH = "./Script Logs"

#Kalenterimerkinnän teksti
CAL_SUMMARY = "Sali"
#Kalenterimerkinnän väri(1=lavender, 2=sage, 3=grape, 4=flamingo, 5=banana, 6=tangerine,
#	7=peacock, 8=graphite, 9=blueperry, 10=basil, 11=tomato)
CAL_COLOR = "10"
#Kuinka monta minuuttia aikaisemmin muistutukset tulee
POPUP1 = 10
POPUP2 = 60*10

#----------------------------------------------------------
#------Metodit ja funktiot---------------------------------
#----------------------------------------------------------

#Kirjautuu booking palveluun sisälle mun tunnuksilla
def kirjautuminen():
	sposti = driver.find_element_by_id("login")
	sposti.send_keys(POSTI)

	ssana = driver.find_element_by_id("password")
	ssana.send_keys(SANA)

	loginnappi = driver.find_element_by_name("submit")
	loginnappi.click()

#Avaa ja tarvittaessa luo /BBLogs kansion ja logitiedoston
def logs():
	if not os.path.exists("%s/BBLogs" % LOGFILEPATH):
		os.makedirs(("%s/BBLogs" % LOGFILEPATH))
	global log
	log = open("%s/BBLogs/Log_%s.txt" % (LOGFILEPATH,pvmTarkistus), "w")

#Palauttaa päivämäärän jolloin halutaan varata eri erotinmerkeillä
def pvm(erotin):
	
	#Jos ohjelma käynnistetään valmiiksi vaihtuneeseen vuorokauteen käytetään
	#varausjakson pituutta sellaisenaan
	if datetime.datetime.now().hour == 00:
		tanaanPlus = date.today() + timedelta(days= VARAUSJAKSONPITUUS)
	
	#Jos ohjelma käynnistyy ennen vuorokauden vaihtumista lisätään
	#varausjakson pituuteen 1 jotta saadaan oikea pvm
	else:
		tanaanPlus = date.today() + timedelta(days= VARAUSJAKSONPITUUS + 1)

	#tanaanPlus = date(2021, 4, 4)
	pvmMuotoiltu = tanaanPlus.strftime("%d" + erotin + "%m" + erotin + "%Y")
	return pvmMuotoiltu

def pvmLogManage(paivat):
	tanaanMiinus = date.today() - timedelta(days= paivat)
	return tanaanMiinus.strftime("%d.%m.%Y")

def cal_time(aika, isEndTime):
	if not(isEndTime):
		dateTimeObj = datetime.datetime.strptime(pvmTarkistus + aika, "%d.%m.%Y%H:%M")
		return dateTimeObj.strftime("%Y-%m-%dT%H:%M:%S")
	else:
		dateTimeObj = datetime.datetime.strptime(pvmTarkistus + aika, "%d.%m.%Y%H:%M")
		dateTimeObj = dateTimeObj + timedelta(hours=1)
		return dateTimeObj.strftime("%Y-%m-%dT%H:%M:%S")


#Koittaa ladata oikean päivämäärän varaussivun joko kunnes on yritetty haluttu määrä
#tai kunnes oikea päivämäärä on ladattu
def lataa_sivu():
	i = 0
	while i < YRITYKSET:
		driver.get("https://booking.koas.fi/koas/service/timetable/159/" + pvmOsoite)
		tanaan = driver.find_element_by_class_name("js-datepicker").text
		if tanaan == pvmTarkistus:
			print("Oikea pvm ladattiin")
			log.write("Oikea pvm ladattiin\n")
			return
		print("%s: Väärä pvm (" % pvmTarkistus + tanaan + "). Yritys " + str(i + 1))
		log.write("%s: Väärä pvm (" % pvmTarkistus + tanaan + "). Yritys " + str(i + 1)+"\n")
		time.sleep(SEKUNNIT)
		i += 1
	print("Oikeaa päivämäärää ei onnistuttu lataamaan. Sammutetaan ohjelma.")
	log.write("Oikeaa päivämäärää ei onnistuttu lataamaan. Sammutetaan ohjelma.\n")
	lopeta()



def tarkista_paiva():
	for x in LEPOPAIVAT:
		if driver.find_element_by_class_name("day-name").text == x:
			print("Tänään on lepopäivä. Vuoroja ei varattu.")
			log.write("Tänään on lepopäivä. Vuoroja ei varattu.\n")
			lopeta()

def varaa_vuorot():
	varattiinko = False
	liikaaVuoroja = False
	vuoro = VUORONAIKA
	paikka = 2
	startTime = None
	endTime = None
	kellonAika = None
	#Vastaa vuorojen selaamisesta
	while vuoro <= VUOROJENMAARA:
		x = 1
		kellonAika = driver.find_element_by_xpath("/html/body/main/div/div/div/div[2]/div/div/table/tbody/tr[" + str(vuoro) +"]/td[1]").text
		#Vastaa paikkojen selaamisesta vuoron sisällä
		while paikka <= PAIKKOJENMAARA + 1:
			
			try:
				#Koittaa etsiä Vapaa napin. Jos paikka varattu niin siirtyy except:iin
				vuoroElement = driver.find_element_by_xpath("/html/body/main/div/div/div/div[2]/div/div/table/tbody/tr[" + str(vuoro) +"]/td[" + str(paikka) + "]/a")
				print(pvmTarkistus + " " + kellonAika + " Paikka " + str(x) + ": Vapaa")
				log.write(pvmTarkistus + " " + kellonAika + " Paikka " + str(x) + ": Vapaa\n")
				vuoroElement.click()
				
				#Asettaa halutun nimen varaukseen
				nimi = driver.find_element_by_class_name("js-reservation-name")
				nimi.send_keys(VARAUSNIMI)

				#Painaa nappia jolla vuoro varataan
				varaanappi = driver.find_element_by_link_text("Varaa")
				varaanappi.click()
				
				try:
					liikaaVuorojaNappi = driver.find_element_by_class_name("ui-dialog-buttonset")
					liikaaVuorojaNappi.click()
					liikaaVuoroja = True

					print("Viikolla: " + viikkoStr + " on liika vuoroja. Vuoroa ei voitu varata.")
					log.write("Viikolla: " + viikkoStr + " on liika vuoroja. Vuoroa ei voitu varata.\n")
					break
				except:
					pass	
				print(pvmTarkistus + " " + kellonAika + " Paikka " + str(x) + ": Varattu onnistuneesti.")
				log.write(pvmTarkistus + " " + kellonAika + " Paikka " + str(x) + ": Varattu onnistuneesti.\n")
				if not(varattiinko):
					startTime = cal_time(kellonAika, False)
				endTime = cal_time(kellonAika, True)
				varattiinko = True
				#Lopettaa paikkoja selaava silmukan jotta varataan vain yksi paikka per vuoro
				break
			except:
				print(pvmTarkistus + " " + kellonAika + " Paikka " + str(x) + ": ei ole vapaa.")
				log.write(pvmTarkistus + " " + kellonAika + " Paikka " + str(x) + ": ei ole vapaa.\n")
			x += 1
			paikka += 1
		if liikaaVuoroja:
			break
		paikka = 2
		vuoro += 1
	if liikaaVuoroja:
		lopeta()
	if  not(varattiinko):
		print("Ei vapaita vuoroja")
		log.write("Ei vapaita vuoroja.\n")
		lopeta()
	add_event(startTime, endTime)
	print("Vuoroja varattiin!")
	log.write("Vuoroja varattiin!\n")
	lopeta()

def authenticate_google():
    creds = None
    if os.path.exists('./token.json'):
        creds = Credentials.from_authorized_user_file('./token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('./token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return service

def add_event(startT, endT):
	eventBody = {
	"summary": CAL_SUMMARY,
	"colorId": CAL_COLOR,
	"start": {
		"dateTime": startT,
        "timeZone": "Europe/Helsinki",
	},
	"end": {
		"dateTime": endT,
        "timeZone": "Europe/Helsinki",
	},
	"reminders": {
		"useDefault": False,
		"overrides": [
			{
			"method": "popup",
			"minutes": POPUP1
			},
			{
			"method": "popup",
			"minutes": POPUP2
			},
		],
	},
	}
	response = service.events().insert(calendarId="primary", body=eventBody).execute()


#Sammuttaa ohjelman ja tekee tarvittavat toimenpiteet
def lopeta():
	#Poistaa mahdolliset liian vanhat logitiedot
	pvmPoistaLogi = pvmLogManage(LOGIENSAILYTYS)
	if os.path.exists("%s/BBLogs/Log_%s.txt" % (LOGFILEPATH,pvmPoistaLogi)):
		os.remove("%s/BBLogs/Log_%s.txt" % (LOGFILEPATH,pvmPoistaLogi))
		print("%s päivän logi poistettiin." % pvmPoistaLogi)
		log.write("%s päivän logi poistettiin.\n" % pvmPoistaLogi)
	else:
		print("Ei poistettavaa logitiedostoa(%s)" % pvmPoistaLogi)
		log.write("Ei poistettavaa logitiedostoa(%s)\n" % pvmPoistaLogi)

	print("Sammutetaan...")
	log.write("Sammutetaan...\n")
	log.close()
	#Sammuttaa webdriverin ja ohjelman
	driver.quit()
	time.sleep(5)
	sys.exit()
	
#----------------------------------------------------------
#------Main------------------------------------------------
#----------------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/calendar"]
PATH = "/usr/lib/chromium-browser/chromedriver"
options = webdriver.ChromeOptions()
#options.add_argument("headless")
options.add_argument("window-size=1920x1080")
driver = webdriver.Chrome(PATH, options = options)

pvmOsoite = pvm("/")
pvmTarkistus = pvm(".")
viikkoObj = datetime.datetime.today() + timedelta(days=VARAUSJAKSONPITUUS)
viikkoStr = viikkoObj.strftime("%W")

#Logitiedostojen luonti
logs()

#Tunnistautuu googlelle
global service
service = authenticate_google()

timeNow = datetime.datetime.now()
timeStrNow = timeNow.strftime("%H:%M:%S")
log.write("aika ennen sleep: " + timeStrNow + "\n")

#Asettaa viiveen (s), koska cronissa voi asettaa vain minuutin tarkkuudella
time.sleep(40)

#Kirjautumissivu
driver.get("https://booking.koas.fi/koas/")

#Kirjaudutaan sisään
kirjautuminen()

timeNow = datetime.datetime.now()
timeStrNow = timeNow.strftime("%H:%M:%S")
log.write("Sivun päivitys aloitettiin: " + timeStrNow + "\n")
#Ladataan varaussivu
lataa_sivu()

#Tarkistaa onko kyseinen päivä lepopäivä
tarkista_paiva()

#Varataan vuorot
varaa_vuorot()