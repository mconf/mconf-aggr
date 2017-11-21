import json
import unittest
import unittest.mock as mock

from main_event_listener import aggregator, DataReader

class TestReader(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        publisher_mock = mock.Mock()
        self.data_reader = DataReader()
        self.data_reader.route = "/mock"
        self.data_reader.setup(publisher_mock)

    def test_reader_read(self):
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
                }]
        data = json.dumps(data)
        expected = [{
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

        self.data_reader.read(data)

        self.data_reader.publisher.publish.assert_called_with(expected,channel='webhooks')

        aggregator.stop()
