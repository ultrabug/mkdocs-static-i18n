from pathlib import PurePath

version = "1.3.0"


def is_relative_to(src_path, dest_path):
    try:
        return PurePath(src_path).is_relative_to(dest_path)
    except AttributeError:
        # python < 3.9 compat
        try:
            PurePath(src_path).relative_to(dest_path)
            return True
        except ValueError:
            return False
