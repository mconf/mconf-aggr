"""This module provides the basic data structures that represent webhook events internally.
"""
import collections
import logging

from mconf_aggr.webhook.exceptions import InvalidWebhookMessageError, InvalidWebhookEventError


"""Webhook event to be manipulated internally.

It contains two fields `event_type` and `event`.
`event_type` is a valid type of event generated by webhooks.
`event` is a data structure that represents a valid event received by the webhook.
"""
WebhookEvent = collections.namedtuple('WebhookEvent', ['event_type', 'event', 'server_url'])

# The namedtuples defined below are used internally to represent webhook events.

MeetingCreatedEvent = collections.namedtuple('MeetingCreatedEvent',
                                             [
                                                'server_url',
                                                'external_meeting_id',
                                                'internal_meeting_id',
                                                'name',
                                                'create_time',
                                                'create_date',
                                                'voice_bridge',
                                                'dial_number',
                                                'attendee_pw',
                                                'moderator_pw',
                                                'duration',
                                                'recording',
                                                'max_users',
                                                'is_breakout',
                                                'meta_data'
                                             ])

MeetingEndedEvent = collections.namedtuple('MeetingEndedEvent',
                                           [
                                                'external_meeting_id',
                                                'internal_meeting_id',
                                                'end_time'
                                           ])

UserJoinedEvent = collections.namedtuple('UserJoinedEvent',
                                         [
                                                'name',
                                                'role',
                                                'internal_user_id',
                                                'external_user_id',
                                                'internal_meeting_id',
                                                'external_meeting_id',
                                                'join_time',
                                                'is_presenter',
                                                'meta_data'
                                         ])


UserLeftEvent = collections.namedtuple('UserLeftEvent',
                                       [
                                                'internal_user_id',
                                                'external_user_id',
                                                'internal_meeting_id',
                                                'external_meeting_id',
                                                'leave_time',
                                                'meta_data'
                                       ])

UserVoiceEnabledEvent = collections.namedtuple('UserVoiceEnabledEvent',
                                               [
                                                'internal_user_id',
                                                'external_user_id',
                                                'external_meeting_id',
                                                'internal_meeting_id',
                                                'has_joined_voice',
                                                'is_listening_only',
                                                'event_name'
                                               ])

UserEvent = collections.namedtuple('UserEvent',
                                   [
                                                'internal_user_id',
                                                'external_user_id',
                                                'external_meeting_id',
                                                'internal_meeting_id',
                                                'event_name'
                                   ])

RapProcessEvent = collections.namedtuple('RapProcessEvent',
                                  [
                                                'external_meeting_id',
                                                'internal_meeting_id',
                                                'record_id',
                                                'workflow',
                                                'current_step'
                                  ])

RapPublishEvent = collections.namedtuple('RapPublishEvent',
                                  [
                                                'external_meeting_id',
                                                'internal_meeting_id',
                                                'record_id',
                                                'workflow',
                                                'current_step'
                                  ])

RapPublishEndedEvent = collections.namedtuple('RapPublishEndedEvent',
                                              [
                                                'name',
                                                'is_breakout',
                                                'start_time',
                                                'end_time',
                                                'size',
                                                'raw_size',
                                                'meta_data',
                                                'playback',
                                                'download',
                                                'external_meeting_id',
                                                'internal_meeting_id',
                                                'workflow',
                                                'current_step'
                                              ])

RapPublishUnpublishHandler = collections.namedtuple('RapPublishUnpublishHandler',
                                            [
                                                'internal_meeting_id',
                                                'external_meeting_id',
                                            ])

RapDeletedEvent = collections.namedtuple('RapDeletedEvent',
                                            [
                                                'internal_meeting_id',
                                                'external_meeting_id',
                                            ])

RapEvent = collections.namedtuple('RapEvent',
                                  [
                                                'external_meeting_id',
                                                'internal_meeting_id',
                                                'record_id',
                                                'current_step',
                                  ])


