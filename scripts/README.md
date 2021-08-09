# Requirements:
- It is necessary to define an environment variable *MC_AGGR* for the path of the aggregator directory.
- To run locally, you must do the configuration for Python virtual environment explained in ```$MC_AGGR/README.md```.

# Instructions:
This folder contains all the scripts that configure the environment to run the aggregator.

You can define *webhook-env-file.env* in the *env* folder and run *dev_run.sh*. Basically, this script can generate the environment file, run it locally or in a container.

```./dev_run.sh [-g] [-d | -l] [-r] [-n]```

- **-g:** If you don't want to define the environment file, you can use the *-g* option that will generate it using *gen_file.sh*.
- **-d:** Run inside a Docker container.
- **-l:** Run locally.
- **-r:** Should register hook on live. The options are "true" or "false". Default is false.
- **-n:** Run ngrok. The options are "true" or "false". Default is false. To use this option you must download [ngrok](https://ngrok.com/) and copy it to ```$MC_AGGR/scripts/utils```.

**Caution:** you cannot use *-d* and *-l* simultaneously. In addition, execution in Docker is defined by default.

Also, if you don't want to use *dev_run.sh*, you can skip to *dev_locally.sh* (to run locally) and *dev_docker.sh* (to run in a Docker container).