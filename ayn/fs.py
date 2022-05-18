from typing import Dict
from pathlib import Path


class Fs(object):
    def __init__(self):
        self.files: Dict[Path, str] = {}

    def include(self, path, glob):
        base = Path(path)
        for filename in base.glob(glob):
            if filename.is_file():
                self.files[filename.relative_to(base)] = filename.read_text()

    def export(self, path):
        base = Path(path)
        for filename, value in self.files.items():
            output = base.joinpath(filename)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(value)

    def __getitem__(self, fname):
        return self.files[Path(fname)]

    def __setitem__(self, fname, value):
        path = Path(fname)
        assert not path.is_absolute()
        self.files[Path(fname)] = value

    def __delitem__(self, fname):
        del self.files[Path(fname)]
