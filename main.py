from ayn.entry_point import main, prepare
import pathlib
import random

DEMOCRACY_4_PATHS = [
    r"C:\Program Files\Steam\steamapps\common\Democracy 4\data\simulation",
    r"C:\Program Files (x86)\Steam\steamapps\common\Democracy 4\data\simulation",
    # Did I miss your path? Go on GitHub and create an issue!
]


def command_line_main(argv):
    print("finding Democracy 4")
    for i in DEMOCRACY_4_PATHS:
        if pathlib.Path(i).exists():
            path = i
            print("... found! ({})".format(path))
            break
    else:
        print("... couldn't find Democracy 4! Find it yourself, then make a GitHub issue.")
        return

    prepare(path)

    print("finding seed")
    if len(argv) == 1:
        print("... not specified: generating one")
        seed = random.randint(0, 1000**5)
        print("... got {}!".format(seed))
    else:
        try:
            seed = -1 if argv[1].lower() == "reset" else int(argv[1])
        except ValueError:
            print("... formatted wrong. ({!r}); should be one integer!".format(argv[1]))
            return

        print("... saw {}!".format(seed))
    main(seed, ["output", path])


if __name__ == '__main__':
    import sys
    command_line_main(sys.argv)
