#!/bin/bash

echo "meeting-created"; echo ">"; read
python ./meeting_created.py
echo "user-presenter-assigned"; echo ">"; read
python ./user_presenter_assigned.py
echo "user-joined"; echo ">"; read
python ./user_joined.py
echo "user-presenter-unassigned"; echo ">"; read
python ./user_presenter_unassigned.py
echo "user-audio-voice-enabled"; echo ">"; read
python ./user_audio_voice_enabled.py
echo "meeting-recording-changed"; echo ">"; read
python ./meeting_recording_changed.py
echo "meeting-ended"; echo ">"; read
python ./meeting_ended.py