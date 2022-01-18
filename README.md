# Graphite-Python
Catchpoint integration with Graphite

We can use this script to pull timeseries data from Catchpoint and store it in Graphite for viewing and analysis using a compatible analysis tool such as Grafana.

This integration relies on a Node.js script that runs at 15 minutes intervals to pull raw performance chart data from the Catchpoint GET: LastRaw API. It can be used to retrieve and store data for a list of tests in the same division. 

# Prerequisites

1. Python v3.x
3. [Graphite 1.1x](https://graphite.readthedocs.io/en/latest/install.html)
4. Catchpoint account with a REST API consumer

# Installation and Configuration

Copy the graphite-python folder to your machine
Run following commands in the directory /graphite-python
   - python -m pip install requests
   - pip install pyyaml
   - pip install logger

   
### Configuration
1. In the “config_catchpoint.yaml” file under config sub-directory, enter your [Catchpoint API consumer key and secret](https://portal.catchpoint.com/ui/Content/Administration/ApiDetail.aspx)
2. In the test_ids dictionary of the “config_catchpoint.yaml” file, enter the test IDs you want to pull the data for in a dictionary of array format.

*Example:*

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
3. In the "config_graphite.yaml" file, enter your Graphite server address and port. The default Graphite URL for a local installation is http://127.0.0.1:2003


### How to run

 
- Create a cronjob to run the application.py file every 15 minutes.

*Example crontab entry, if the file resides in /usr/local/bin/application.py*

`*/15 * * * * cd /usr/local/bin/ && python /usr/local/bin/application.py > /usr/local/bin/log/cronlog.log 2>&1`


## File Structure

    graphite-python/
    ├── request_handler.py          ## Contains APIs related to authentication       
    ├── config
    | ├── config_catchpoint.yaml    ## Configuration file for Catchpoint 
    | ├── config_graphite.yaml      ## Configuration file for Graphite
    ├── log
    | ├── app.log                   ## Contains informational and error logs. 
    ├── application.py              ## main file
    ├── log.py
    ├── request_handler.py          ## Contains API requests for token and raw endpoint 
    ├── utils.py                    ##  utility fot parsing data, inserting it to Graphite and validating configurations
           

Once the script starts running and data is inserted into Graphite, it can viewed via Graphite's Web UI.
