Let's create some big project using Python.
It's a server side implementation. Don't have to think about UI.
Using UV and virtual environment.


Go through the below links properly and gather the knowledge.
https://groww.in/trade-api/docs/python-sdk
https://groww.in/trade-api/docs/python-sdk/instruments
https://groww.in/trade-api/docs/python-sdk/orders
https://groww.in/trade-api/docs/python-sdk/smart-orders
https://groww.in/trade-api/docs/python-sdk/portfolio
https://groww.in/trade-api/docs/python-sdk/margin
https://groww.in/trade-api/docs/python-sdk/live-data
https://groww.in/trade-api/docs/python-sdk/historical-data
https://groww.in/trade-api/docs/python-sdk/backtesting

Our project will expose the same API above.

We will get live data from Yahoo Finance or Finnhub.
There will be some design pattern because how Yahoo Finance or Finnhub have set data, maybe not match with our expecting data.
Some mechanism to add different provider, except Yahoo finance and Finnhub.

Pulling data from the selected provider, only one API in every configuration seconds(2 for now).


