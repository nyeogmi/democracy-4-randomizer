from dataclasses import dataclass
from pathlib import Path

from .data_objects import Policies, Situations, SimVars
from .fs import Fs
from .parsers.errors import CantWriteException
from .parsers.policies import parse_policies, dump_policies
from .parsers.simvars import parse_simvars, dump_simvars
from .parsers.situations import parse_situations, dump_situations


import random


def prepare(path):
    print("finding simulator data")
    if Path("original").exists():
        print("... simulator data found!")
    else:
        print("cloning Democracy 4 simulator data to original/")
        print("(if you have already run the randomizer, your seeds will behave differently from everyone else's)")

        fs = Fs()
        fs.include(path, "*.csv")
        fs.export("original")

        print("... cloned!")


def main(seed, output):
    fs = Fs()
    fs.include("original", "*.csv")

    print("running self test.")
    policies = parse_policies(fs["policies.csv"])
    situations = parse_situations(fs["situations.csv"])
    simvars = parse_simvars(fs["simulation.csv"])

    assert parse_policies(dump_policies(policies)) == policies
    assert parse_situations(dump_situations(situations)) == situations
    assert parse_simvars(dump_simvars(simvars)) == simvars
    print("... passed!")

    if seed == -1:
        print("... not randomizing (seed == -1; \"reset\")")
    else:
        while True:
            print("trying seed: {}".format(seed))
            policies = parse_policies(fs["policies.csv"])
            situations = parse_situations(fs["situations.csv"])
            simvars = parse_simvars(fs["simulation.csv"])

            randomize_model(
                seed, policies, situations, simvars,
                # TODO: Enable this to be controlled externally
                CrossPollinate(mix_simvar_situation=False, mix_good_bad=True)
            )

            try:
                policies_csv = dump_policies(policies)
                situations_csv = dump_situations(situations)
                simvars_csv = dump_simvars(simvars)
                print("... worked!")
                break

            except CantWriteException as cwe:
                print("... couldn't write: {}".format(cwe))
                seed += 1

        fs["policies.csv"] = policies_csv
        fs["situations.csv"] = situations_csv
        fs["simvars.csv"] = simvars_csv

    print("writing to disk")
    for o in output:
        fs.export(o)
        print("... written! ({})".format(o))


@dataclass
class CrossPollinate(object):
    mix_good_bad: bool
    mix_simvar_situation: bool


