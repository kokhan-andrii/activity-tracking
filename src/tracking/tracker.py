from typing import Optional, Union, List

from tracking.activity import Activity


class Tracker:
    def __init__(self):
        self._activities: List[Activity] = list()
        self._activity = None

    @property
    def activities(self) -> List[Activity]:
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

    def find(self, search_str: str, exact_match: bool = True) -> Union[List[Activity], Activity]:
        # activities = [activity for activity in self._activities
        # if by in activity.details.name or by in activity.assignee]
        activities: Union[List[Activity], Activity] = []
        if not search_str:
            print(f'Search string has invalid value:<{search_str}>.')
            return activities
        else:
            search_str = search_str.strip()

        for activity in self.activities:
            if exact_match:
                if activity.details:
                    if search_str == activity.details.activity_name or search_str == activity.assignee:
                        activities.append(activity)
            else:
                if search_str in activity.details.activity_name or search_str in activity.assignee:
                    activities.append(activity)

        if activities:
            if len(activities) == 1:
                return activities[0]
        return activities

    def __repr__(self):
        return f'<Tracker {self.activities}>'
