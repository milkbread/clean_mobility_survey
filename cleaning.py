import pandas as pd
import numpy as np

from geopy.geocoders import Nominatim

location_to_clean = [
    ("Taubenheim", "Taubenheim (Klipphausen)"),
    ("Leuben", "Leuben - Schleinitz"),
    ("Polenz", "Polenz (Klipphausen)"),
    ("Scharfenberg", "Scharfenberg (Klipphausen)"),
    ("Steinbach", "Steinbach (Moritzburg)"),
    ("Siebeneichen", "Siebeneichen (Meißen)"),
    ("röhrdorf", "Röhrsdorf (Klipphausen)"),
    ("Lommatsch", "Lommatzsch"),
    ("stroichen", "Stroischen"),
    ("Ortsteil von Lommatzsch", "Lommatzsch"),
    ("Nossen OT Gruna", "Gruna (Nossen)"),
    ("Niderjahna", "Niederjahna"),
    ("Schmidewalde", "Schmiedewalde"),
    ("Niederau, Weinböhla", "Niederau (Meißen)"),
    ("Bahra gemeinde hirstein", "Bahra gemeinde hirschstein"),
    ("Meißen Mölln", "Meißen-Cölln"),
    ("Dira-zeren", "Diera-Zehren"),
    ("Luga", "Luga (Käbschütztal)"),
    ("1662", "Meißen"),
]

r_list = [
    ("15 min. ", ""),
    ("6-7", 6.5),
    ("6 und 15", (15 + 6) / 2),
    ("3-5", 4),
    ("14 und 12", 13),
    ("14 und 12", 13),
    ("4.292 6.253", (4.292 + 6.253) / 2),
    ("180m laut google maps (4", 0.18),
    ("7.5  und 11", (7.5 + 11) / 2),
    ("7.5/9.0", (7.5 + 9) / 2),
    ("450m 6min laufz", 0.45),
    ("10.5 und 9", (10.5 + 9) / 2),
    ("13-18", (13 + 18) / 2),
]

replace_counts = {
    "5x": "5",
    "4x": "4",
    "3x": "3",
    "2x": "2",
    "1x": "1",
    "0x": "",
    5.0: "5",
    4.0: "4",
    3.0: "3",
    2.0: "2",
    1.0: "1",
    0.0: "",
}
replace_starts = {
    "Ich starte immer vom gleichen Ort aus.": "gleicher Ort",
    "Ich habe zwei Wohnorte": "zwei Wohnorte",
}


