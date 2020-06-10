There are two useful scripts to test aggregator in this dir.

### post_event
If you want to use a specific *json* file as an event, use *post_event.py*:

``` post_event.py -f <json> -u <url> ```

Where *json* is the filename and *url* is the aggregator's endpoint.

### load_test
Also, to do load tests, you can use ``` load_test.py ``` and set some parameters:
- -r: it will randomize meeting's configuration. If not set, it'll use *config.cfg*. Also, if there isn't a *config.cfg*, it will be random anyway.
- -e: run forever. Use ```CTRL+C``` to stop requests.
- -t/--times: how many meetings will be generated and sent to aggregator. ```--times=1``` will send only one meeting.


