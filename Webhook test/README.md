This folder has one script for each event necessary to create, run and end a meeting. 
- *meeting_created.py*
- *meeting_ended.py*
- *meeting_recording_changed.py*
- *user_audio_voice_enabled.py*
- *user_joined.py*
- *user_presenter_assigned.py*
- *user_presenter_unassigned.py*

Also, it has one script for each sent event when a meeting is ended, even if it was recorded.
- *rap_archive_ended.py*
- *rap_archive_started.py*
- *rap_post_publish_ended.py*
- *rap_post_publish_started.py*
- *rap_process_ended_pv.py*
- *rap_process_ended.py*
- *rap_process_started_pv.py*
- *rap_process_started.py*
- *rap_publish_ended_pv.py*
- *rap_publish_ended_rec_pv.py*
- *rap_publish_ended_rec.py*
- *rap_publish_ended.py*
- *rap_publish_started_pv.py*
- *rap_publish_started.py*
- *rap_sanity_ended.py*
- *rap_sanity_started.py*

If you only want to send the events in the correct order, just use *correct_sequence.sh* and *correct_sequence_recording.sh*.

To use the scripts above, you have to set the configuration file which is in Utility folder.
## Instructions to send events (*config.py*).
1. Set *URL* endpoint (somewhere that aggr can listen).
2. Set *AUTHORIZATION* code (it must be in db).

If you want to use a specific *json* file as an event, use *post_event.py*:

``` post_event.py -i <json> -u <url> ```

Where *json* is the filename and *url* is the above endpoint..


