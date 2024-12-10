# Clean Mobility Survey

Dieses Projekt ermöglicht die Bereinigung der Umfragedaten zum Mobilitätsverhalten der FWS.

## Inhaltsverzeichnis

- [Installation](#installation)
- [Verwendung](#verwendung)
- [Dateien](#dateien)
- [Technologien](#technologien)
- [Lizenz](#lizenz)

## Installation

1. Klone das Repository:
    ```sh
    git clone https://github.com/dein-benutzername/clean_mobility_survey.git
    ```
2. Wechsle in das Projektverzeichnis:
    ```sh
    cd clean_mobility_survey
    ```
3. Erstelle eine virtuelle Python Umgebung:
    ```sh
    python3 -m venv venv
    ```
4. Aktiviere die virtuelle Umgebung:
    - Auf macOS/Linux:
        ```sh
        source venv/bin/activate
        ```
    - Auf Windows:
        ```sh
        .\venv\Scripts\activate
        ```
5. Installiere die Abhängigkeiten:
    ```sh
    pip install -r requirements.txt
    ```

## Verwendung

Das Skript [main.py](main.py) bietet verschiedene Befehle zur Bereinigung und zum Export der Umfragedaten. Hier sind die verfügbaren Befehle:

1. **clean**: Bereinigt die Daten.
    ```sh
    python main.py clean -i <input_file>
    ```

2. **export_coordinates**: Exportiert die Koordinaten als GeoJSON.
    ```sh
    python main.py export_coordinates -i <input_file>
    ```

3. **export_table**: Exportiert die Daten als HTML-Tabelle.
    ```sh
    python main.py export_table -i <input_file>
    ```

4. **run**: Führt die Bereinigung und den Export der Daten durch.
    ```sh
    python main.py run -i <input_file> -o <output_file> [--repeat]
    ```

## Dateien

- [index.html](docs/index.html): Startseite mit Links zur Karte und Tabelle sowie Download-Optionen.
- [map.html](docs/map.html): Zeigt eine Leaflet-Karte mit den Startorten der Umfrage.
- [table.html](docs/table.html): Zeigt die gereinigten Daten der Umfrage in einer DataTable.
- [cleaned_data.csv](data/cleaned_data.csv): Gereinigte Daten der Umfrage im CSV-Format.
- [coordinates.geojson](docs/coordinates.geojson): Koordinaten der Startorte im GeoJSON-Format.
- [main.py](main.py): Hauptskript mit Click-Befehlen zur Bereinigung und zum Export der Daten.


## Technologien

- [Python](https://www.python.org/)
- [Pandas](https://pandas.pydata.org/)
- [Leaflet](https://leafletjs.com/)
- [DataTables](https://datatables.net/)
- [Bootstrap](https://getbootstrap.com/)

## Lizenz

Dieses Projekt ist unter der Apache 2.0-Lizenz lizenziert. Siehe die [LICENSE](LICENSE)-Datei für weitere Details.
