#!/bin/bash

echo "rap-archive-started"; echo ">"; read
python rap_archive_started.py
echo "rap-archive-ended"; echo ">"; read
python rap_archive_ended.py
echo "rap-sanity-started"; echo ">"; read
python rap_sanity_started.py
echo "rap-sanity-ended"; echo ">"; read
python rap_sanity_ended.py
echo "rap-process-started"; echo ">"; read
python rap_process_started.py
echo "rap-process-ended"; echo ">"; read
python rap_process_ended.py
echo "rap-process-started-pv"; echo ">"; read
python rap_process_started_pv.py
echo "rap-process-ended-pv"; echo ">"; read
python rap_process_ended_pv.py
echo "rap-publish-started"; echo ">"; read
python rap_publish_started.py
echo "rap-publish-ended"; echo ">"; read
python rap_publish_ended.py
echo "rap-post-publish-started"; echo ">"; read
python rap_post_publish_started.py
echo "rap-post-publish-ended"; echo ">"; read
python rap_post_publish_ended.py
echo "rap-publish-started-pv"; echo ">"; read
python rap_publish_started_pv.py
echo "rap-publish-ended-pv"; echo ">"; read
python rap_publish_ended_pv.py
echo "rap-post-publish-started-2"; echo ">"; read
python rap_post_publish_started.py
echo "rap-post-publish-ended-2"; echo ">"; read
python rap_post_publish_ended.py
echo "rap-publish-ended-rec"; echo ">"; read
python rap_publish_ended_rec.py
echo "rap-publish-ended-rec-pv"; echo ">"; read
python rap_publish_ended_rec_pv.py