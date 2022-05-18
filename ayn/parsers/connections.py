from typing import List

from ayn.data_objects import Connection


def parse_connections(lst: List[str]) -> List[Connection]:
    lst = [i for i in lst if i != ""]

    conns = []
    for function in lst:
        bits = function.split(",")
        if len(bits) == 2 or len(bits) == 3 and bits[2] == "":
            conns.append(Connection(node=bits[0], code=bits[1], turns=1))
        elif len(bits) == 3:
            conns.append(Connection(node=bits[0], code=bits[1], turns=int(bits[2])))
        else:
            assert("wrong number of bits: {} ({})".format(bits, function))

    return conns


def dump_connections(width: int, *lists: List[Connection]) -> List[str]:
    out = []
    for ix, l in enumerate(lists):
        if ix != 0:
            out.append("#")

        for i in l:
            if i.turns == 1:
                out.append("{},{}".format(i.node, i.code))
            else:
                out.append("{},{},{}".format(i.node, i.code, i.turns))

    while len(out) < width:
        out.append("")

    return out

