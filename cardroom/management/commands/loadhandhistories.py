from argparse import ArgumentParser
from functools import partial
from glob import glob
from itertools import chain
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from pokerkit import HandHistory

from cardroom import models


class Command(BaseCommand):
    help = 'Installs the hand histories to the database.'

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            'pathnames',
            nargs='+',
            type=str,
            help='One or more pathnames',
        )

    def handle(self, *args: Any, **options: Any) -> None:
        pathnames = options['pathnames']
        count = 0

        for pathname in chain.from_iterable(
                map(partial(glob, recursive=True), pathnames),
        ):
            try:
                with open(pathname, 'rb') as file:
                    hh = HandHistory.load(file)
            except ValueError:
                raise CommandError(
                    f'failed to parse hand history file {repr(pathname)}',
                )

            models.HandHistory.dump(hh).save()

            count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Success: created {count} hand history models',
            ),
        )
