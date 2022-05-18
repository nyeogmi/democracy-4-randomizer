import csv
from io import StringIO

from ayn.data_objects import Policy, Policies
from ayn.parsers.connections import parse_connections, dump_connections
from ayn.parsers.errors import CantWriteException


def parse_policies(data: str) -> Policies:
    s = StringIO(data)

    csvf = csv.reader(s)
    labels = next(csvf)
    policies = []

    for row in csvf:
        active = row[0]
        if active != "#":
            continue

        assert len(row) == 39
        assert row[21] == "#Effects"
        connections = row[22:39]
        outputs = parse_connections(connections)

        policies.append(Policy(
            name=row[1],
            slider=row[2],
            flags=row[3],
            opposites=row[4],
            introduce=int(row[5]),
            cancel=int(row[6]),
            raise_=int(row[7]),
            lower=int(row[8]),
            department=row[9],
            prereqs=row[10],
            min_cost=float(row[11]),
            max_cost=float(row[12]),
            cost_function=row[13],
            cost_multiplier=row[14],
            implementation=int(row[15]),
            min_income=float(row[16]),
            max_income=float(row[17]),
            income_function=row[18],
            income_multiplier=row[19],
            nationalization_gdp_percentage=float(row[20]) if row[20] else 0.0,
            outputs=outputs,
        ))

    return Policies(
        labels=labels,
        policies=policies
    )


def dump_policies(policies: Policies) -> str:
    s = StringIO()

    csvf = csv.writer(s, lineterminator="\n")
    csvf.writerow(policies.labels)
    for policy in policies.policies:
        row = [
            "#", policy.name, policy.slider, policy.flags, policy.opposites,
            policy.introduce, policy.cancel, policy.raise_, policy.lower,
            policy.department, policy.prereqs, policy.min_cost, policy.max_cost,
            policy.cost_function, policy.cost_multiplier, policy.implementation,
            policy.min_income, policy.max_income, policy.income_function, policy.income_multiplier,
            policy.nationalization_gdp_percentage if policy.nationalization_gdp_percentage != 0.0 else "",
            "#Effects", *dump_connections(39-22, policy.outputs)
        ]
        if len(row) != 39:
            raise CantWriteException("can't write policy {}: too many connections".format(policy.name))

        csvf.writerow(row)

    return s.getvalue()