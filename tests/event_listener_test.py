import json
import unittest
import unittest.mock as mock

from mconf_aggr.webhook.event_listener import WebhookDataHandler

class TestReader(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        publisher_mock = mock.Mock()
        self.channel = 'webhooks'
        self.data_reader = WebhookDataHandler(publisher_mock,self.channel)

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

        self.data_reader.process_data(data)

        self.data_reader.publisher.publish.assert_called_with(expected,channel=self.channel)
