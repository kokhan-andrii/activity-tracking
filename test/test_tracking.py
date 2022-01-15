from typing import Optional, Union

import pytest

from tracker.activity import ActivityDetails, Activity
from tracker.tracker import Tracker


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


def test_find_exact_existing_name(tracker_with_activity):
    activity_by_name = tracker_with_activity.find(tracker_with_activity.activity.details.name)
    assert activity_by_name
    assert activity_by_name.details.name == 'Jogging'
    assert activity_by_name.assignee == 'mee'


def test_find_part_existing_name(tracker_with_activity):
    name = tracker_with_activity.activity.details.name[0:-1]
    activity_by_name = tracker_with_activity.find(search_str=name,exact_match=False)
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
