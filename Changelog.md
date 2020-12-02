# Changelog

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
    * Add new columns in meetings table
    * Add new columns in recordings table
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