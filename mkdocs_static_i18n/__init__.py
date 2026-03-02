from pathlib import PurePath

version = "1.3.1"


def is_relative_to(src_path, *all_dirs):
    is_relative = False
    for path in all_dirs:
        try:
            is_relative ^= PurePath(src_path).is_relative_to(path)
        except AttributeError:
            # python < 3.9 compat
            try:
                PurePath(src_path).relative_to(path)
                is_relative ^= True
            except ValueError:
                pass
    return is_relative
