import sys
import getopt
import json
import events

from Utility.config import Config

def main(argv):
    times = 1
    randomize = True
    forever = False
    try:
        opts, args = getopt.getopt(argv, "her:t:", ["randomize=", "times="])
    except getopt.GetoptError:
        print('load_test.py -r --times=1')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('load_test.py -r --times=1')
            sys.exit()
        elif opt == '-e':
            forever = True
        elif opt in ['-r', '--randomize']:
            randomize = bool(arg)
        elif opt in ['-t', '--times']:
            times = int(arg)

    try:
        if forever:
            while True:
                cfg = Config()

                if randomize:
                    cfg.randomize_configuration()

                run_meeting(cfg)
                run_recording(cfg)
        else:
            for i in range(0, times):
                cfg = Config()

                if randomize:
                    cfg.randomize_configuration()

                run_meeting(cfg)
                run_recording(cfg)
    except KeyboardInterrupt:
        print()
        print("Terminating...")
        sys.exit()
        

def run_meeting(cfg):
    events.post_meeting_created(cfg.internal_meeting_id, cfg.external_meeting_id)
    events.post_user_presenter_assigned(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.internal_user_id)
    events.post_user_joined(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.internal_user_id)
    events.post_user_presenter_unassigned(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.internal_user_id)
    events.post_user_audio_voice_enabled(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.internal_user_id)
    events.post_meeting_recording_changed(cfg.internal_meeting_id, cfg.external_meeting_id)
    events.post_meeting_ended(cfg.internal_meeting_id, cfg.external_meeting_id)

def run_recording(cfg):
    events.post_rap_archive_started(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_archive_ended(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_sanity_started(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_sanity_ended(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_process_started(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_process_ended(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_process_started_pv(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_process_ended_pv(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_publish_started(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_publish_ended(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_post_publish_started(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_post_publish_ended(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_publish_started_pv(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_publish_ended_pv(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_post_publish_started(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_post_publish_ended(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_publish_ended_rec(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    events.post_rap_publish_ended_rec_pv(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)

main(sys.argv[1:])