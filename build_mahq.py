#!/usr/bin/env python

import argparse
import logging
import os
import shutil
from pathlib import Path
from pprint import pformat

import pandas as pd
import yaml
from jinja2 import Environment, FileSystemLoader


def main(root_path='html', version='v0.0.1'):
    args = parse_options(version=version)
    set_log_config(args=args)
    logger = logging.getLogger(__name__)
    logger.debug('args:{0}{1}'.format(os.linesep, pformat(vars(args))))

    root_dir = Path(root_path)
    data_dir = Path(__file__).parent.joinpath('data')
    template_dir = Path(__file__).parent.joinpath('template')
    favicon_path = data_dir.joinpath('favicon.ico')
    lang_data = read_yml(path=str(data_dir.joinpath('lang.yml')))
    logger.debug('lang_data:{0}{1}'.format(os.linesep, lang_data))
    df_wl = pd.read_csv(
        str(data_dir.joinpath('whitelist.csv')), index_col='site'
    )
    logger.debug('df_wl:{0}{1}'.format(os.linesep, df_wl))

    if not root_dir.is_dir():
        print_log('Make a directory:\t{}'.format(root_dir))
        root_dir.mkdir()
    for s in ['en', 'ja']:
        p = root_dir.joinpath(s)
        if not p.is_dir():
            print_log('Make a directory:\t{}'.format(p))
            p.mkdir()
    print_log('Create favicon.ico:\t{}'.format(favicon_path))
    shutil.copyfile(favicon_path, str(root_dir.joinpath('favicon.ico')))
    render_html(
        template_name='index.html.j2', template_dir_path=str(template_dir),
        data=lang_data['en'], output_path=str(root_dir.joinpath('index.html'))
    )
    for s in ['en', 'ja']:
        render_html(
            template_name='lang_index.html.j2',
            template_dir_path=str(template_dir),
            data={
                'site_array_string': str(
                    df_wl.pipe(lambda d: d[d[s].astype(bool)].index.tolist())
                ),
                **lang_data[s]
            },
            output_path=str(root_dir.joinpath(s).joinpath('index.html'))
        )


def parse_options(version):
    parser = argparse.ArgumentParser(
        prog=Path(__file__).name, description='mahq HTML document builder'
    )
    parser.add_argument(
        '--version', action='version', version='%(prog)s {}'.format(version)
    )
    parser.add_mutually_exclusive_group()
    parser.add_argument(
        '--debug', dest='debug', action='store_true',
        help='Log with DEBUG level'
    )
    parser.add_argument(
        '--info', dest='info', action='store_true',
        help='Log with INFO level'
    )
    return parser.parse_args()


def set_log_config(args):
    if args.debug:
        lv = logging.DEBUG
    elif args.info:
        lv = logging.INFO
    else:
        lv = logging.WARNING
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S', level=lv
    )


def print_log(message):
    logger = logging.getLogger(__name__)
    logger.info(message)
    print('>>\t{}'.format(message), flush=True)


def read_yml(path):
    with open(path, 'r') as f:
        d = yaml.load(f, Loader=yaml.FullLoader)
    return d


def render_html(template_name, template_dir_path, data, output_path):
    print_log('Render a HTML file:\t{}'.format(output_path))
    with open(output_path, 'w') as f:
        f.write(
            Environment(
                loader=FileSystemLoader(template_dir_path, encoding='utf8')
            ).get_template(template_name).render(data)
        )


if __name__ == '__main__':
    main()
