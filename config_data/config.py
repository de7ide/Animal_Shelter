from dataclasses import dataclass
from environs import Env


@dataclass
class Config:
    admin_ids: list[int]


def load_config() -> Config:
    env = Env()
    env.read_env()
    return Config(
        admin_ids=list(map(int, env.list('ADMINS_IDS')))
    )