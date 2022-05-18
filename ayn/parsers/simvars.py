import csv
from io import StringIO

from ayn.data_objects import SimVar, SimVars
from ayn.parsers.connections import parse_connections, dump_connections
from ayn.parsers.errors import CantWriteException


def parse_simvars(data: str) -> SimVars:
    s = StringIO(data)

    csvf = csv.reader(s)
    labels = next(csvf)
    simvars = []

    for row in csvf:
        active = row[0]
        if active != "#":
            continue

        assert len(row) == 28

        assert row[8] == "#"
        connections = row[9:28]
        separator_ix = connections.index("#")
        inputs = parse_connections(connections[:separator_ix])
        outputs = parse_connections(connections[separator_ix+1:])

        simvars.append(SimVar(
            name=row[1], zone=row[2], default=float(row[3]),
            min=float(row[4]), max=float(row[5]),
            emotion=row[6],
            icon=row[7],
            # row[8] is always "#"
            inputs=inputs, outputs=outputs,
        ))

    return SimVars(
        labels=labels,
        simvars=simvars,
    )


def dump_simvars(simvars: SimVars) -> str:
    s = StringIO()

    csvf = csv.writer(s, lineterminator="\n")
    csvf.writerow(simvars.labels)
    for simvar in simvars.simvars:
        row = [
            "#", simvar.name, simvar.zone, simvar.default,
            simvar.min, simvar.max,
            simvar.emotion, simvar.icon,
            "#", *dump_connections(28-9, simvar.inputs, simvar.outputs)
        ]
        if len(row) != 28:
            raise CantWriteException("can't write simvar {}: too many connections".format(simvar.name))

        csvf.writerow(row)

    return s.getvalue()