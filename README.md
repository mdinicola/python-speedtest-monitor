# python-speedtest-monitor

Monitors internet speedtests and alerts to Pushover if download speed is lower than a defined threshold.

# Dependencies
- [speedtest-tracker](https://github.com/henrywhitaker3/Speedtest-Tracker)
- [asuswrtspeedtest](https://github.com/mdinicola/python-asuswrt-speedtest)

# How it works

Note: Speedtest-Tracker is configured to run a speedtest once per hour

- Check download speed from Speedtest-Tracker
- If download speed is lower than configured threshold:
    - Run another speedtest on an AsusWRT-powered router. This can be disabled in configuration
    - Send a notification to Pushover with both the Speed-Tracker and router download speeds.  This notification can be disabled in configuration

# Configuration

Create a file `config/config.ini` file and fill in the details

    [asus_router]
    host = 
    port = 
    use_https = 
    username = 
    password = 
    run_speedtest = true

    [speedtest]
    timeout = 120
    poll_frequency = 15
    history_limit = 10

    [speedtest_tracker]
    host = 
    port = 
    use_https = 

    [monitor]
    download_threshold = 500

    [pushover]
    enabled = false
    user_id = 
    api_token = 
    sound=climb

# How to run

1. Clone the repo
2. Create a configuration file as defined in the Configuration section above
3. `python3 monitor.py`

For continued notifications, set it up to run as a cron job or scheduled task.

# Logs

Logs are written to the `logs/monitor.log` file