def map_webhook_event(event):
    """Map from a webhook event received to the corresponding data structure.

    This function calls the corresponding function based on the type of event received.
    It can be thought as an event dispatcher.

    Parameters
    ----------
    event : dict
        Dict with fields and values of the event as received by the webhook.

    Returns
    -------
    mapped_event : event_mapper.WebhookEvent
        It encapsulates both the event type and the event itself.
    """
    logger = logging.getLogger(__name__)

    try:
        event_type = event["data"]["id"]
        server_url = event["server_url"]
    except (KeyError, TypeError) as err:
        logger.warn("Webhook message dos not contain a valid id: {}".format(err))
        raise InvalidWebhookMessageError("Webhook message dos not contain a valid id")

    if event_type == "meeting-created":
        mapped_event = _map_create_event(event, event_type, server_url)

    elif event_type == "meeting-ended":
        mapped_event = _map_end_event(event, event_type, server_url)

    elif event_type == "user-joined":
        mapped_event = _map_user_joined_event(event, event_type, server_url)

    elif event_type == "user-left":
        mapped_event = _map_user_left_event(event, event_type, server_url)

    elif event_type == "user-audio-voice-enabled":
        mapped_event = _map_user_voice_enabled_event(event, event_type, server_url)

    elif (event_type in ["user-audio-voice-enabled", "user-audio-voice-disabled",
                "user-audio-listen-only-enabled", "user-audio-listen-only-disabled",
                "user-cam-broadcast-start", "user-cam-broadcast-end",
                "user-presenter-assigned", "user-presenter-unassigned"]):
        mapped_event = _map_user_event(event, event_type, server_url)

    elif(event_type in ["rap-publish-started", "rap-post-publish-started",
                "rap-post-publish-ended"]):
        mapped_event = _map_rap_publish_event(event, event_type, server_url)

    elif event_type == "rap-publish-ended":
        mapped_event = _map_rap_publish_ended_event(event, event_type, server_url)

    elif(event_type in ["rap-process-started", "rap-process-ended",
                "rap-post-process-started", "rap-post-process-ended"]):
        mapped_event = _map_rap_process_event(event, event_type, server_url)

    elif(event_type in ["rap-archive-started", "rap-archive-ended",
                "rap-sanity-started", "rap-sanity-ended",
                "rap-post-archive-started", "rap-post-archive-ended"]):
        mapped_event = _map_rap_event(event, event_type, server_url)

    elif(event_type in ["rap-unpublished", "rap-published"]):
        mapped_event = _map_rap_published_unpublished_event(event, event_type, server_url)

    elif(event_type == "rap-deleted"):
        mapped_event = _map_rap_deleted_event(event, event_type, server_url)

    else:
        logger.warn("Webhook event id is not valid: '{}'".format(event_type))
        raise InvalidWebhookEventError("Webhook event '{}' is not valid".format(event_type))

    return mapped_event


def _map_create_event(event, event_type, server_url):
    """Map `meeting-created` event to internal representation
    """
    create_event = MeetingCreatedEvent(
                       server_url=event.get("server_url", ""),
                       external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                       internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                       name=_get_nested(event, ["data", "attributes", "meeting", "name"], ""),
                       create_time=_get_nested(event, ["data", "attributes", "meeting", "create-time"], 0),
                       create_date=_get_nested(event, ["data", "attributes", "meeting", "create-date"], None),
                       voice_bridge=_get_nested(event, ["data", "attributes", "meeting", "voice-conf"], ""),
                       dial_number=_get_nested(event, ["data", "attributes", "meeting", "dial-number"], ""),
                       attendee_pw=_get_nested(event, ["data", "attributes", "meeting", "viewer-pass"], ""),
                       moderator_pw=_get_nested(event, ["data", "attributes", "meeting", "moderator-pass"], ""),
                       duration=_get_nested(event, ["data", "attributes", "meeting", "duration"], 0),
                       recording=_get_nested(event, ["data", "attributes", "meeting", "record"], False),
                       max_users=_get_nested(event, ["data", "attributes", "meeting", "max-users"], 0),
                       is_breakout=_get_nested(event, ["data", "attributes", "meeting", "is-breakout"], False),
                       meta_data=_get_nested(event, ["data", "attributes", "meeting", "metadata"], {}))

    webhook_event = WebhookEvent(event_type, create_event, server_url)

    return webhook_event

def _map_rap_deleted_event(event, event_type, server_url):
    """Map `rap-deleted` event to internal representation.
    """
    end_event = RapDeletedEvent(
                    external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                    internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""))

    webhook_event = WebhookEvent(event_type, end_event, server_url)

    return webhook_event

def _map_rap_published_unpublished_event(event, event_type, server_url):
    """Map `rap-unpublished` event to internal representation.
    """
    end_event = RapPublishUnpublishHandler(
                    external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                    internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""))

    webhook_event = WebhookEvent(event_type, end_event, server_url)

    return webhook_event

def _map_end_event(event, event_type, server_url):
    """Map `meeting-ended` event to internal representation.
    """
    end_event = MeetingEndedEvent(
                    external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                    internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                    end_time=_get_nested(event, ["data", "event", "ts"], 0))

    webhook_event = WebhookEvent(event_type, end_event, server_url)

    return webhook_event


def _map_user_joined_event(event, event_type, server_url):
    """Map `user-joined` event to internal representation.
    """
    user_event = UserJoinedEvent(
                     name=_get_nested(event, ["data", "attributes", "user", "name"], ""),
                     role=_get_nested(event, ["data", "attributes", "user", "role"], ""),
                     internal_user_id=_get_nested(event, ["data", "attributes", "user", "internal-user-id"], ""),
                     external_user_id=_get_nested(event, ["data", "attributes", "user", "external-user-id"], ""),
                     internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                     external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                     join_time=_get_nested(event, ["data", "event", "ts"], ""),
                     is_presenter=_get_nested(event, ["data", "attributes", "user", "presenter"], True),
                     meta_data=_get_nested(event, ["data", "attributes", "user", "metadata"], {}))

    webhook_event = WebhookEvent(event_type, user_event, server_url)

    return webhook_event

