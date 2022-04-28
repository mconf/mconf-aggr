import json
import re
import time
from contextlib import contextmanager

import requests
import sqlalchemy

from mconf_aggr.webhook.database_model import (
    Meetings,
    MeetingsEvents,
    Recordings,
    UsersEvents,
)


class IntegrationEngine:
    def __init__(self, token, database_uri, url="http://localhost:8000", delay=5):
        self._orm_session = sqlalchemy.orm.sessionmaker()
        engine = sqlalchemy.create_engine(database_uri, echo=True)
        self._orm_session.configure(bind=engine)

        self._database_uri = database_uri
        self._url = url
        self._scheme, self._domain, self._port = self._extract_from_url(self._url)
        self._token = token
        self._delay = delay
        self._timestamp = int(time.time() * 1000.0)
        self._tables = [Meetings, UsersEvents, MeetingsEvents, Recordings]

        self._reset_tables()

    @property
    def database_session(self):
        @contextmanager
        def _session_scope(raise_exception=True):
            """Provide a transactional scope around a series of operations."""
            self._session = self._orm_session()
            try:
                yield
                self._session.commit()
            except RuntimeError:
                self._session.rollback()
                if raise_exception:
                    raise
            finally:
                self._session.close()

        return _session_scope

    def post_and_wait(self, event, delay=None):
        _ = self.post(event)

        delay = delay or self._delay
        time.sleep(delay)

    def post(self, event):
        converted_event = json.dumps(event)

        r = requests.post(
            url=self._url,
            data={
                "domain": self._domain,
                "event": converted_event,
                "timestamp": self._timestamp,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": "Bearer " + self._token,
            },
        )

        return r

    def users_meetings_events_by_user_id(self, internal_user_id):
        users_events, meetings_events = (
            self._session.query(UsersEvents, MeetingsEvents)
            .join(UsersEvents.meeting_event)
            .filter(UsersEvents.internal_user_id == internal_user_id)
            .first()
        )

        return (users_events, meetings_events)

    def meetings_meetings_events_by_meeting_id(self, internal_meeting_id):
        meetings, meetings_events = (
            self._session.query(Meetings, MeetingsEvents)
            .join(Meetings.meeting_event)
            .filter(MeetingsEvents.internal_meeting_id == internal_meeting_id)
            .first()
        )

        return (meetings, meetings_events)

    def users_events_by_user_id(self, user_id):
        users_events = (
            self._session.query(UsersEvents)
            .join(UsersEvents.meeting_event)
            .filter(UsersEvents.internal_user_id == user_id)
            .first()
        )

        return users_events

    def meetings_events_by_meeting_id(self, internal_meeting_id):
        meetings_events = (
            self._session.query(MeetingsEvents)
            .filter(MeetingsEvents.internal_meeting_id == internal_meeting_id)
            .first()
        )

        return meetings_events

    def meetings_by_meeting_id(self, internal_meeting_id):
        meetings = (
            self._session.query(Meetings)
            .join(Meetings.meeting_event)
            .filter(MeetingsEvents.internal_meeting_id == internal_meeting_id)
            .first()
        )

        return meetings

    def recordings_by_meeting_id(self, meeting_id):
        recordings = (
            self._session.query(Recordings)
            .filter(Recordings.internal_meeting_id == meeting_id)
            .first()
        )

        return recordings

    def _reset_tables(self):
        with self.database_session():
            for table in self._tables:
                self._session.query(table).delete()

    def _extract_from_url(self, url):
        p = re.compile(r"(http|https)://([\w.-]*):(\d+)")
        match = p.match(url)

        return match.groups()
