import logging
import click

from cleaning import Cleaning
from export import Export

log = logging.getLogger(__name__)


@click.group()
@click.option("--debug/--no-debug", "-d", is_flag=True, default=False)
def main(debug):
    log_level = logging.DEBUG if debug else logging.INFO

    log_config = dict(
        level=log_level,
        format="%(asctime)s %(name)-10s %(levelname)-4s %(message)s",
    )
    logging.basicConfig(**log_config)
    logging.getLogger("").setLevel(log_level)


@main.command()
@click.option("-i", "--input_file", help="location of the input file")
def clean(input_file):
    Cleaning(input_file).run()


@main.command()
@click.option("-i", "--input_file", help="location of the input file")
def export_coordinates(input_file):
    Export(input_file).coordinates()


@main.command()
@click.option("-i", "--input_file", help="location of the input file")
def export_table(input_file):
    Export(input_file).table()

@main.command()
@click.option(
    "-i", "--input_file", help="location of the input file",
    show_default=True, default="./data/cleaned_data.csv")
def export_wordcloud(input_file):
    Export(input_file).wordcloud()

@main.command()
@click.option(
    "-i", "--input_file", help="location of the input file",
    show_default=True, default="./data/cleaned_data.csv")
def unique_locations(input_file):
    Export(input_file).unique_locations()

@main.command()
@click.option(
    "-i", "--input_file", help="location of the input file", show_default=True,
    default="./data/export_Schueler.csv")
@click.option(
    "-o", "--output_file", help="location of the output file", show_default=True,
    default="./data/cleaned_data.csv")
@click.option(
    "-r", "--repeat", is_flag=True,
    help="takes output file as input file and repeats cleaning for that"
    )

def run(input_file, output_file, repeat):
    if repeat:
        input_file = output_file
    Cleaning(input_file, output_file=output_file).run()
    Export(output_file).coordinates()
    Export(output_file).table()
    Export(output_file).wordcloud()
    Export(output_file).unique_locations()


if __name__ == "__main__":
    main()
