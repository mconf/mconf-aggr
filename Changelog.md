# Changelog

## 1.5.1
* Fix exception when trying to close _LivenessProbeListener_:
    - Add `is_running` attribute.

## 1.5.0
* Add partial graceful shutdown support:
    - The application waits for all the current requests to be responded and all the events in the aggregator's channels be handled;
    - If the application receives events upon initiating shutdown, they may be lost.
* Configure `/ready` and `/health` to have different behaviours:
    - `/health` returns `OK` and 200 if the application is running. Else, it responds `NOT OK` and 503;
    - `/ready` returns `OK` if `/health` returns `OK` and if the application can connect with the database. Else, it responds `NOT OK` and 503.
* Add a way to deprecate events and not handle them when receive:
    - `MCONF_WEBHOOK_DEPRECATED_EVENTS` is a new env variable that tells which events the aggregator should not handle when receive them. The value must have each event separated by spaces, `meeting-ended meeting-created user-joined` for example.

## 1.4.0
* Rename metadata's field of UsersEvents table to `userdata`.

## 1.3.4
* Fix requirements after greenlet update.
* Fix error when meeting name is not a string.

## 1.3.3
* Add fallback for `external_meeting_id` and `internal_meeting_id` when handling rap events.
* Add logs showing when this error occurs.

## 1.3.2
* Update metadata recording logic, merging only the new metadata
* Fix logging keywords to be a valid json

## 1.3.1
* Add check for external meeting id when creating a meeting

## 1.3.0
* Add new columns for optimization
    - Add new columns in meetings table
    - Add new columns in recordings table
* Add a time logger for each event handled
* Update some levels of logs

## 1.2.0
* Update logging format to json.

### Bugs fixed
* Fix error to build the image after update of a package.
* Fix `RequestDepedencyWarning` exception.
* Fix error when the column `name` of a few tables is set with more than its maximum length.

## 1.1.0
* Update modifications in recording's table to only insert a recording if the meeting was recorded.
* Add scripts to run it easily.
* Add load tests.