# required modules
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from scipy import stats
from statsmodels.stats import weightstats as stests
from statsmodels.stats.proportion import proportions_ztest
import math
import time
from datetime import datetime
from flask import Flask, render_template, url_for, request, redirect, flash
from werkzeug.utils import secure_filename



# upload folder
UPLOAD_FOLDER = os.getcwd() + '/static'
ALLOWED_EXTENSIONS = {'csv'}



# app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = "SbMqMX80'1Ssz/7;sX/5uO4]Y"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# helper function
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/', methods=['GET','POST'])
def fileUpload():
    if request.method == 'POST':
        file1 = request.files['file1']
        file2 = request.files['file2']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file1.filename == '' or file2.filename == '':
            flash('Please select both the files')
            return redirect(url_for('fileUpload'))

        if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
            filename1 = secure_filename(file1.filename)
            filename2 = secure_filename(file2.filename)
            file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
            flash('Files Successfully Uploaded')
            return redirect(url_for('links'))
        else:
            flash('Please upload CSV files only')
            return redirect(url_for('fileUpload'))
    return render_template('fileUpload.html')


@app.route('/links')
def links():
    return render_template('links.html')

@app.route('/graphs.html')
def graphs():
    return render_template('graphs.html')

@app.route('/basicanalysis.html')
def basicanalysis():
    return render_template('basicanalysis.html')

@app.route('/hypotheses.html')
def hypotheses():
    return render_template('hypotheses.html')




@app.route('/hypothesis_distribution_of_alarm_types_accross_buses')
def hypothesis_distribution_of_alarm_types_accross_buses():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)

    # a. Chi squared test for Homogeneity - Distribution of Alarm types across  different buses
    cont =pd.crosstab(df['deviceId'], 
                                df['alarmType'],  
                                   margins = False) 
    chi,pval,dof,expected=stats.chi2_contingency(cont)
    
    # b. Code for plotting the distribution
    fig = df.groupby(['deviceId','alarmType']).size().unstack().plot(kind = 'bar',stacked=False,figsize=(8,8)).get_figure()
    fig.savefig(os.getcwd() + '/static/' + 'hypo1.jpeg')
    plt.close(fig)
    return render_template('hypo.html', title_no=1, title='Hypothesis Testing to check the distribution of alarm types across buses which is followed by the distribution graph', null="Alarm types are identically distributed among the buses", alternate="The distribution of alarm types varies from bus to bus", chi=chi, fig='hypo1.jpeg', caption='Distribution of alarm types among the buses')


@app.route('/hypothesis_distribution_of_alarm_types_accross_hours')
def hypothesis_distribution_of_alarm_types_accross_hours():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    hr = df['recorded_at_time'].str.slice(0,2)
    # a. Chi squared test for Homogeneity - Distribution of Alarm types across hours
    cont =pd.crosstab(df['alarmType'], 
                                hr,  
                                   margins = False) 
    chi,pval,dof,expected=stats.chi2_contingency(cont)
    df['hour'] = hr
    # b. Code for plotting the distribution
    fig = df.groupby(['hour','alarmType']).size().unstack().plot(kind = 'bar',stacked=False,figsize=(8,8)).get_figure()
    fig.savefig(os.getcwd() + '/static/' + 'hypo2.jpeg')
    plt.close(fig)
    return render_template('hypo.html', title_no=2, title='Hypothesis Testing to check the distribution of alarm types across hours', null="Alarm types are identically distributed across hours", alternate="The distribution of alarm types depends on the hour", chi=chi, fig='hypo2.jpeg', caption='Distribution of alarm types in the ith hour')

    
@app.route('/best_speed_for_optimal_mileage')
def best_speed_for_optimal_mileage():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[1]
    df1 = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    df = df1.dropna()
    hrs = df['Duration(in milliseconds)']/3600000
    speeds = df['Total Distance']/hrs
    df['Avg speed'] = speeds

    df = df[df['Avg speed'] < 60]

    #Alternate : Average mileage is < 3.5kmpl for buses whose avg speeds are lesser than 60kmph
    #H0 : μ >= 3.5, H1 : μ < 3.5
    zstat ,pval = stests.ztest(x1=df['Mileage'],value=3.5,alternative='smaller')
    return render_template('hypo.html', title_no=4, title='Hypothesis Testing to check the best speed for optimal mileage', null="Average mileage is >= 3.5kmpl for buses whose avg speeds are lesser than 60kmph", alternate="Average mileage is < 3.5kmpl for buses whose avg speeds are lesser than 60kmph", pvalue=pval)


