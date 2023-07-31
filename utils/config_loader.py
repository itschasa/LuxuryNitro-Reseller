import yaml
import yaml
from dataclasses import dataclass
from typing import Union

class ConfigError(Exception):
    pass


@dataclass
class claiming:
    mode: str
    start_time: int
    api_key: str
    merchant: Union[str, None]
    product: str

    def __post_init__(self):
        if self.mode not in ('sellix', 'sellapp', 'sellpass'):
            raise ConfigError("claiming.mode not in ('sellix', 'sellapp', 'sellpass)")
        
        self.product = str(self.product)

@dataclass
class hit_webhook:
    url: str
    message: str
    emojis: dict

@dataclass
class queue_webhook:
    url: str
    title_emoji: str
    color: int
    emojis: dict
    footer_icon: str
    show_eta: bool

@dataclass
class config:
    discord_admins: list[int]
    api_key: str
    database_name: str
    claiming: claiming
    purchase_link: str
    discord_token: str
    hit_webhook: hit_webhook
    queue_webhook: queue_webhook
    logs_channel: int
    qr_code_link: str

    def __post_init__(self):
        if isinstance(self.claiming, dict):
            self.claiming: claiming = claiming(**self.claiming)
        if isinstance(self.hit_webhook, dict):
            self.hit_webhook: hit_webhook = hit_webhook(**self.hit_webhook)
        if isinstance(self.queue_webhook, dict):
            self.queue_webhook: queue_webhook = queue_webhook(**self.queue_webhook)


def load():
    f = open('config.yml', 'r')
    _config = yaml.safe_load(f)
    f.close()
    return config(**_config)