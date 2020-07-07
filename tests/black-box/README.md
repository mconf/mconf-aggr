There are two useful scripts to test aggregator in this dir.

### post_event
If you want to use a specific *json* file as an event, use *post_event.py*:

``` post_event.py -f <json> -u <url> ```

Where *json* is the filename and *url* is the aggregator's endpoint.

### load_test
Also, to do load tests, you can use ``` load_test.py ``` and set some parameters:
- -b/--between: how many milliseconds between requests.
- -e/--ever: run forever. Use ```CTRL+C``` to stop requests.
- -h: to get more information about the script.
- -r/--randomize: it will randomize meeting's configuration. If not set, it'll use *config.cfg*. Also, if there isn't a *config.cfg*, it will be random anyway.
- -s/--simultaneously: how many threads running simultaneously.
- -t/--times: how many meetings will be generated and sent to aggregator. ```--times=1``` will send only one meeting.


