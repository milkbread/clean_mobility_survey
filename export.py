import logging
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import nltk
from nltk.corpus import stopwords

from wordcloud import WordCloud

log = logging.getLogger(__name__)

class Export:
    def __init__(self, filename, type="pupils"):
        self.filename = filename
        self.type = type

        # CSV-Datei einlesen
        self.df = pd.read_csv(
            filename,
            # "export_Schueler_bereinigt.csv",
            delimiter=";",
            encoding="utf-8",
        )

    def coordinates(self):
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
        with open(f"docs/coordinates-{self.type}.geojson", "w") as f:
            f.write("const geojson = ")
            json.dump(geojson, f)

    def table(self):
        # CSV in HTML-Tabelle umwandeln
        html_table = self.df.to_html(
            index=False,
            classes="display",
            table_id="mobility_survey",
            decimal=",",
            na_rep="-",
        )

        # HTML-Datei erstellen
        html_content = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>FWS Mobilitätsumfrage</title>
            <link rel="stylesheet" href="https://cdn.datatables.net/2.1.8/css/dataTables.dataTables.min.css">
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script src="https://cdn.datatables.net/2.1.8/js/dataTables.min.js"></script>
            <style>
                body, html {{
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }}
                .dataTables_wrapper {{
                    height: 100vh;
                    overflow-y: auto;
                }}
                table#mobility_survey {{
                    width: 100%;
                }}
            </style>
            <script>
                $(document).ready(function() {{
                    table = new DataTable('#mobility_survey');

                }});
            </script>
        </head>
        <body>
            {html_table}
        </body>
        </html>
        """

        # HTML-Datei speichern
        with open(f"docs/table-{self.type}.html", "w") as f:
            f.write(html_content)

    def wordcloud(self):

        nltk.download('stopwords')
        # Text aus der Spalte "Was ich sonst noch hinzufügen möchte (Anregungen und Anmerkungen)" extrahieren
        text = ' '.join(self.df['Was ich sonst noch hinzufügen möchte (Anregungen und Anmerkungen)'].dropna().astype(str))

        # Stopwords definieren
        stop_words = set(stopwords.words('german'))

        # Wordcloud generieren
        wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=stop_words).generate(text)

        # Wordcloud als Bild speichern
        wordcloud.to_file(f'docs/wordcloud-{self.type}.png')

        # Optional: Wordcloud anzeigen
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')

    def unique_locations(self):
        # Eindeutige Wohnorte extrahieren
        unique_locations = self.df.dropna(subset=['Wohnort', 'lat'])
        unique_locations = self.df['Wohnort'].dropna().apply(lambda x: x.rstrip()).unique()

        # DataFrame mit eindeutigen Wohnorten erstellen
        unique_locations_df = pd.DataFrame(unique_locations, columns=['Wohnort'])

        unique_locations_df = unique_locations_df.sort_values(by='Wohnort')
        unique_locations_df.insert(1, "Cluster", "")

        # Neue CSV-Datei speichern
        unique_locations_df.to_csv(f'data/unique_locations-{self.type}.csv', index=False, sep=';')