@app.route('/graph_of_device_id_vs_frequency_of_FCW_6_to_6')
def graph_of_device_id_vs_frequency_of_FCW_6_to_6():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    date_objs=[]
    d1=df["recorded_at_date"]
    t1=df["recorded_at_time"]
    for i in range(len(df)):
        d=list(map(int,d1[i].split('-')))
        t=list(map(int,t1[i].split(':')))
        date_obs=datetime(d[0],d[1],d[2],t[0],t[1],t[2])
        date_objs.append(date_obs)

    device_id=df["deviceId"].values
    alarm_type=df["alarmType"].values
    speed=df["speed"].values
    d2={}
    for i in range(len(df)):
        if device_id[i] not in d2:
            d2[device_id[i]]=[]
            d2[device_id[i]].append(0)
        if alarm_type[i]=="FCW" and date_objs[i].hour>6 and date_objs[i].hour<18:
            d2[device_id[i]][0]+=1

    d3={}
    for i in range(len(df)):
        if device_id[i] not in d3:
            d3[device_id[i]]=[]
        if alarm_type[i]=="FCW" and date_objs[i].hour>6 and date_objs[i].hour<18:
            d3[device_id[i]].append(speed[i])

    l1=[]
    for i in d3:
        l1.append(np.mean(d3[i]))

    j=0
    for i in d3:
        if l1[j] >  30.0:
            print(i ,"=>", "careless driving")
            d2[i].append(l1[j])
            d2[i].append("careless")
        else:
            print(i ,"=>", "careful driving")
            d2[i].append(l1[j])
            d2[i].append("careful")
        j+=1

    ls=[]
    ls1=[]
    ls2=[]
    for i in d2:
        ls.append(i)
        ls1.append(d2[i][0])
        ls2.append(d2[i][1])

    p1=plt.bar(range(len(ls)),ls1,0.42,color='orange')
    plt.xticks(range(len(ls)), ls,rotation=90,fontsize=10)
    plt.yticks(range(0,8500,500))
    plt.ylabel('device id')
    plt.xlabel('frequency')
    plt.title("frequency count of FCW alarm from 6am to 6pm")
    plt.rcParams['figure.figsize'] = (20.0, 20.0)

    plt.savefig(os.getcwd() + '/static/' + 'basicVisual1.jpeg')
    return render_template('basicVisual.html', title_no=1, title='Frequency of FCW from 6am to 6pm', fig='basicVisual1.jpeg', caption='Frequency of FCW from 6am to 6pm')


@app.route('/HWM_turning_into_FCW')
def HWM_turning_into_FCW():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    df1 = df.groupby(['deviceId'],as_index=False)

    buses = []

    # buses list
    for x in df1:
        buses.append(x[0])
    dates = df['recorded_at_date']
    times = df['recorded_at_time']
    date_objs = []

    # creating datetime objects
    for i in range(len(df)):
        d = list(map(int,dates[i].split('-')))
        t = list(map(int,times[i].split(':')))
        date_obj = datetime(d[0],d[1],d[2],t[0],t[1],t[2])
        date_objs.append(date_obj)

    h_f_d = {}
    # h_f_d is a hmw to fcw dictionary
    # of the form {'bus_id': [day_transitions,night_transitions,%day_trans,%night_trans]}
    for bus in buses:
        h_f_d[bus] = []

    c = 0
    for x in df1:
        count_days = 0
        count_nights = 0
        df = x[1]

        # considered a transition period = 5 seconds
        # day time is considered as 5am to 9pm
        # night time is considered as 9pm to 5am
        for i in range(c,c + len(df)-1):
            if(df['alarmType'][i] == 'HMW' and df['alarmType'][i+1] == 'FCW' and (date_objs[i+1]-date_objs[i]).seconds <= 5):
                if(21 <= date_objs[i].hour <= 23 or 0 <= date_objs[i].hour <= 4):
                    count_nights += 1
                else:
                    count_days += 1

        h_f_d[x[0]].append(count_days)
        h_f_d[x[0]].append(count_nights)
        hmw = len(df.loc[df['alarmType']=='HMW'])
        dperc = (count_days/hmw)*100
        nperc = (count_nights/hmw)*100
        h_f_d[x[0]].append(dperc)
        h_f_d[x[0]].append(nperc)
        c += len(df)

    # plotting
    df2 = pd.DataFrame(h_f_d)
    dperc = df2.iloc[0]
    nperc = df2.iloc[1]
    r1 = np.arange(9)
    r2 = [x + .25 for x in r1]
    plt.bar(r1,dperc,label='day',width=.25)
    plt.bar(r2,nperc,label='night',width=.25)
    plt.xticks([r + .25 for r in range(9)], buses, rotation = 90, fontsize=10)
    plt.rcParams['figure.figsize'] = (8, 8)
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual2.jpeg')
    plt.close()
    return render_template('basicVisual.html', title_no=2, title='How many times HWM turned into FCW?', fig='basicVisual2.jpeg', caption='blue bar - day_count, orange bar - night_count')


