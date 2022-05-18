import csv
from io import StringIO

from ayn.data_objects import Situation, Situations, Connection
from ayn.parsers.connections import parse_connections, dump_connections
from ayn.parsers.errors import CantWriteException


def parse_situations(data: str) -> Situations:
    s = StringIO(data)

    csvf = csv.reader(s)
    labels = next(csvf)
    situations = []

    for row in csvf:
        active = row[0]
        if active != "#":
            continue

        assert len(row) == 32

        connections = row[12:32]
        separator_ix = connections.index("#")
        inputs = parse_connections(connections[:separator_ix])
        outputs = parse_connections(connections[separator_ix+1:])

        situations.append(Situation(
            name=row[1], zone=row[2], prereq=row[3] or None, icon=row[4],
            positive=bool(int(row[5])),
            start_trigger=float(row[6]), stop_trigger=float(row[7]),
            cost=float(row[8]), cost_function=row[9],
            income=float(row[10]), income_function=row[11],
            inputs=inputs, outputs=outputs,
        ))

    return Situations(
        labels=labels,
        situations=situations
    )


def dump_situations(situations: Situations) -> str:
    s = StringIO()

    csvf = csv.writer(s, lineterminator="\n")
    csvf.writerow(situations.labels)
    for situation in situations.situations:
        row = [
            "#", situation.name, situation.zone, situation.prereq or "", situation.icon,
            int(situation.positive),
            situation.start_trigger, situation.stop_trigger,
            situation.cost, situation.cost_function,
            situation.income, situation.income_function,
            *dump_connections(32-12, situation.inputs, situation.outputs)
        ]
        if len(row) != 32:
            raise CantWriteException("can't write situation {}: too many connections".format(situation.name))

        csvf.writerow(row)

    return s.getvalue()