def randomize_model(
    seed: int,
    policies: Policies,
    situations: Situations, simvars: SimVars,
    cross_pollinate: CrossPollinate
):
    rng = random.Random(seed)

    # load all the policies etc
    n_policy_outputs = CPQ()

    policy_outputs = CPQ()

    n_simvar_inputs_good = CPQ()
    n_simvar_inputs_bad = CPQ()

    n_simvar_outputs_good = CPQ()
    n_simvar_outputs_bad = CPQ()

    simvar_inputs_good = CPQ()
    simvar_inputs_bad = CPQ()

    simvar_outputs_good = CPQ()
    simvar_outputs_bad = CPQ()

    n_situation_inputs_good = CPQ()
    n_situation_inputs_bad = CPQ()

    n_situation_outputs_good = CPQ()
    n_situation_outputs_bad = CPQ()

    situation_inputs_good = CPQ()
    situation_inputs_bad = CPQ()

    situation_outputs_good = CPQ()
    situation_outputs_bad = CPQ()

    policy_costs = CPQ()
    policy_incomes = CPQ()

    for p in policies.policies:
        n_policy_outputs.append(len(p.outputs))

        for o in p.outputs:
            policy_outputs.append(o)

        policy_costs.append((p.min_cost, p.max_cost, p.cost_function, p.cost_multiplier))
        policy_incomes.append((p.min_income, p.max_income, p.income_function, p.income_multiplier))

    for s in simvars.simvars:
        n_inputs, n_outputs, inputs, outputs = (
            (n_simvar_inputs_good, n_simvar_outputs_good, simvar_inputs_good, simvar_outputs_good) if "GOOD" in s.emotion else
            (n_simvar_inputs_bad, n_simvar_outputs_bad, simvar_inputs_bad, simvar_outputs_bad)
        )

        n_inputs.append(len(s.inputs))
        n_outputs.append(len(s.outputs))

        for i in s.inputs:
            inputs.append(i)

        for o in s.outputs:
            outputs.append(o)

    for s in situations.situations:
        n_inputs, n_outputs, inputs, outputs = (
            (n_situation_inputs_good, n_situation_outputs_good, situation_inputs_good, situation_outputs_good) if s.positive else
            (n_situation_inputs_bad, n_situation_outputs_bad, situation_inputs_bad, situation_outputs_bad)
        )

        n_inputs.append(len(s.inputs))
        n_outputs.append(len(s.outputs))

        for i in s.inputs:
            inputs.append(i)

        for o in s.outputs:
            outputs.append(o)

    # cross-pollinate
    if cross_pollinate.mix_good_bad:
        n_simvar_inputs_good.mix(n_simvar_inputs_bad),
        n_simvar_outputs_good.mix(n_simvar_outputs_bad),
        simvar_inputs_good.mix(simvar_inputs_bad),
        simvar_outputs_good.mix(simvar_outputs_bad),
        n_situation_inputs_good.mix(n_situation_inputs_bad),
        n_situation_outputs_good.mix(n_situation_outputs_bad),
        situation_inputs_good.mix(situation_inputs_bad),
        situation_outputs_good.mix(situation_outputs_bad),

    if cross_pollinate.mix_simvar_situation:
        n_simvar_inputs_good.mix(n_situation_inputs_good)
        n_simvar_inputs_bad.mix(n_situation_inputs_bad)
        n_simvar_outputs_good.mix(n_situation_outputs_good)
        n_simvar_outputs_bad.mix(n_situation_outputs_bad)
        simvar_inputs_good.mix(situation_inputs_good)
        simvar_inputs_bad.mix(situation_inputs_bad)
        simvar_outputs_good.mix(situation_outputs_good)
        simvar_outputs_bad.mix(situation_outputs_bad)

    # now scramble!!!
    for i in [
        n_policy_outputs,
        policy_outputs,
        n_simvar_inputs_good, n_simvar_inputs_bad,
        n_simvar_outputs_good, n_simvar_outputs_bad,
        simvar_inputs_good, simvar_inputs_bad,
        simvar_outputs_good, simvar_outputs_bad,
        n_situation_inputs_good, n_situation_inputs_bad,
        n_situation_outputs_good, n_situation_outputs_bad,
        situation_inputs_good, situation_inputs_bad,
        situation_outputs_good, situation_outputs_bad,
        policy_costs, policy_incomes,
    ]:
        i.shuffle(rng)

    # now reassign
    for p in policies.policies:
        my_n_outputs = n_policy_outputs.pop()

        p.outputs = [policy_outputs.pop() for _ in range(my_n_outputs)]

        p.min_cost, p.max_cost, p.cost_function, p.cost_multiplier = policy_costs.pop()
        p.min_income, p.max_income, p.income_function, p.income_multiplier = policy_incomes.pop()

    for s in simvars.simvars:
        n_inputs, n_outputs, inputs, outputs = (
            (n_simvar_inputs_good, n_simvar_outputs_good, simvar_inputs_good, simvar_outputs_good) if "GOOD" in s.emotion else
            (n_simvar_inputs_bad, n_simvar_outputs_bad, simvar_inputs_bad, simvar_outputs_bad)
        )

        my_n_inputs = n_inputs.pop()
        my_n_outputs = n_outputs.pop()

        s.inputs = [inputs.pop() for _ in range(my_n_inputs)]
        s.outputs = [outputs.pop() for _ in range(my_n_outputs)]

    for s in situations.situations:
        n_inputs, n_outputs, inputs, outputs = (
            (n_situation_inputs_good, n_situation_outputs_good, situation_inputs_good, situation_outputs_good) if s.positive else
            (n_situation_inputs_bad, n_situation_outputs_bad, situation_inputs_bad, situation_outputs_bad)
        )

        my_n_inputs = n_inputs.pop()
        my_n_outputs = n_outputs.pop()

        s.inputs = [inputs.pop() for _ in range(my_n_inputs)]
        s.outputs = [outputs.pop() for _ in range(my_n_outputs)]


class CPQ(object):  # "cross-pollinate queue"
    def __init__(self):
        self.resolve = None
        self.queue = []

    def append(self, x):
        if self.resolve:
            self.resolve.append(x)
            return
        self.queue.append(x)

    def mix(self, other):
        if self.resolve:
            return self.resolve.mix(other)

        if other.resolve:
            return self.mix(other.resolve)

        self.queue.extend(other.queue)
        other.resolve = self

    def pop(self):
        if self.resolve:
            return self.resolve.pop()
        return self.queue.pop()

    def shuffle(self, rng):
        if self.resolve:
            return self.resolve.shuffle(rng)

        rng.shuffle(self.queue)
