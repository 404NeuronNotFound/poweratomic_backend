"""
Bridges a completed Pomodoro *work* session into today's habit check-in.

NOT WIRED UP YET. checkins/models.py and checkins/serializers.py weren't
available when this was written, so I'm not going to guess at field names
for a write path (creating a CheckIn row) - a wrong guess here would
either crash or silently create malformed data, which is worse than doing
nothing.

To finish this: replace the body of `create_habit_checkin` with a call
into checkins' existing create logic - ideally by importing and calling
whatever function/serializer checkins/views.py already uses for
`POST /checkins/`, so this doesn't duplicate check-in creation rules
(e.g. one-per-day uniqueness) that already live there.
"""

from typing import Optional

from poweratomic.habits.models import Habit

def create_habit_checkin(user, habit: Habit) -> Optional[bool]:
    """
    Should create (or no-op if one already exists) today's check-in for
    `habit`, mirroring whatever checkinsApi.create() does on the frontend.

    Returns True if a new check-in was created, False if one already
    existed today, or None if this hasn't been wired up yet (current
    state - see module docstring).
    """
    return None