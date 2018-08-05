# coding=utf-8
"""
USAGE:
  jpk-fa-cli.py --seller SELLER --invoice INVOICE --output OUTPUT

Options:
  --seller SELLER  File with seller data see ``seller.yml`` for example
  --invoice INVOICE  File with invoice data see ``invoice1.yml`` for example
  --output OUTPUT  Output file

"""
import pathlib

import docopt

from jpk_fa.utils import render_from_source_file

if __name__ == '__main__':
  arguments = docopt.docopt(__doc__)
  print(arguments)

  with pathlib.Path(arguments['--output']).open('w') as f:
    f.write(render_from_source_file(
      pathlib.Path(arguments['--seller']),
      pathlib.Path(arguments['--invoice'])
    ))

