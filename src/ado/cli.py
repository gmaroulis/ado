"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mado` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``ado.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``ado.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
from ado.state_machine_extractor import generate_state_machine_template

parser = argparse.ArgumentParser(description='Command description.')

parser.add_argument('names', metavar='NAME', nargs=argparse.ZERO_OR_MORE,
                    help="A name of something.")

parser.add_argument('-p', '--path', nargs=argparse.ZERO_OR_MORE, help='path to flow.py file')
parser.add_argument('-n', '--name', nargs=argparse.ZERO_OR_MORE, help='name of the state machine')
parser.add_argument('-aws', '--aws', nargs=argparse.ZERO_OR_MORE, help='aws account number')


def main(args=None):
    """Generate the state machine."""
    args = parser.parse_args(args=args)
    generate_state_machine_template(args)
