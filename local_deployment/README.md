# SMART INVESTING
This repository showcases an end-to-end project designed to support investors in navigating the market.

## Features
Key features include:

- Collecting investment data from the internet and storing it locally for customized analysis and modeling
- Visualizing and interacting with historical market data
- Providing answers to basic statistical and market-related queries
- Generating predictions using a machine learning model
- Offering suggestions to support buy or sell decisions


## Running
run the app.py to start the app

## Structure

inv_project/
├── README.md
├── app.py              # main app to run
├── smartinvest/            # logic and processing
│   └── __init__.py
│       ├── datadriver/     # data processing
│       ├── interactor/     # QA interaction with data
│       ├── simulator/      # simulate historical performance
│       └── predictor/      # prediction and give recommendation
├── templates
│   ├── index.html          # home page
│   └── qa.html             # QA page
├── requirements.txt
└── .gitignore