def _map_user_left_event(event, event_type, server_url):
    """Map `user-left` event to internal representation.
    """
    user_event = UserLeftEvent(
                     internal_user_id=_get_nested(event, ["data", "attributes", "user", "internal-user-id"], ""),
                     external_user_id=_get_nested(event, ["data", "attributes", "user", "external-user-id"], ""),
                     internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                     external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                     leave_time=_get_nested(event, ["data", "event", "ts"], ""),
                     meta_data=_get_nested(event, ["data", "attributes", "user", "metadata"], {}))

    webhook_event = WebhookEvent(event_type, user_event, server_url)

    return webhook_event

def _map_user_voice_enabled_event(event, event_type, server_url):
    """Map `user-audio-voice-enabled` event to internal representation.
    """
    user_event = UserVoiceEnabledEvent(
                     internal_user_id=_get_nested(event, ["data", "attributes", "user", "internal-user-id"], ""),
                     external_user_id=_get_nested(event, ["data", "attributes", "user", "external-user-id"], ""),
                     internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                     external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                     has_joined_voice=_get_nested(event, ["data", "attributes", "user", "sharing-mic"], True),
                     is_listening_only=_get_nested(event, ["data", "attributes", "user", "listening_only"], True),
                     event_name=event_type)

    webhook_event = WebhookEvent(event_type, user_event, server_url)

    return webhook_event

def _map_user_event(event, event_type, server_url):
    """Map `user-*` event to internal representation.
    """
    user_event = UserEvent(
                     internal_user_id=_get_nested(event, ["data", "attributes", "user", "internal-user-id"], ""),
                     external_user_id=_get_nested(event, ["data", "attributes", "user", "external-user-id"], ""),
                     external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                     internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                     event_name=event_type)

    webhook_event = WebhookEvent(event_type, user_event, server_url)

    return webhook_event


def _map_rap_process_event(event, event_type, server_url):
    """Map `rap[-post]-process-*` event to internal representation.
    """
    rap_event = RapProcessEvent(
                    external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                    internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                    record_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                    workflow=_get_nested(event, ["data", "attributes", "workflow"], {}),
                    current_step=event_type)

    webhook_event = WebhookEvent(event_type, rap_event, server_url)

    return webhook_event


def _map_rap_publish_event(event, event_type, server_url):
    """Map `rap[-post]-publish-*` event to internal representation (except for started).
    """
    rap_event = RapPublishEvent(
                    external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                    internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                    record_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                    workflow=_get_nested(event, ["data", "attributes", "workflow"], {}),
                    current_step=event_type)

    webhook_event = WebhookEvent(event_type, rap_event, server_url)

    return webhook_event


def _map_rap_publish_ended_event(event, event_type, server_url):
    """Map `rap-publish-ended` event to internal representation.
    """
    rap_event = RapPublishEndedEvent(
                    name=_get_nested(event, ["data", "attributes", "recording", "name"], ""),
                    is_breakout=_get_nested(event, ["data", "attributes", "recording", "isBreakout"], False),
                    start_time=_get_nested(event, ["data", "attributes", "recording", "startTime"], 0),
                    end_time=_get_nested(event, ["data", "attributes", "recording", "endTime"], 0),
                    size=_get_nested(event, ["data", "attributes", "recording", "size"], ""),
                    raw_size=_get_nested(event, ["data", "attributes", "recording", "rawSize"], 0),
                    meta_data=_get_nested(event, ["data", "attributes", "recording", "metadata"], {}),
                    playback=_get_nested(event, ["data", "attributes", "recording", "playback"], ""),
                    download=_get_nested(event, ["data", "attributes", "recording", "download"], ""),
                    external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                    internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                    workflow=_get_nested(event, ["data", "attributes", "workflow"], {}),
                    current_step=event_type)

    webhook_event = WebhookEvent(event_type, rap_event, server_url)

    return webhook_event


def _map_rap_event(event, event_type, server_url):
    """Map `rap-*` event to internal representation (except for process and publish).
    """
    rap_event = RapEvent(
                    external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                    internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                    record_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                    current_step=event_type)

    webhook_event = WebhookEvent(event_type, rap_event, server_url)

    return webhook_event


def _get_nested(d, keys, default):
    """This function allows retrieving a value for a given list of keys from
    nested dictionaries or returning a default value passed as argument if any
    of the keys is not found.
    """
    for k in keys:
        if k not in d:
            return default
        d = d[k]

    return d
