import unittest
import unittest.mock as mock

from mconf_aggr.webhook.db_operations import DataProcessor, Meetings, MeetingsEvents, Recordings, Session ,UsersEvents


class TestOperationsMeetings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        session_mock = mock.Mock()
        session_mock.query = mock.Mock()
        session_mock.query.get = mock.Mock()

        session_mock.query().get.return_value = Meetings(running=False,
                                                           has_user_joined=False,
                                                           participant_count=0,
                                                           listener_count=0,
                                                           voice_participant_count=0,
                                                           video_count=0,
                                                           moderator_count=0,
                                                           attendees=[])
        data = ["mock1", "mock2"]
        self.data_processor = DataProcessor(session_mock, data)

    def test_create_event(self):
        data = [{
                  "data": {
                    "type": "event",
                    "id": "meeting-created",
                    "attributes": {
                      "meeting": {
                        "name": "random-578101",
                        "external-meeting-id": "random-578101",
                        "internal-meeting-id": "0a168dbfbe554287381bf0cfe27e015e33207702-150221244223xx8",
                        "is-breakout": False,
                        "duration": 0,
                        "create-time": 1502212442238,
                        "create-date": "Tue Aug 08 17:14:02 UTC 2017",
                        "moderator-pass": "mp",
                        "viewer-pass": "ap",
                        "record": False,
                        "voice-conf": 73583,
                        "dial-number": "613-555-1234",
                        "max-users": 12,
                        "metadata": {
                           "anything_set_here": "any-other",
                           "anotherMeta": "123"
                        }
                      },
                      "event": {
                        "ts": 1502810164922
                      }
                    }
                  }
                },
                {
                    "external_meeting_id" : "random-578101",
                    "internal_meeting_id" : "0a168dbfbe554287381bf0cfe27e015e33207702-150221244223xx8",
                    "name" : "random-578101",
                    "create_time" : 1502212442238,
                    "create_date" : "Tue Aug 08 17:14:02 UTC 2017",
                    "voice_bridge" : 73583,
                    "dial_number" : "613-555-1234",
                    "attendee_pw" : "ap",
                    "moderator_pw" : "mp",
                    "duration" : 0,
                    "recording" : False,
                    "max_users" : 12,
                    "is_breakout" : False,
                    "meta_data" : {
                       "anything_set_here": "any-other",
                       "anotherMeta": "123"
                    }
                }]
        self.data_processor.webhook_msg = data[0]
        self.data_processor.mapped_msg = data[1]

        self.data_processor.create_meeting()
        args = self.read_args(self.data_processor.session.add)

        self.assertIsInstance(args, Meetings)

    def test_ended_event(self):
        data = [{
                  "data": {
                    "type": "event",
                    "id": "meeting-created",
                    "attributes": {
                      "meeting": {
                        "name": "random-578101",
                        "external-meeting-id": "random-578101",
                        "internal-meeting-id": "0a168dbfbe554287381bf0cfe27e015e33207702-150221244223xx8",
                        "is-breakout": False,
                        "duration": 0,
                        "create-time": 1502212442238,
                        "create-date": "Tue Aug 08 17:14:02 UTC 2017",
                        "moderator-pass": "mp",
                        "viewer-pass": "ap",
                        "record": False,
                        "voice-conf": 73583,
                        "dial-number": "613-555-1234",
                        "max-users": 12,
                        "metadata": {
                           "anything_set_here": "any-other",
                           "anotherMeta": "123"
                        }
                      },
                      "event": {
                        "ts": 1502810164922
                      }
                    }
                  }
                },
                {
                    "external_meeting_id" : "random-578101",
                    "internal_meeting_id" : "0a168dbfbe554287381bf0cfe27e015e33207702-150221244223xx8",
                    "end_time" : 999999
                }]
        self.data_processor.webhook_msg = data[0]
        self.data_processor.mapped_msg = data[1]

        self.data_processor.meeting_ended()
        args = self.read_args(self.data_processor.session.delete)

        self.assertIsInstance(args, Meetings)

        args = self.read_args(self.data_processor.session.add)

        self.assertEqual(args.end_time, data[1]["end_time"])

    def read_args(self, path):
        args, kwargs = path.call_args
        args = args[0]
        return args

