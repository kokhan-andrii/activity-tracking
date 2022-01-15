from dataclasses import dataclass
from datetime import datetime
from typing import Final, Optional
from uuid import uuid4, UUID


@dataclass
class ActivityDetails:
    __id: Final[UUID] = uuid4()
    name: Optional[str] = ''


@dataclass(order=True)
class Activity:
    details: Optional[ActivityDetails]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    topic: Optional[str] = None
    done: bool = False
    assignee: str = 'me'