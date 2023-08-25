# Changelog

## 1.14.0
* Add support to multiple recordings by meeting

## 1.13.1
* Fix error on hooks/build.

## 1.13.0
* Change project manager to PDM.
* Set user's leave_time when the meeting ends.

## 1.12.0
* Refactor logs using the loguru package.

## 1.11.0
* Set the metadata `mconf-decrypter-pending` to false when the workflow field `presentation` is updated to `published`.

## 1.10.0
* Add continuous integration:
    - Add `poetry` for dependency management;
    - Add `flake8` for linting and `black` for formatting:
        - Refactor for fixing errors and warnings identified by linter or formatter.
    - Add GitHub Actions workflows:
        - `lint` applies the `flake8` with the `isort` on the code;
        - `test` run all the unit tests and publish the test coverage in the GitHub PR (if the commit is in a PR).

## 1.9.3
* Fix remaining Falcon warnings about deprecated methods;
* Fix error on graceful shutdown with `gevent` monkey patch before all other imports.

## 1.9.2
* Fix Falcon warnings about usage of deprecated methods:
    - `falcon.HTTPUnauthorized` method updated to use keyword arguments instead of positional ones;
    - Assignment on `falcon.response.body` property updated to `falcon.response.text`.

## 1.9.1
* Fix error which doesn't handle the HTTPUnauthorized exception when the request is not authorized.

## 1.9.0
* Update Python version to v3.9.10:
    - Update modules with the latest versions.
* Update load testing to support institutions and secrets:
    - Rename some files out of the PEP 8 style guide;
    - Update the configuration file to use JSON;
    - Add institution and secret for a few events:
        - `rap-publish-ended`
        - `meeting-created`
    - Remove configuration of identifiers:
        - `internal_meeting_id`
        - `external_meeting_id`
        - `record_id`
        - `internal_user_id`
* Fix error which adds empty playbacks into database.

## 1.8.0
* Log all requests for event handling.

## 1.7.0
* Add parent meeting information on breakout rooms:
    - Add `parent_meeting_id` attribute on `MeetingsEvents` and `Recordings` classes.

## 1.6.0
* Add transfer mode support:
    - Add `transfer` and `transfer_count` fields in `Meetings` class;
    - Add `MeetingTransferHandler` to handle `meeting-transfer-*` events;
    - Add `MeetingTransferEvent` tuple containing all the necessary fields to handle these `transfer` events; 
    - Add tests cases for the new handler and for `user-joined` events when the meeting is in `transfer mode`.

## 1.5.2
* Fix error when calling `/health` route:
    - There was a typo in `__init__` method of _LivenessProbeListener_ throwing an exception.

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
