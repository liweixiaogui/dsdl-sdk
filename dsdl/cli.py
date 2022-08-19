import click

from dsdl import parse
from dsdl.tools import view


@click.group()
def cli():
    pass


# parser解析器的入口：用来解析yaml里面的模型和标签部分。
cli.add_command(parse)
cli.add_command(view)

if __name__ == "__main__":
    cli()
