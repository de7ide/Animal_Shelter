from dataclasses import dataclass
from environs import Env


@dataclass
class Config:
    token: str
    admin_ids: list[int]


def load_config() -> Config:
    env = Env()
    env.read_env()
    return Config(
        token=env('BOT_TOKEN'),
        admin_ids=list(map(int, env.list('ADMINS_IDS')))
    )