class TestOperationsUsers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        self.user_mock = {"is_presenter":False,"is_listening_only":False,
                    "has_joined_voice":False,"has_video":False,
                    "ext_user_id":"mock","int_user_id":"mock",
                    "full_name":"mock","role":"MOCK"}
        session_mock = mock.Mock()
        session_mock.query = mock.Mock()
        session_mock.query.get = mock.Mock()
        session_mock.query.join = mock.Mock()
        session_mock.query.join.filter = mock.Mock()
        session_mock.query.join.filter.count = mock.Mock()

        session_mock.query().join().filter().count.return_value = 1;
        session_mock.query().get.return_value = Meetings(running=False,
                                                           has_user_joined=False,
                                                           participant_count=0,
                                                           listener_count=0,
                                                           voice_participant_count=0,
                                                           video_count=0,
                                                           moderator_count=0,
                                                           attendees=[self.user_mock])

        data = ["mock1","mock2"]
        self.data_processor = DataProcessor(session_mock, data)

    def test_join_event(self):
        data = [{
                  "data": {
                    "type": "event",
                    "id": "user-joined",
                    "attributes": {
                      "meeting": {
                        "external-meeting-id": "mock",
                        "internal-meeting-id": "mock"
                      },
                      "user": {
                        "name": "Mock_User",
                        "role": "MODERATOR",
                        "presenter": True,
                        "internal-user-id": "mock_1",
                        "external-user-id": "mock_1",
                        "sharing-mic": True,
                        "stream": True,
                        "listening-only": True
                      },
                      "event": {
                        "ts": 1502810164922
                      }
                    }
                  }
                },
                {
                    "name" : "Mock_User",
                    "role" : "MODERATOR",
                    "internal_user_id" : "mock_1",
                    "external_user_id" : "mock_1",
                    "join_time" : 1502810164922
                }]
        self.data_processor.webhook_msg = data[0]
        self.data_processor.mapped_msg = data[1]

        self.data_processor.user_join()

        calls = self.data_processor.session.add.call_args_list
        user = calls[len(calls)-2][0][0]
        meeting = calls[len(calls)-1][0][0]

        self.assertIsInstance(user, UsersEvents)
        self.assertEqual(meeting.running, True)
        self.assertEqual(meeting.has_user_joined, True)
        self.assertEqual(meeting.participant_count, 2)
        self.assertEqual(meeting.listener_count, 1)
        self.assertEqual(meeting.voice_participant_count, 1)
        self.assertEqual(meeting.video_count, 1)
        self.assertEqual(meeting.moderator_count, 1)
        self.assertEqual(meeting.attendees[1], {"is_presenter":True,"is_listening_only":True,"has_joined_voice":True,
                                                "has_video":True,"ext_user_id":"mock_1","int_user_id":"mock_1",
                                                "full_name":"Mock_User","role":"MODERATOR"})
        self.data_processor.session.query().join().filter().count.assert_called_once()

        del meeting.attendees[1]

    def test_left_event(self):
        data = [{
                  "data": {
                    "type": "event",
                    "id": "user-left",
                    "attributes": {
                      "meeting": {
                        "external-meeting-id": "mock",
                        "internal-meeting-id": "mock"
                      },
                      "user": {
                        "internal-user-id": "mock",
                        "external-user-id": "mock"
                      },
                      "event": {
                        "ts": 999
                      }
                    }
                  }
                },
                {
                    "internal_user_id" : "mock",
                    "external_user_id" : "mock",
                    "leave_time" : 999
                }]
        self.data_processor.webhook_msg = data[0]
        self.data_processor.mapped_msg = data[1]
        self.data_processor.user_left()

        args = self.read_args(self.data_processor.session.add)

        self.assertEqual(args.attendees, [])

        args.attendees.append(self.user_mock)

    def test_info_update_event(self):
        data = [{
                    "data": {
                        "id": "mock_id"
                    }
                },
                {
                    "internal_user_id" : "mock",
                    "external_user_id" : "mock",
                    "external_meeting_id" : "mock",
                    "internal_meeting_id" : "mock",
                    "event_name" : "user-audio-voice-enabled"
                },
                {
                    "internal_user_id" : "mock",
                    "external_user_id" : "mock",
                    "external_meeting_id" : "mock",
                    "internal_meeting_id" : "mock",
                    "event_name" : "user-audio-voice-disabled"
                },
                {
                    "internal_user_id" : "mock",
                    "external_user_id" : "mock",
                    "external_meeting_id" : "mock",
                    "internal_meeting_id" : "mock",
                    "event_name" : "user-audio-listen-only-enabled"
                },
                {
                    "internal_user_id" : "mock",
                    "external_user_id" : "mock",
                    "external_meeting_id" : "mock",
                    "internal_meeting_id" : "mock",
                    "event_name" : "user-audio-listen-only-disabled"
                },
                {
                    "internal_user_id" : "mock",
                    "external_user_id" : "mock",
                    "external_meeting_id" : "mock",
                    "internal_meeting_id" : "mock",
                    "event_name" : "user-cam-broadcast-start"
                },
                {
                    "internal_user_id" : "mock",
                    "external_user_id" : "mock",
                    "external_meeting_id" : "mock",
                    "internal_meeting_id" : "mock",
                    "event_name" : "user-cam-broadcast-end"
                }]
        self.data_processor.webhook_msg = data[0]

        # hasJoinedVoice = True [1]
        self.data_processor.mapped_msg = data[1]
        self.data_processor.user_info_update()

        args = self.read_args(self.data_processor.session.add)

        self.assertEqual(args.attendees[0]["has_joined_voice"], True)

        # hasJoinedVoice = False [2]
        self.data_processor.mapped_msg = data[2]
        self.data_processor.user_info_update()

        args = self.read_args(self.data_processor.session.add)

        self.assertEqual(args.attendees[0]["has_joined_voice"], False)

        # isListeningOnly = True [3]
        self.data_processor.mapped_msg = data[3]
        self.data_processor.user_info_update()

        args = self.read_args(self.data_processor.session.add)

        self.assertEqual(args.attendees[0]["is_listening_only"], True)

        # isListeningOnly = False [4]
        self.data_processor.mapped_msg = data[4]
        self.data_processor.user_info_update()

        args = self.read_args(self.data_processor.session.add)

        self.assertEqual(args.attendees[0]["is_listening_only"], False)

        # hasVideo = True [5]
        self.data_processor.mapped_msg = data[5]
        self.data_processor.user_info_update()

        args = self.read_args(self.data_processor.session.add)

        self.assertEqual(args.attendees[0]["has_video"], True)

        # hasVideo = False [6]
        self.data_processor.mapped_msg = data[6]
        self.data_processor.user_info_update()

        args = self.read_args(self.data_processor.session.add)

        self.assertEqual(args.attendees[0]["has_video"], False)

    def read_args(self,path):
        args, kwargs = path.call_args
        args = args[0]
        return args

