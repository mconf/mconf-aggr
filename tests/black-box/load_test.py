import getopt
import sys
import threading
import time
from random import choice

import events
from utility.config import Config


def main(argv):
    times = 1
    simultaneously = 1
    randomize = True
    forever = False
    interval = 0
    try:
        opts, args = getopt.getopt(
            argv,
            "hert:s:b:",
            ["ever=", "randomize=", "times=", "simultaneously=", "between="],
        )
    except getopt.GetoptError as e:
        print(f"Error: {e}")
        print("Try 'load_test.py -h' to read which parameters can be used.")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print(
                "This script has some default requests to simulate a meeting at the vision of aggregator. It can be used to load testing, for example."
            )
            print("Parameters:")
            print(
                " -b|--between:<integer>: represents the interval in milliseconds between requests."
            )
            print("     Accepts only integers.")
            print("     Default is '0'.")
            print(
                " -e|--ever: only stops to send requests with KeyboardInterrupt exception ('CTRL+C')."
            )
            print(" -h: show this message.")
            print(
                " -r|--randomize: randomize meeting's information as internal meeting id, record id, etc."
            )
            print(
                " -s|--simultaneously=<integer>: how many meetings will be sent simultaneously to aggregator."
            )
            print("     Accepts only integers.")
            print("     Default is '1'.")
            print(" -t|--times=<integer>: how many meetings will be sent to aggregator.")
            print("     Accepts only integers.")
            print("     Default is '1'.")
            sys.exit()
        elif opt in ["-e", "--ever"]:
            forever = True
        elif opt in ["-r", "--randomize"]:
            randomize = True
        elif opt in ["-t", "--times"]:
            times = int(arg)
        elif opt in ["-s", "--simultaneously"]:
            simultaneously = int(arg)
        elif opt in ["b", "--between"]:
            interval = int(arg) / 1000.0

    try:
        threads = []
        for i in range(0, simultaneously):
            threads.append(
                Sender(
                    i,
                    f"Sender_Thread_{i}",
                    randomize,
                    interval,
                    int(times / simultaneously),
                )
            )

        if forever:
            while True:
                for thread in threads:
                    if not thread.is_alive():
                        thread.start()
        else:
            for thread in threads:
                thread.start()

            while threading.activeCount() > 1:
                pass
    except KeyboardInterrupt:
        print()
        print("Terminating...")
        sys.exit()


class Sender(threading.Thread):
    def __init__(self, threadID, name, randomize, interval, times):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.randomize = randomize
        self.interval = interval
        self.times = times

    def run(self):
        print("Starting " + self.name)
        for t in range(0, self.times):
            print(self.name + ":" + "\t" + f"sending load {t}.")
            send_load(self.randomize, self.interval)
        print("Exiting " + self.name)


def send_load(randomize, interval):
    cfg = Config()

    if randomize:
        cfg.randomize_configuration()

    run_meeting(cfg, interval)
    time.sleep(interval)
    run_recording(cfg, interval)


def run_meeting(cfg, interval):
    events.post_meeting_created(
        cfg.internal_meeting_id,
        cfg.external_meeting_id,
        cfg.shared_secret,
        cfg.institution,
    )
    time.sleep(interval)
    for _ in range(choice(range(5))):
        events.post_user_presenter_assigned(
            cfg.internal_meeting_id, cfg.external_meeting_id, cfg.internal_user_id
        )
        time.sleep(interval)
        events.post_user_joined(
            cfg.internal_meeting_id, cfg.external_meeting_id, cfg.internal_user_id
        )
        time.sleep(interval)
        events.post_user_presenter_unassigned(
            cfg.internal_meeting_id, cfg.external_meeting_id, cfg.internal_user_id
        )
        time.sleep(interval)
        events.post_user_audio_voice_enabled(
            cfg.internal_meeting_id, cfg.external_meeting_id, cfg.internal_user_id
        )
        time.sleep(interval)
    events.post_meeting_recording_changed(cfg.internal_meeting_id, cfg.external_meeting_id)
    time.sleep(interval)
    events.post_meeting_transfer_enabled(cfg.internal_meeting_id, cfg.external_meeting_id)
    time.sleep(interval)
    events.post_meeting_transfer_disabled(cfg.internal_meeting_id, cfg.external_meeting_id)
    time.sleep(interval)
    events.post_meeting_ended(cfg.internal_meeting_id, cfg.external_meeting_id)


def run_recording(cfg, interval):
    events.post_rap_archive_started(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    time.sleep(interval)
    events.post_rap_archive_ended(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    time.sleep(interval)
    events.post_rap_sanity_started(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    time.sleep(interval)
    events.post_rap_sanity_ended(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    time.sleep(interval)
    events.post_rap_process_started(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    time.sleep(interval)
    events.post_rap_process_ended(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    time.sleep(interval)
    events.post_rap_process_started_pv(
        cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id
    )
    time.sleep(interval)
    events.post_rap_process_ended_pv(
        cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id
    )
    time.sleep(interval)
    events.post_rap_publish_started(cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id)
    time.sleep(interval)
    events.post_rap_publish_ended(
        cfg.internal_meeting_id,
        cfg.external_meeting_id,
        cfg.record_id,
        cfg.shared_secret,
        cfg.institution,
    )
    time.sleep(interval)
    events.post_rap_post_publish_started(
        cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id
    )
    time.sleep(interval)
    events.post_rap_post_publish_ended(
        cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id
    )
    time.sleep(interval)
    events.post_rap_publish_started_pv(
        cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id
    )
    time.sleep(interval)
    events.post_rap_publish_ended_pv(
        cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id
    )
    time.sleep(interval)
    events.post_rap_post_publish_started(
        cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id
    )
    time.sleep(interval)
    events.post_rap_post_publish_ended(
        cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id
    )
    time.sleep(interval)
    events.post_rap_publish_ended_rec(
        cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id
    )
    time.sleep(interval)
    events.post_rap_publish_ended_rec_pv(
        cfg.internal_meeting_id, cfg.external_meeting_id, cfg.record_id
    )


main(sys.argv[1:])
