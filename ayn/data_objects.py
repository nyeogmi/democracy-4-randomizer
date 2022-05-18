from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Policies(object):
    labels: List[str]
    policies: List["Policy"]


@dataclass
class Policy(object):
    name: str
    slider: str
    flags: str
    opposites: str
    introduce: int
    cancel: int
    raise_: int
    lower: int
    department: str
    prereqs: str
    min_cost: float
    max_cost: float
    cost_function: str
    cost_multiplier: str
    implementation: int
    min_income: float
    max_income: float
    income_function: str
    income_multiplier: str
    nationalization_gdp_percentage: float
    outputs: List["Connection"]


@dataclass
class SimVars(object):
    labels: List[str]
    simvars: List["SimVar"]


@dataclass
class SimVar(object):
    name: str
    zone: str
    default: float
    min: float
    max: float
    emotion: str
    icon: str
    inputs: List["Connection"]
    outputs: List["Connection"]


@dataclass
class Situations(object):
    labels: List[str]
    situations: List["Situation"]


@dataclass
class Situation(object):
    name: str
    zone: str
    prereq: Optional[str]
    icon: str
    positive: bool
    start_trigger: float
    stop_trigger: float
    cost: float
    cost_function: str  # TODO: Function type
    income: float
    income_function: str
    inputs: List["Connection"]  # TODO: function type
    outputs: List["Connection"]  # TODO: function type


@dataclass
class Connection(object):
    node: str
    code: str
    turns: int