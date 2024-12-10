import pandas as pd
import numpy as np
import json


class Coordinates:
    def __init__(self, filename):
        self.filename = filename

        # CSV-Datei einlesen
        self.df = pd.read_csv(
            filename,
            # "export_Schueler_bereinigt.csv",
            delimiter=";",
            encoding="utf-8",
        )

    def run(self):
        df = self.df
        features = []
        for index, row in df.iterrows():
            if not (np.isnan(row["lat"]) or np.isnan(row["lng"])):
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [row["lng"], row["lat"]],
                    },
                    "properties": {"Wohnort": row["Wohnort"]},
                }
                features.append(feature)

        geojson = {"type": "FeatureCollection", "features": features}

        # GeoJSON-Datei speichern
        with open("pages/coordinates.geojson", "w") as f:
            f.write("const geojson = ")
            json.dump(geojson, f)