class TestOperationsRecording(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        session_mock = mock.Mock()
        data = ["mock","mock"]
        self.data_processor = DataProcessor(session_mock, data)

    def test_rap_event(self):
        data = [{
                  "data": {
                    "type": "event",
                    "id": "rap-publish-ended",
                    "attributes": {
                      "meeting": {
                        "external-meeting-id": "random-578101",
                        "internal-meeting-id": "0a168dbfbe554287381bf0cfe27e015e33207702-1502212442238"
                      },
                      "recording": {
                        "name": "meetingName",
                        "isBreakout": False,
                        "startTime": 1348943978,
                        "endTime": 3432323,
                        "size": 45,
                        "rawSize": 443,
                        "metadata":{
                        	"something": "set"
                        },
                        "playback":{
                        	"something": "set"
                        },
                        "download":{
                        	"something": "set"
                        }
                      },
                      "event": {
                        "ts": 1502810164922
                      }
                    }
                  }
                },
                {
                    "external_meeting_id" : "random-578101",
                    "internal_meeting_id" : "0a168dbfbe554287381bf0cfe27e015e33207702-1502212442238",
                    "current_step" : "rap-publish-ended",
                    "name" : "meetingName",
                    "is_breakout" : False,
                    "start_time" : 1348943978,
                    "end_time" : 3432323,
                    "size" : 45,
                    "raw_size" : 445,
                    "meta_data" : {},
                    "playback" : {},
                    "download" : {}
                }]
        self.data_processor.webhook_msg = data[0]
        self.data_processor.mapped_msg = data[1]

        self.data_processor.rap_events()

        args,kwargs = self.data_processor.session.add.call_args
        args = args[0]

        self.assertEqual(args.name, data[1]["name"])
        self.assertEqual(args.is_breakout, data[1]["is_breakout"])
        self.assertEqual(args.start_time, data[1]["start_time"])
        self.assertEqual(args.end_time, data[1]["end_time"])
        self.assertEqual(args.size, data[1]["size"])
        self.assertEqual(args.raw_size, data[1]["raw_size"])
        self.assertEqual(args.meta_data, data[1]["meta_data"])
        self.assertEqual(args.playback, data[1]["playback"])
        self.assertEqual(args.download, data[1]["download"])
        self.assertEqual(args.current_step, data[1]["current_step"])
