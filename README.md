# Client-centered care
In home health care, every day of the week, a health care organization has a set of 
health care jobs that need to be performed by a team of professionals. The jobs are 
geographically located within some region and are defined through their duration 
and time window. The duration is the amount of time it takes to handle the job and 
the time window indicates the time frame wherein the job needs to be handled. 
The same job may occur on multiple days of the week. A job is always associated to 
a client, and multiple jobs may belong to the same client.  A goal of the project is to optimize w.r.t. continuity of care, while taking into 
account the workforce rules and regulations. In other words, minimize the number of nurses clients can see during the week.

## Table of contents

* ### Prerequisites
* ### Installation
* ### Usage

## Prerequisites 
Before you get started with the project, you'll need to make sure you have the following software and tools installed on your machine:

* Python 3.x. You can download it from the official Python website: https://www.python.org/downloads/
* Dash:Dash is a framework for building analytical web applications in Python. You will need to install it in order to build and run a project. You can install it using pip:
```
$ pip install dash
```
* Plotly: Plotly is a data visualization library that Dash uses to render its plots and graphs. You will need to install it in order to build and run a project. You can install it using pip:

```
$ pip install plotly
```

## Installation

1. Clone the repository to your local machine: 
```
$  git clone https://github.com/nastiamazurak/OBP-Yoram3.git
```

2. Navigate to the project directory:

```
$ cd OBP-Yoram3
```
3. Install the required dependencies:

```
$ pip install -r requirements.txt
```
4. Run the project:

```
$ python app.py
```

## Usage

This section provides an overview of how to use the project.

To use the project use these steps: 

1. Run the project: 
```
$ python app.py
```
2. Open http://127.0.0.1:8054/ in browser

3. Upload dataset  (Example of dataset could be found in OBP-Yoram3/src/utils/uploads/user_upload.csv) 
4. Provide number of nurses
5. Click "Submit" button
6. Observe the visuals of the executed algorithm

