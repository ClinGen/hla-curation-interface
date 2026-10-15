"""Lists every database backup, including those under prefixes like daily/."""

from dbbackup.storage import get_storage
from django.core.files.storage import Storage
from django.core.management.base import BaseCommand


def find_backups(storage: Storage, directory: str = "") -> list[str]:
    """Find every backup in a storage, searching its directories too.

    django-dbbackup's listbackups only looks at the top level, but our backups live
    under prefixes like daily/ and pre-deployment/.

    Args:
        storage: The Django storage that holds the backups.
        directory: The directory to search, relative to the storage's root.

    Returns:
        The backups' names, relative to the storage's root, without .metadata files.
    """
    subdirectories, files = storage.listdir(directory)
    prefix = f"{directory}/" if directory else ""
    names = [prefix + name for name in files if not name.endswith(".metadata")]
    for subdirectory in subdirectories:
        names += find_backups(storage, prefix + subdirectory)
    return names


class Command(BaseCommand):
    help = "List every database backup, oldest first, with the name to restore it by."

    def handle(self, *_args: object, **_options: object) -> None:
        """Print each backup's modification time and name, oldest first."""
        storage = get_storage().storage
        backups = sorted(
            (storage.get_modified_time(name), name) for name in find_backups(storage)
        )
        if not backups:
            self.stdout.write("No backups found.")
        for modified, name in backups:
            self.stdout.write(f"{modified:%Y-%m-%d %H:%M %Z}  {name}")