@app.route('/when_max_alerts_were_generated_for_each_bus')
def when_max_alerts_were_generated_for_each_bus():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    df1 = df.groupby(['deviceId'],as_index=False)

    # getting hours
    hrs = df['recorded_at_time']
    hrs = list(map(int, list(map(lambda k : k[0]+k[1], hrs))))
    df['hrs'] = hrs

    dict_={}
    # dict_ will have "bus_id : information about the bus grouped by hours" 
    for x in df1:
        dict_[x[0]] = x[1]
    for bus,val in dict_.items():
        dict_[bus] = val.groupby(['hrs'])

    csv = ''
    for bus,hrs in dict_.items():
        l = []
        i = 0
        for x in hrs:
            l.append((i,len(x[1])))
            i+=1

        # finding the hour when maximum alerts have been generated
        max_hr = max(l,key=lambda x:x[1])[0]
        low = str(max_hr)+':00'
        high = str(max_hr+1)+':00'
        t = time.strptime(low, "%H:%M")
        low = time.strftime( "%I:%M %p", t )
        t = time.strptime(high, "%H:%M")
        high = time.strftime( "%I:%M %p", t )
        csv += bus + "," + low[:2] + " " + low[-2:] + ' to ' + high[:2] + " " + high[-2:] + "\n"

    csv = csv[:-1]
    return render_template('basicVisual2.html', csv=csv, title='When has the maximum number of alerts been generated for each bus?')



@app.route('/distribution_of_speed_for_FCW')
def distribution_of_speed_for_FCW():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    alarm_type=df["alarmType"].values
    speed=df["speed"].values
    ls1=[]
    for i in range(len(speed)):
        if alarm_type[i]=='FCW':
            ls1.append(speed[i])
    sns.set(style="whitegrid")
    ax = sns.boxplot(y=ls1,color="green")
    plt.yticks(fontsize=10)
    plt.xlabel("speed variation for FCW",fontsize=10)
    plt.rcParams['figure.figsize'] = (20.0, 20.0)
    plt.ylabel("speed",fontsize=10)
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual3.jpeg')
    return render_template('basicVisual.html', title_no=3, title='Distribution of speed for FCW', fig='basicVisual3.jpeg', caption='Distribution of speed for FCW')

#Basic analysis
@app.route('/ba1')
def ba1():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    df1 = pd.read_csv(os.getcwd() + '/static/' + csvfiles[0])
    df2 = pd.read_csv(os.getcwd() + '/static/' + csvfiles[1])
    res = (str(len(set(df1['deviceId']))) + ' buses in AlertData') + ',' + (str(len(set(df2['VehicleId']))) + 'buses in FuelInfo')
    return render_template('ba_template.html',title='Number of buses described',title_no=1,res=res)

