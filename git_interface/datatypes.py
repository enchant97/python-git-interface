from dataclasses import dataclass
from datetime import datetime


@dataclass
class Log:
    commit_hash: str
    author_email: str
    commit_date: datetime
    subject: str
