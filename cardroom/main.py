from functools import partial
from sys import argv

from django.core.management import execute_from_command_line

main = partial(execute_from_command_line, argv)

if __name__ == '__main__':
    main()  # pragma: no cover
