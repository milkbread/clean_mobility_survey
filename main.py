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
@click.option("-f", "--filename", help="name of the input file")
def clean(filename):
    Cleaning(filename).run()


@main.command()
@click.option("-f", "--filename", help="name of the input file")
def export_coordinates(filename):
    Export(filename).coordinates()


@main.command()
@click.option("-f", "--filename", help="name of the input file")
def export_table(filename):
    Export(filename).table()


if __name__ == "__main__":
    main()
