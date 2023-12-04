"""Build static HTML site from directory of HTML templates and plain files."""
from pathlib import Path
import json
import sys
import shutil
import click
import jinja2


def get_data(path):
    """Get data from the json config file."""
    config_filename = path.joinpath("config.json")
    if not config_filename.is_file():
        print(f'Error: \'{config_filename}\' not found.')
        sys.exit(1)
    with config_filename.open() as config_file:
        try:
            return json.load(config_file)
        except json.decoder.JSONDecodeError as err:
            sys.exit(f"Error: '{config_filename}'\n{err})")


@click.command()
@click.argument("input_dir", nargs=1, type=click.Path(exists=True))
@click.option("-o", "--output",
              type=(click.Path(exists=False)), help='Output directory.')
@click.option("-v", "--verbose", is_flag=True, help='Print more output.')
def main(input_dir, output, verbose):
    """Templated static website generator."""
    # get templates
    path = Path(input_dir)
    # load json data
    data = get_data(path)
    # define the output directory
    out_dir = ""
    if output is None:
        out_dir = Path(input_dir)/Path("html")
    else:
        out_dir = Path(output)
    sample = input_dir/Path('static/')
    try:
        if sample.is_dir():
            shutil.copytree(sample/'.', out_dir, copy_function=shutil.copy)
            if verbose:
                print(f'Copied {sample} -> {out_dir}')
        else:
            out_dir.mkdir()
    except FileExistsError:
        if output is None:
            print("Error: 'html' already exists.")
        else:
            print(f'Error: \'{output}\' already exists.')
        sys.exit(1)
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(path)+"/templates/"),
        autoescape=jinja2.select_autoescape(['html', 'xml']),)
    for info in data:
        try:
            template = template_env.get_template(info["template"])
        except jinja2.exceptions.TemplateError as err:
            sys.exit(f"Error: '{info['template']}'\n{err})")
        access = Path(out_dir/Path(info['url'].lstrip("/")))
        if not access.is_dir():
            access.mkdir(parents=True)
        with open(access/Path('index.html'),
                  'w', encoding="utf-8") as file:
            file.write(template.render(info['context']))
        if verbose:
            print(f"Rendered {info['template']}", "->",
                  f"{access/Path('index.html')}")


if __name__ == "__main__":
    main()
