from dataclasses import dataclass

@dataclass
class Status:
    _type: int
    status_text: str
    in_queue: bool = False
    claiming: bool = False
    completed: bool = False
    
    _map = {0: 'in_queue', 1: 'claiming', 2: 'completed'}

    def __init__(self, _type:str, status_text:str = None):
        self._type = _type
        self.status_text = status_text
        attribute = self._map.get(self._type)
        if attribute: setattr(self, attribute, True)

@dataclass
class ETA:
    next_gift: int = None
    completed: int = None

@dataclass
class Nitro:
    _type: str
    boost: bool = None
    classic: bool = None
    basic: bool = None
    yearly: bool = None
    monthly: bool = None

    def __init__(self, _type:str):
        self._type = _type
        self.boost = True if "Boost" in self._type else False
        self.classic = True if "Classic" in self._type else False
        self.basic = True if "Basic" in self._type else False
        self.yearly = True if "Yearly" in self._type else False
        self.monthly = True if "Monthly" in self._type else False

@dataclass
class PublicUser:
    display_name: str
    id: int
    anonymous: bool

    def __init__(self, display_name:str, id:int):
        self.display_name = display_name
        self.id = id
        self.anonymous = True if self.id == -1 else False

@dataclass
class Claim:
    timestamp: int
    nitro_type: Nitro
    user: PublicUser
    order_id: str
    snipe_time: str = None
    instance: str = None


@dataclass
class Order:
    claimed: list[Claim]
    id: str
    eta: ETA
    quantity: int
    received: int
    status: Status
    user: PublicUser
    timestamp: int = None

@dataclass
class VPS:
    alts: str
    instance_id: str
    last_seen: int
    servers: str
    
@dataclass
class Stats:
    alts: int
    boost_chance: float
    servers: int
    support_time: int
    total_claims: int


@dataclass
class Ticket:
    timestamp: int
    id: str
    opened: bool
    seen: bool

@dataclass
class User:
    username: str
    display_name: str
    email: str
    id: int
    orders: list[Order]
    stats: Stats
    tickets: list[Ticket]
    credits: int

@dataclass
class Queue:
    eta: ETA
    length: int
    queue: list[Order]
    recent: list[Claim]

@dataclass
class CreditChange:
    change: int
    closing_balance: int
    id: str
    reason: str
    timestamp: int

@dataclass
class Credits:
    total: int
    history: list[CreditChange]
