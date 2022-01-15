from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union, Final
from uuid import uuid4, UUID

import pytest


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


class Tracker:
    def __init__(self):
        self._activities = []
        self._activity = None

    def list_activities(self) -> Optional[list[Activity]]:
        return self._activities

    @property
    def activity(self) -> Optional[Activity]:
        return self._activity

    @activity.setter
    def activity(self, new_activity: Optional[Activity]):
        if not new_activity:
            raise ValueError('Activity is mandatory to set.')

        self._activity = new_activity
        self._activities.append(self._activity)

    def find(self, search_str: str, exact_match: bool = True) -> Union[list[Activity], Activity]:
        # activities = [activity for activity in self._activities
        # if by in activity.details.name or by in activity.assignee]
        activities = []
        if not search_str:
            print(f'Search string has invalid value:<{search_str}>.')
            return activities
        else:
            search_str = search_str.strip()

        for activity in self.list_activities():
            if exact_match:
                if search_str == activity.details.name or search_str == activity.assignee:
                    activities.append(activity)
            else:
                if search_str in activity.details.name or search_str in activity.assignee:
                    activities.append(activity)

        if activities:
            if len(activities) == 1:
                return activities[0]
        return activities


@pytest.fixture
def activities():
    details1 = ActivityDetails()
    details1.name = 'Learning Python'
    details2 = ActivityDetails()
    details2.name = 'Jazz guitar'

    learn_python: Activity = Activity(details1)
    jazz_guitar: Activity = Activity(details2)

    return list([learn_python, jazz_guitar])


@pytest.fixture
def activity() -> Activity:
    details = ActivityDetails()
    details.name = 'Jogging'
    return Activity(details=details, assignee='mee')


@pytest.fixture
def tracker(activity) -> Tracker:
    return Tracker()


@pytest.fixture
def tracker_with_activity(activity) -> Tracker:
    tracker = Tracker()
    tracker.activity = activity
    return tracker


def test_create_activity(activity, tracker):
    tracker.activity = activity
    assert tracker.activity
    assert tracker.list_activities()


def test_create_none_activity(tracker):
    with pytest.raises(ValueError) as er:
        tracker.activity = None
    assert str(er.value) == 'Activity is mandatory to set.'


def test_create_empty_name_activity():
    activity = Activity(details=None)
    assert not activity.details


def test_create_tracking_with_none_activity(tracker):
    with pytest.raises(ValueError) as ex:
        tracker.activity = None
        assert ex.value == 'Activity is mandatory to set.'


def test_find_by_existing_name(tracker_with_activity):
    activity_by_name = tracker_with_activity.find(tracker_with_activity.activity.details.name)
    assert activity_by_name
    assert activity_by_name.details.name == 'Jogging'
    assert activity_by_name.assignee == 'mee'


@pytest.mark.parametrize("invalid_search_criterion", ['', None, ' ', ' f '])
def test_find_by_name_empty(invalid_search_criterion, tracker_with_activity):
    assert tracker_with_activity.find(invalid_search_criterion) == []


def test_find_existing_with_trailing_spaces(tracker_with_activity):
    str_to_search = ' ' + tracker_with_activity.activity.assignee + ' '
    assert tracker_with_activity.activity.assignee == tracker_with_activity.find(search_str=str_to_search).assignee


def test_find_by_assignee(tracker_with_activity):
    activity_by_assignee = tracker_with_activity.find(tracker_with_activity.activity.assignee)
    assert activity_by_assignee
    assert activity_by_assignee.details.name == 'Jogging'
    assert activity_by_assignee.assignee == 'mee'


def test_list_all_activities(activities, tracker):
    tracker.activity = activities
    assert len(activities) == 2
    for activity in activities:
        print(activity)
        tracker.activity = activity
    tracked_activities: list[Activity] = tracker.list_activities()
    print(tracked_activities)
    assert len(tracked_activities) == 3


def test_update_activity(activity, tracker):
    assert activity.details.name == 'Jogging'
    tracker.activity = activity
    before_activities = tracker.list_activities()

    tracker2: Tracker = Tracker()
    tracker2.activity = Activity(
        details=ActivityDetails(name='Evening Jogging'),
        assignee=activity.assignee,
        topic=activity.topic,
        start_date=activity.start_date,
        end_date=activity.end_date,
        done=activity.done
    )
    assert tracker2.activity.details.name == 'Evening Jogging'

    after_activities = tracker2.list_activities()
    assert before_activities[0].details.name != after_activities[0].details.name
