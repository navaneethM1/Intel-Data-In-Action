import pickle
import flask
import datetime

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Welcome to TracknAlert"

def DecTreeRes(time,lat,long):
    with open("dtclass", 'rb') as file:  
        model = pickle.load(file)
    return (model.predict([[time,lat,long]])[0])

def getPrediction(time,lat,long):
    res1 = DecTreeRes(time,lat,long)
    res2 = ClusterRes([[lat,long]])
    res = res1 + res2
    if(res==2):
        res=1
    return res 

def ClusterRes(coordinates):
    # loading kmeans model
    kmeans = pickle.load(open("kmeans.pkl", "rb"))

    # loading alertLevel Array
    alertLevel = pickle.load(open("alertLevel.pkl", "rb"))

    # coordinates belongs to which cluster number?
    cluster = kmeans.predict(coordinates)[0]
    alertlvl = alertLevel[cluster]
    return alertlvl


@app.route('/Op/<string>')
def DecisionTree(string):
    time = datetime.datetime.now().strftime('%H') + "." + datetime.datetime.now().strftime('%M') 
    lat,long = tuple(map(float,string.split(',')))
    res = getPrediction(float(time),lat,long)
    return str(res)
    
if __name__ == '__main__':
    app.run(host="192.168.1.100",debug=True)

