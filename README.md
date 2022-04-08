# Python-Graphite
Catchpoint Integration with Graphite
---
Graphite is a scalable graphing tool for Time Series data. In Graphite, data is composed of a metric name, metric value, timestamp, and optional tags.

This integration makes use of a Python script that runs at 15 minutes intervals to pull raw performance chart data from the Catchpoint GET: LastRaw API. It can be used to retrieve and store data for a list of tests in the same division.

### Prerequisites
1. Python v3.x
2. [Graphite 1.1x](https://graphite.readthedocs.io/en/latest/install.html)
3. Catchpoint account with a REST API consumer

## Installation and Configuration

Copy the graphite-python folder to your machine
Run following commands in the directory /graphite-python
   - python -m pip install requests
   - pip install pyyaml
   - pip install logger
   - pip install python-dateutil


### Configuration
1. In the 'config_catchpoint.yaml' file under config sub-directory, enter your [Catchpoint API consumer key and secret](https://portal.catchpoint.com/ui/Content/Administration/ApiDetail.aspx)
2. In the test_ids object of the 'config_catchpoint.yaml' file, enter the test IDs you want to pull the data for in a dictionary of array format.

*Example:*

---
    test_ids: { 
              web : ['142619','142620','142621','142622'],
              traceroute : ['142607','142608','142609'], 
              api : ['142637','142638','142683','142689'],
              transaction: ['142602','142603'],
              dns : '142644','142645','142646','142647'],
              smtp : ['142604'],
              websocket: ['842700'],
              ping : ['142599','142600','142601']
          }

---       
3. In the 'config_graphite.yaml' file, enter your Graphite server address and port. The default Graphite URL for a local installation is http://127.0.0.1:2003

4. The carbon configuration file `/etc/carbon/carbon.conf` must be modified to allow creating thousands of datapoints. Change the value `MAX_CREATES_PER_MINUTE = 50` to `MAX_CREATES_PER_MINUTE = inf` and restart carbon-cache using `sudo systemctl restart carbon-cache`

**Note: Ensure that carbon-cache is enabled `CARBON_CACHE_ENABLED=true`**

## How to run


- Create a cronjob to run the application.py file every 15 minutes.

*Example crontab entry, if the file resides in /usr/local/bin/application.py*

`*/15 * * * * cd /usr/local/bin/ && python /usr/local/bin/application.py > /usr/local/bin/logs/cronlog.log 2>&1`



## File Structure

    graphite-python/
    ├── request_handler.py          ## Contains APIs related to authentication       
    ├── config
    | ├── config_catchpoint.yaml    ## Configuration file for Catchpoint 
    | ├── config_graphite.yaml      ## Configuration file for Graphite 
    ├── log
    | ├── app.log                   ## Contains informational and error logs. 
    ├── application.py              ## main file
    ├── log.py                      ## custom logger function
    ├── request_handler.py          ## Contains API requests for token and raw endpoint 
    ├── utils.py                    ##  utility for parsing data, inserting it into Graphite and validating configurations


Time Series data in Graphite can be viewed via it's Web UI. Alternatively, we can connect Graphite to an analytics tool such as Grafana and [explore the data](https://grafana.com/docs/grafana/latest/datasources/graphite/).

**Note: Each distinct metric sent to Graphite is stored in its own database file. This means that high volume data requires a good RAID array and/or SSDs to keep up with the I/O operations, or there may be missing data. For more on Graphite scalability please refer to the [FAQ](https://graphite.readthedocs.io/en/latest/faq.html)**
