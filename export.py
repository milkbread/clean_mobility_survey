import pandas as pd
import numpy as np
import json


class Export:
    def __init__(self, filename):
        self.filename = filename

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
        with open("docs/coordinates.geojson", "w") as f:
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
            <title>CSV-Daten der Mobilitätesumfrage</title>
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
        with open("docs/table.html", "w") as f:
            f.write(html_content)
