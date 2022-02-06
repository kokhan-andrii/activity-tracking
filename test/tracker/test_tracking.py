from datetime import datetime

import pytest
from pydantic import ValidationError

from tracking.activity import ActivityDetails, Activity
from tracking.tracker import Tracker


@pytest.fixture
def activities():
    learn_python: Activity = Activity()
    learn_python.details = ActivityDetails(activity_name='Vjobbing')

    jazz_guitar: Activity = Activity()
    jazz_guitar.details = ActivityDetails(activity_name='Jazz guitar')

    return list([learn_python, jazz_guitar])


@pytest.fixture
def activity_details():
    details = ActivityDetails(activity_name='Vjobbing')
    return details


@pytest.fixture
def activity(activity_details) -> Activity:
    activity = Activity(details=activity_details,
                        assignee='mee',
                        start_date=datetime.now(),
                        end_date=datetime.now(),
                        topic='Joba',
                        done=False)
    return activity


@pytest.fixture
def tracker(activity) -> Tracker:
    return Tracker()


@pytest.fixture
def tracker_with_activity(activity) -> Tracker:
    tracker = Tracker()
    tracker.activity = activity
    print('tracker_with_activity', tracker)
    return tracker


def test_create_activity(activity, tracker):
    tracker.activity = activity
    assert tracker.activity
    print('\ntracker.activities: ', tracker.activities)
    assert tracker.activities


def test_create_none_activity(tracker):
    with pytest.raises(ValueError) as er:
        tracker.activity = None
    assert str(er.value) == 'Activity is mandatory to set.'


def test_create_empty_name_activity():
    with pytest.raises(ValidationError):
        Activity(details=None)


def test_create_tracking_with_none_activity(tracker):
    with pytest.raises(ValueError) as ex:
        tracker.activity = None
        assert ex.value == 'Activity is mandatory to set.'


def test_find_exact_existing_name(tracker_with_activity):
    assert tracker_with_activity.activity
    assert tracker_with_activity.activity.details
    activity_by_name = tracker_with_activity.find(tracker_with_activity.activity.details.activity_name)
    assert activity_by_name
    assert activity_by_name.details.activity_name == 'Jogging'
    assert activity_by_name.details.assignee == 'mee'


def test_find_part_existing_name(tracker_with_activity):
    name = tracker_with_activity.activity.details.activity_name[0:-1]
    activity_by_name = tracker_with_activity.find(search_str=name, exact_match=False)
    assert activity_by_name
    assert activity_by_name.details.activity_name == 'Jogging'
    assert activity_by_name.details.assignee == 'mee'


@pytest.mark.parametrize("invalid_search_criterion", ['', None, ' ', ' f '])
def test_find_by_name_empty(invalid_search_criterion, tracker_with_activity):
    assert tracker_with_activity.find(invalid_search_criterion) == []


def test_find_existing_with_trailing_spaces(tracker_with_activity):
    str_to_search = ' ' + tracker_with_activity.activity.details.assignee + ' '
    assert tracker_with_activity.activity.details.assignee == \
           tracker_with_activity.find(search_str=str_to_search).details.assignee


def test_find_by_assignee(tracker_with_activity):
    activity_by_assignee = tracker_with_activity.find(tracker_with_activity.activity.details.assignee)
    assert activity_by_assignee
    assert activity_by_assignee.details.activity_name == 'Jogging'
    assert activity_by_assignee.details.assignee == 'mee'


def test_list_all_activities(activities, tracker):
    tracker.activity = activities
    assert len(activities) == 2
    for activity in activities:
        print(activity)
        tracker.activity = activity
    tracked_activities: list[Activity] = tracker.activities
    print(tracked_activities)
    assert len(tracked_activities) == 3


def test_update_activity(activity, tracker):
    assert activity.details.activity_name == 'Jogging'
    tracker.activity = activity
    before_activities = tracker.activities

    tracker2: Tracker = Tracker()
    tracker2.activity = Activity(
        details=ActivityDetails(name='Evening Jogging'),
        assignee=activity.details.assignee,
        topic=activity.topic,
        start_date=activity.start_date,
        end_date=activity.end_date,
        done=activity.done
    )
    assert tracker2.activity.details.activity_name == 'Evening Jogging'

    after_activities = tracker2.activities
    assert before_activities[0].details.activity_name != after_activities[0].details.activity_name
