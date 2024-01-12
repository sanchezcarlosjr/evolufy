from evolufy import __version__

__author__ = "sanchezcarlosjr"
__copyright__ = "sanchezcarlosjr"
__license__ = "MIT"

from evolufy import setup_logging, _logger
from evolufy.webservice import WebService

# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.

import typer
from typing import Optional

app = typer.Typer()


@app.command()
def version():
    print(f"evolufy {__version__}")


@app.command()
def run_webapp(share=False):
    _logger.info("Starting webapp..")
    from evolufy.webapp import webapp
    webapp.launch(share)


@app.command()
def run_webservice():
    """
    The command initiates the webservice and maintains it in the background. Additionally,
    this command is used to update the service.
    """
    _logger.info("Starting webservice...")


def main(verbose: Optional[int] = typer.Option(0, '--verbose', '-v', count=True,
                                               help="Increase verbosity by augmenting the count of 'v's, and enhance "
                                                    "the total number of messages.")):
    setup_logging(verbose * 10)
    app()


def run():
    app()


if __name__ == "__main__":
    typer.run(app)