class Cleaning:
    def __init__(self, filename):
        self.filename = filename

        # CSV-Datei einlesen
        self.df = pd.read_csv(
            filename,
            # "export_Schueler_bereinigt.csv",
            delimiter=";",
            encoding="utf-8",
        )

        self.app = Nominatim(user_agent="cleaning")

    def run(self):
        self.clean_columns()

        self.add_duration()

        # Neue Spalten 'lat' & 'lng' hinter 'Wohnort' einfügen,
        # wenn nicht vorhanden
        if "lat" not in self.df.columns:
            col_index = self.df.columns.get_loc("Wohnort")
            self.df.insert(col_index + 1, "lat", "")
            self.df.insert(col_index + 1, "lng", "")

        # Alle *x-Werte durch Zahlen ersetzen (z.B. 5x -> 5)
        self.df.replace(replace_counts, inplace=True)

        # Alle Startortangebaen durch kurze Werte ersetzen
        self.df.replace(replace_starts, inplace=True)

        # Timedelta berechnen und ausgeben
        for index, row in self.df.iterrows():
            try:

                self.df.at[index, "Alter"] = self.clean_age(row)
                self.df.at[index, "Schulweg (in km)"] = self.clean_distance(row)
                self.df.at[index, "Wohnort"] = self.clean_location(row, index)

            except Exception as e:
                print(e)

        # Bereinigte CSV-Datei speichern
        self.df.to_csv("data/cleaned_data.csv", index=False, sep=";", encoding="utf-8")

        print("Bereinigung abgeschlossen und Datei gespeichert.")

    def clean_columns(self):
        # Spalten "E-Mail" und "Name" entfernen
        self.df = self.df.drop(
            columns=["E-Mail", "Name", "Dauer (in min)"], errors="ignore"
        )

        # Spaltennamen umbenennen (für bessere Lesbarkeit)
        for col in self.df.columns:
            if "Mein Schulweg im Sommer... HINFAHRT." in col:
                _type = col.split("Mein Schulweg im Sommer... HINFAHRT.")[1]
                self.df.rename(columns={col: f"Hinweg(Sommer):{_type}"}, inplace=True)
            elif "Mein Schulweg im Sommer... Rückfahrt." in col:
                _type = col.split("Mein Schulweg im Sommer... Rückfahrt.")[1]
                self.df.rename(columns={col: f"Rückweg(Sommer):{_type}"}, inplace=True)
            elif "Mein Schulweg im Winter... Hinfahrt." in col:
                _type = col.split("Mein Schulweg im Winter... Hinfahrt.")[1]
                self.df.rename(columns={col: f"Hinweg(Winter):{_type}"}, inplace=True)
            elif "Mein Schulweg im Winter... Rückfahrt." in col:
                _type = col.split("Mein Schulweg im Winter... Rückfahrt.")[1]
                self.df.rename(columns={col: f"Rückweg(Winter):{_type}"}, inplace=True)
            elif (
                "Wie zufrieden bist Du mit dem Weg zur Schule im Hinblick auf...."
                in col
            ):
                _type = col.split(
                    "Wie zufrieden bist Du mit dem Weg zur Schule im Hinblick auf...."
                )[1]
                self.df.rename(columns={col: f"Zufriedenheit:{_type}"}, inplace=True)
            elif "In welchem Ort wohnst Du?" == col:
                self.df.rename(columns={col: "Wohnort"}, inplace=True)
            elif (
                "Wie lang ist Dein Weg zur Schule (einfache Strecke) in Kilometern?"
                == col
            ):
                self.df.rename(columns={col: "Schulweg (in km)"}, inplace=True)
            elif "Wie alt bist Du?" == col:
                self.df.rename(columns={col: "Alter"}, inplace=True)

    def add_duration(self):
        # Spalte "Dauer (in min)" hinzufügen, wenn nicht vorhanden
        date_format = "%d.%m.%Y %H:%M"
        self.df["Startzeit"] = pd.to_datetime(self.df["Startzeit"], format=date_format)
        self.df["Fertigstellungszeit"] = pd.to_datetime(
            self.df["Fertigstellungszeit"], format=date_format
        )

        # Index der Spalte 'Fertigstellungszeit' herausfinden
        col_index = self.df.columns.get_loc("Fertigstellungszeit")
        # Neue Spalte 'Dauer' hinter 'Fertigstellungszeit' einfügen
        self.df.insert(
            col_index + 1,
            "Dauer (in min)",
            self.df["Fertigstellungszeit"] - self.df["Startzeit"],
        )

        self.df["Dauer (in min)"] = self.df["Dauer (in min)"].dt.total_seconds() / 60

        # reset to initial date format
        self.df["Startzeit"] = self.df["Startzeit"].dt.strftime(date_format)
        self.df["Fertigstellungszeit"] = self.df["Fertigstellungszeit"].dt.strftime(
            date_format
        )

    def clean_location(self, row, index):
        _location = row["Wohnort"]
        # clean name
        for loc in location_to_clean:
            if loc[0] in _location:
                _location = loc[1]
        # get location
        if (row["lat"] == "" and row["lng"] == "") or (
            np.isnan(row["lat"]) or np.isnan(row["lng"])
        ):
            location = self.app.geocode(_location)
            if location:
                self.df.at[index, "lat"] = location.raw["lat"]
                self.df.at[index, "lng"] = location.raw["lon"]
            else:
                print(f"Location not found for {_location}")
        return _location

    def clean_distance(self, row):
        distance_ = str(row["Schulweg (in km)"])
        _distance = distance_
        _distance = _distance.strip()
        _distance = _distance.lower().strip("km").replace("km", "")
        _distance = _distance.lower().strip("meter")
        _distance = _distance.lower().strip("  (luftlinie)")
        _distance = _distance.lower().strip("ca.")
        _distance = _distance.lower().strip("kilo")
        _distance = _distance.lower().strip("kilm")
        _distance = _distance.lower().strip("luftlin")
        _distance = _distance.replace(",", ".")
        _distance = _distance.lstrip().rstrip()

        for r in r_list:
            if r[0] in _distance:
                _distance = _distance.replace(r[0], str(r[1]))

        distance = float(_distance)
        if distance > 100:
            distance = distance / 1000

        return round(distance, 2)

    def clean_age(self, row):
        _age = row["Alter"]
        if isinstance(_age, str):
            _age = _age.strip()
            _age = _age.strip("+")
            _age = _age.strip("über")
            if "aber" in _age:
                _age = _age.split("aber")[0]
            _age = _age.lower().strip("jahre")
            age = int(_age)
            return age
        return _age
