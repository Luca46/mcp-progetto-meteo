# Importazione delle librerie necessarie
from datetime import datetime
from mcp.server.fastmcp import FastMCP # Framework MCP per creare tool interattivi
import requests # Per effettuare richieste HTTP
import re # Per gestire e visualizzare messaggi di log
import logging
import sys
import os # Per leggere variabili d'ambiente
from pydantic import BaseModel, Field, ValidationError
from typing import List

# Inizializzazione dell'applicazione MCP
mcp = FastMCP("My App Meteo")

# Recupero l'indirizzo email da una variabile d'ambiente necessaria per l'header HTTP
email = os.getenv("EMAIL")
if not email:
    raise ValueError("La variabile d'ambiente 'EMAIL' è obbligatoria.")

# Header da usare nelle richieste HTTP per identificare l'app
headers = {
    "User-Agent": f"MyAppName/1.0 ({email})"
}

# Configuro il livello di logging su WARNING, mostrando solo messaggi di avviso o errore
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s') 
# %(levelname)s Inserisci il livello del messaggio (es. WARNING, ERROR, INFO) come stringa (s).
# %(message)s Inserisci il testo vero e proprio del messaggio di log.

# Modello per l'input dell'utente
class InputModel(BaseModel):
    citta: str = Field(min_length=3, pattern=r"^[a-zA-Z\sàèéìòùÀÈÉÌÒÙ']+$")
    #citta: deve essere una stringa di almeno 3 lettere, composta solo da lettere, spazi, accenti e apostrofi.
    past_days: int = Field(ge=0) #ge=0 significa "greater than or equal to 0"
    # past_days: deve essere un intero maggiore o uguale a 0 (0 per temperatura attuale).

# Modello per i dati delle coordinate
class CoordinateModel(BaseModel):
    lat: float
    lon: float

# Modello per i dati meteo orari
class MeteoModel(BaseModel):
    temperature_2m: List[float]
    time: List[str]

# Definisco della funzione MCP che restituisce la tempratura di una città
@mcp.tool()
def trova_temperatura(citta: str, past_days: int = 0):
    """First of all look up the latitude and longitude of a city. Then, get the current temperature."""
    # Controllo sull'input ci non devono esserci caratteri specialie il nome deve essere abbastanza lungo
    try:
        #validazione input
        try:
            input_validato = InputModel(citta=citta, past_days=past_days)
        except ValidationError as e:
            logging.warning("Errore input: %s", e)
            return {"errore": "Input non valido: " + e.errors()[0]['msg']}

        # Richiesta per ottenere le coordinate geografiche della città
        url_base_cerca_citta = "https://nominatim.openstreetmap.org/search"
        r = requests.get(
            url_base_cerca_citta,
            params={
                "q": citta,
                "format": "json",
                "accept-language": "it",
                "countrycodes": "it"
            }, headers=headers
        )
        # Controllo sulla risposta: errore di rete o città non trovata
        if r.status_code != 200 or not r.json():
            logging.warning("Errore nella richiesta o città non trovata: %s", citta)
            return {"errore": "Errore nella richiesta o città non trovata."}
        
        try:
            raw_coord = r.json()[0]
            coordinate = CoordinateModel(lat=float(raw_coord['lat']), lon=float(raw_coord['lon']))
        except (KeyError, IndexError, ValidationError) as e:
            logging.warning("Errore parsing coordinate: %s", str(e))
            return {"errore": "Errore nel recupero delle coordinate."}

        # Costruzione della richiesta per l'API Open-Meteo per ottenere i dati meteo
        url_base_meteo = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": coordinate.lat,
            "longitude": coordinate.lon,
            "current_weather": True,
            "timezone": "Europe/Rome",
            "past_days": input_validato.past_days, # Numero di giorni passati da includere
            "hourly": "temperature_2m" # Richiede i dati orari di temperatura
        }
           # Richiesta HTTP all’API meteo
        response = requests.get(url_base_meteo, params=params)
        if response.status_code != 200:
            logging.warning("Errore nella richiesta meteo per: %s", input_validato.citta)
            return {"errore": "Errore nella richiesta meteo."}

        data = response.json()
         # Caso in cui non si richiedano giorni passati: restituisce la temperatura attuale
        if input_validato.past_days == 0:
            try:
                temperatura_attuale = data['current_weather']['temperature']
                return f"La temperatura attuale a {input_validato.citta} è di {temperatura_attuale}°C"
            except KeyError:
                return {"errore": "Temperatura attuale non disponibile."}

         # Estrae le temperature orarie e i relativi timestamp
        try:
            meteo_dati = MeteoModel(**data['hourly'])
        except (ValidationError, KeyError) as e:
            logging.warning("Errore parsing dati meteo: %s", str(e))
            return {"errore": "Errore nel recupero dei dati meteo."}

        # Raggruppa le temperature per giorno (formato 'yyyy-mm-dd')
        
        temperature_orarie = meteo_dati.temperature_2m
        orari = meteo_dati.time

        temperature_per_giorno = {}
        for i in range(len(orari)):
            orario = orari[i]
            temperatura = temperature_orarie[i]
            giorno = orario[:10]  # Estrai la parte yyyy-mm-dd
            
            
            if giorno not in temperature_per_giorno:
                temperature_per_giorno[giorno] = []
                
            temperature_per_giorno[giorno].append(temperatura)
        
        # Calcola la media giornaliera per ogni giorno
        medie_giornaliere = []
        for giorno in temperature_per_giorno:
            temperature = temperature_per_giorno[giorno]
            media_giornaliera = sum(temperature) / len(temperature)
            medie_giornaliere.append(media_giornaliera)

        # Calcola la media totale
        media_totale = sum(medie_giornaliere) / len(medie_giornaliere)

        return f"La temperatura media degli ultimi {past_days} giorni a {citta} è di {round(media_totale, 1)}°C"

    except Exception:
        # Gestione generica di errori imprevisti
        logging.warning("Errore generico per: %s", citta)
        return {"errore": "Si è verificato un errore."}