from datetime import datetime
from typing import Final
from uuid import uuid4, UUID

from pydantic import validator, BaseModel


class ActivityDetails(BaseModel):
    activity_name: str
    __id: Final[UUID] = uuid4()
    assignee: str = 'me'


class Activity(BaseModel):
    details: ActivityDetails
    start_date: datetime = None
    end_date: datetime = None
    topic: str = None
    done: bool = False


    @validator('details')
    def activity_details_not_null(cls, value):
        if value is None:
            raise ValueError("ActivityDetails is mandatory to set.")