@app.route('/ba2')
def ba2():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    df1 = pd.read_csv(os.getcwd() + '/static/' + csvfiles[0])
    df2 = pd.read_csv(os.getcwd() + '/static/' + csvfiles[1])
    dict_ = {}
    df1_group_by = df1.groupby(['deviceId'],as_index=False)
    for x in df1_group_by:
        dict_[x[0]] = x[1]
    csv=''
    for bus,val in dict_.items():
        print(bus)
        x = val.iloc[[0,-1]]['recorded_at_date']
        csv+=bus + ',' + x.iloc[0] + ',' + x.iloc[1] + '\n'
    csv = csv[0:-1]
    return render_template('ba_template_table3.html',colh1='Bus ID',colh2='Start Date',colh3='End Date',title='Start and end dates of data for each bus',title_no=2,csv=csv,cols=['Bus_ID','Start Date','End Date'])
   
@app.route('/ba3')
def ba3():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    df2 = pd.read_csv(os.getcwd() + '/static/' + csvfiles[1])
    csv=''
    for bus in df2['VehicleId'].unique():
        df = df2[(df2['VehicleId']==bus) & (df2['Total Distance']!=np.nan)]
        sumdist=0
        for i in df['Total Distance'].values:
            if not np.isnan(i):
                sumdist+=i
        csv+=bus + ',' + str(sumdist) + '\n'
    csv = csv[0:-1]
    return render_template('ba_template_table3.html',title='Total distance covered by each bus',title_no=3,csv=csv,cols=['Bus_ID','Distance'])
   

@app.route('/ba4')
def ba4():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    df2 = pd.read_csv(os.getcwd() + '/static/' + csvfiles[1])
    mils = []
    for i in df2['Mileage'].values :
        if not np.isnan(i):
            mils.append(i)
    res = str(np.average(mils))
    res = 'Average Mileage='+res
    return render_template('ba_template.html',title='Average Mileage',title_no=4,res=res)


@app.route('/ba5')
def ba5():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    df2 = pd.read_csv(os.getcwd() + '/static/' + csvfiles[1])
    csv=''
    for bus in df2['VehicleId'].unique():
        df = df2[(df2['VehicleId']==bus)]
        mils=[]
        for i in df['Mileage'].values :
            if not np.isnan(i):
                mils.append(i)
        if len(mils)>0:
            csv += bus+ ',' +str(np.average(mils))+ '\n'
    csv = csv[0:-1]
      
    return render_template('ba_template_table3.html',title='Average mileage of each bus',title_no=5,csv=csv,cols=['Bus_ID','Average Mileage'])
   

@app.route('/ba7')
def ba7():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    df1 = pd.read_csv(os.getcwd() + '/static/' + csvfiles[0])
    csv=''
    for alertType in df1['alarmType'].unique():
        csv += alertType+','+str(len(df1[df1['alarmType']==alertType]))+'\n'
    csv = csv[0:-1]
    return render_template('ba_template_table3.html',title='Frequency of each alert type',title_no=7,csv=csv,cols=['Alert Type','Frequency'])
   

@app.route('/ba8')
def ba8():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    df1 = pd.read_csv(os.getcwd() + '/static/' + csvfiles[0])
    csv=''
    for alertType in df1['alarmType'].unique():
        csv+= alertType+','+str(np.average(df1[df1['alarmType']==alertType]['speed'].values))+'\n'
    csv = csv[0:-1]
    return render_template('ba_template_table3.html',title='Average speed for each alert type',title_no=8,csv=csv,cols=['Alert Type','Average speed'])

@app.route('/ba10')
def ba10():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    df1 = pd.read_csv(os.getcwd() + '/static/' + csvfiles[0])
    csv=''
    for bus in df1['deviceId'].unique():
        csv += bus +','+str(np.average(df1[df1['deviceId']==bus]['speed'].values))+'\n'
    csv = csv[0:-1]
    return render_template('ba_template_table3.html',title='Average speed of each bus',title_no=9,csv=csv,cols=['Bus_ID','Average speed'])

@app.route('/ba9')
def ba9():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    df1 = pd.read_csv(os.getcwd() + '/static/' + csvfiles[0])
    csv=''
    for bus in df1['deviceId'].unique():
        csv += bus +','+str(len(df1[df1['deviceId']==bus]))+'\n'
    csv = csv[0:-1]
    return render_template('ba_template_table3.html',title='Alert frequencies for each bus',title_no=9,csv=csv,cols=['Bus_ID','Alert frequency'])


if __name__ == '__main__':
    app.run(debug=True)
