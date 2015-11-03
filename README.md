#HomelessNet [HLN]
### SocialCops Twitter-Elasticsearch Challenge


**HLN**  fetches tweets (leads) from  Twitter Streaming API and stores them in Elasticsearch index after text processing and makes searchable and analyzable through a frontend application.


###Features
* Search query results get their relevance scores boosted for query terms matching in extracted mentions
* Search Functionality supports filtering search results on basis of  entities (@mentions) and categories (#hashtags)
* Displaying simple data analytics with use of Elasticsearch aggregations
* MysqlDb based login system



### Dependencies

* Elasticsearch should be up and running
* Mysql should be installed
* Python3 (tweepy module is not supported on Python2)
* Python modules dependencies mentioned in requirements.txt


###How to run?
* Clone the repository
* Run setupdb.sh to setup database and add user
	```$ /bin/bash setupdb.sh```
* Add your mysql credentials in **/config.py** and twitter app credential in **/hln/mod_twapi/config.py**
* Create and activate Virtual Environment 
	 ```$ virtualenv -p /usr/bin/python3 venv --no-site-packages```
	```$ source venv/bin/activate ```
* Install python module dependencies
	```$ pip install -r > requirements.txt```
* Index data in Elasticsearch
	```$ python run.py --esload``` 
* Start the server
	```$ python run.py```

###Contact
For any queries/issues, contact me at `dpkshrma01[at]gmail[dot]com`