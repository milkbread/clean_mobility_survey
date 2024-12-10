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
        df = self.df
        # Spaltennamen umbenennen (für bessere Lesbarkeit)
        for col in df.columns:
            if "Mein Schulweg im Sommer... HINFAHRT." in col:
                _type = col.split("Mein Schulweg im Sommer... HINFAHRT.")[1]
                df.rename(columns={col: f"Hinweg(Sommer):{_type}"}, inplace=True)
            elif "Mein Schulweg im Sommer... Rückfahrt." in col:
                _type = col.split("Mein Schulweg im Sommer... Rückfahrt.")[1]
                df.rename(columns={col: f"Rückweg(Sommer):{_type}"}, inplace=True)
            elif "Mein Schulweg im Winter... Hinfahrt." in col:
                _type = col.split("Mein Schulweg im Winter... Hinfahrt.")[1]
                df.rename(columns={col: f"Hinweg(Winter):{_type}"}, inplace=True)
            elif "Mein Schulweg im Winter... Rückfahrt." in col:
                _type = col.split("Mein Schulweg im Winter... Rückfahrt.")[1]
                df.rename(columns={col: f"Rückweg(Winter):{_type}"}, inplace=True)
            elif (
                "Wie zufrieden bist Du mit dem Weg zur Schule im Hinblick auf...."
                in col
            ):
                _type = col.split(
                    "Wie zufrieden bist Du mit dem Weg zur Schule im Hinblick auf...."
                )[1]
                df.rename(columns={col: f"Zufriedenheit:{_type}"}, inplace=True)
            elif "In welchem Ort wohnst Du?" == col:
                df.rename(columns={col: "Wohnort"}, inplace=True)
            elif (
                "Wie lang ist Dein Weg zur Schule (einfache Strecke) in Kilometern?"
                == col
            ):
                df.rename(columns={col: "Schulweg (in km)"}, inplace=True)
            # else:
            #     print(col)

        if "Dauer (in min)" not in df.columns:
            date_format = "%d.%m.%Y %H:%M"
            df["Startzeit"] = pd.to_datetime(
                df["Startzeit"], format=date_format
            ).dt.strftime(date_format)
            df["Fertigstellungszeit"] = pd.to_datetime(
                df["Fertigstellungszeit"], format=date_format
            ).dt.strftime(date_format)

            # Index der Spalte 'Fertigstellungszeit' herausfinden
            col_index = df.columns.get_loc("Fertigstellungszeit")
            # Neue Spalte 'Dauer' hinter 'Fertigstellungszeit' einfügen
            df.insert(col_index + 1, "Dauer (in min)", "")

        if "lat" not in df.columns:
            # Neue Spalte 'location' hinter 'Wohnort' einfügen
            col_index = df.columns.get_loc("Wohnort")
            df.insert(col_index + 1, "lat", "")
            df.insert(col_index + 1, "lng", "")

        # Timedelta berechnen und ausgeben
        for index, row in df.iterrows():
            try:

                df.at[index, "Wie alt bist Du?"] = self.clean_age(
                    row["Wie alt bist Du?"]
                )
                df.at[index, "Schulweg (in km)"] = self.clean_distance(
                    row["Schulweg (in km)"]
                )
                df.at[index, "Wohnort"] = self.clean_location(row, index)

            except Exception as e:
                print(e)

        # Bereinigte CSV-Datei speichern
        df.to_csv("data/cleaned_data.csv", index=False, sep=";", encoding="utf-8")

        print("Bereinigung abgeschlossen und Datei gespeichert.")

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

    def clean_distance(self, distance_):
        if isinstance(distance_, str):
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
            if distance > 100:
                print(_distance, distance_)
            return distance
        return distance_

    def clean_age(self, _age):
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