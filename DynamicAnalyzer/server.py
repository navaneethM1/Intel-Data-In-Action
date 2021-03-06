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
import datetime
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

@app.route('/hypo5')
def hypo5():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[1]
    df2 = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    df=df2[df2['Total Distance'] >=100]
    df=df.dropna()
    zstat ,pval = stests.ztest(x1=df['Mileage'],value=2.5,alternative='larger')
    return render_template('hypo.html', title_no=5, title='Z test on the mean Mileage in order to explore the relationship between distance and mileage', null="Mean mileage of buses that travel > 100km is <= 2.5kmpl", alternate="Mean mileage of buses that travel > 100km is > 2.5kmpl", pvalue=pval)



@app.route('/hypo4')
def hypo4():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df1 = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    df1_group_by = df1.groupby(['deviceId'],as_index=False)
    l=[]
    for x in df1_group_by:
        l.append(x)
    l[1][1].to_csv(l[1][0]+'.csv')
    df = pd.read_csv('12DF03C6:19523068255842304686.csv')
    df = df.loc[df['alarmType'] == 'PCW']
    no_of_trials = len(df)
    no_of_success = len(df.loc[df['speed'] > 30])

    #hypo 2
    #Proportion of times the bus(id = 12DF03C6:19523068255842304686) has crossed 30kmph is less than or equal to 0.4
    #NULL HYP : p <= 0.4 ALT HYP : p > 0.4
    stat, pval = proportions_ztest(no_of_success, no_of_trials, 0.4, alternative = 'larger')
    return render_template('hypo.html', title_no=4, title='Proportion of times a bus has crossed 30kmph during PCW alerts', null="Proportion of times the bus(id = 12DF03C6:19523068255842304686) has crossed 30kmph <= 0.4 during the time alert is generated", alternate="Proportion of times the bus(id = 12DF03C6:19523068255842304686) has crossed 30kmph > 0.4 during the time alert is generated", pvalue=pval)


@app.route('/visualization1')
def visualization1():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df1 = df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    df1.groupby(['deviceId','alarmType']).size().unstack().plot(kind = 'bar',stacked=False,figsize=(8,8))
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual1.jpeg')
    plt.close()
    return render_template('basicVisual.html', title_no='1', title='Distribution of Alert frequencies across devices', fig='basicVisual1.jpeg', caption='Distribution of Alert frequencies across devices')



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
        date_obs=datetime.datetime(d[0],d[1],d[2],t[0],t[1],t[2])
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

    plt.savefig(os.getcwd() + '/static/' + 'basicVisual2_1.jpeg')
    plt.close()
    return render_template('basicVisual.html', title_no='2_1', title='Frequency of FCW from 6am to 6pm', fig='basicVisual2_1.jpeg', caption='Frequency of FCW from 6am to 6pm')


@app.route('/visualization2_2')
def visualization2_2():
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
        date_obs=datetime.datetime(d[0],d[1],d[2],t[0],t[1],t[2])
        date_objs.append(date_obs)

    device_id=df["deviceId"].values
    alarm_type=df["alarmType"].values
    speed=df["speed"].values
    d2={}
    for i in range(len(df)):
        if device_id[i] not in d2:
            d2[device_id[i]]=[]
            d2[device_id[i]].append(0)
        if alarm_type[i]=="HMW" and date_objs[i].hour>6 and date_objs[i].hour<18:
            d2[device_id[i]][0]+=1

    d3={}
    for i in range(len(df)):
        if device_id[i] not in d3:
            d3[device_id[i]]=[]
        if alarm_type[i]=="HMW" and date_objs[i].hour>6 and date_objs[i].hour<18:
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

    p1=plt.bar(range(len(ls)),ls1,0.42,color='blue')
    plt.xticks(range(len(ls)), ls,rotation=90,fontsize=20)
    plt.yticks(range(0,8500,500))
    plt.ylabel('device id')
    plt.xlabel('frequency')
    plt.title("frequency count of HMW alarm from 6am to 6pm")
    plt.rcParams['figure.figsize'] = (80.0, 50.0)

    plt.savefig(os.getcwd() + '/static/' + 'basicVisual2_2.jpeg')
    plt.close()
    return render_template('basicVisual.html', title_no='2_2', title='Frequency of FCW from 6pm to 6am', fig='basicVisual2_2.jpeg', caption='Frequency of FCW from 6pm to 6am')


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
        date_obj = datetime.datetime(d[0],d[1],d[2],t[0],t[1],t[2])
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
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual3.jpeg')

    plt.close()
    return render_template('basicVisual.html', title_no='3', title='How many times HWM turned into FCW?', fig='basicVisual3.jpeg', caption='blue bar - day_count, orange bar - night_count')

def how_freq(buses, bus_index):
    start_index=buses[bus_index][1].index[0]
    bus_info = buses[bus_index][1]
    # print(len(bus_info))
    diff_in_minutes_list = []
    for i in range(start_index+1, len(bus_info)+start_index):
        date2 = list(map(int, bus_info['recorded_at_date'][i].split('-')))
        time2 = list(map(int, bus_info['recorded_at_time'][i].split(':')))
        final_date_2 = datetime.datetime.datetime(date2[0], date2[1], date2[2], time2[0], time2[1], time2[2])
        date1 = list(map(int, bus_info['recorded_at_date'][i-1].split('-')))
        time1 = list(map(int, bus_info['recorded_at_time'][i-1].split(':')))
        final_date_1 = datetime.datetime.datetime(date1[0], date1[1], date1[2], time1[0], time1[1], time1[2])
        diff = final_date_2 - final_date_1
        diff_in_minutes = diff.seconds/60
        diff_in_minutes_list.append(diff_in_minutes)
    avg = sum(diff_in_minutes_list)/len(diff_in_minutes_list)
    return 1/avg

@app.route('/visualization3_1')
def visualization3_1():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    df1 = df.groupby(['deviceId'],as_index=False)
    # How "frequently" buses generated alerts?
    buses = [x for x in df1]
    # print(len(buses[1][1]))
    avg_diffs = []
    bus_ids = []
    avgs = []
    for i in range(len(buses)):
        bus_ids.append(buses[i][0])
        avgs.append(how_freq(buses, i))
    sns.barplot(x=bus_ids, y=avgs)
    plt.xticks(rotation=90)
    plt.ylabel('Average number of alerts(/minute)')
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual3_1.jpeg')
    
    plt.close()
    return render_template('basicVisual.html', title_no='3_1', title='How "frequently" buses generated alerts?', fig='basicVisual3_1.jpeg', caption='How "frequently" buses generated alerts?')


@app.route('/visualization4')
def visualization4():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    df1 = df
    df1_group_by = df1.groupby(['deviceId'],as_index=False)
    buses = []
    avg_speeds = []
    for x in df1_group_by:
        buses.append(x[0])
        avg_speeds.append(x[1]['speed'].mean())
    plt.bar(buses,avg_speeds)
    plt.xticks(buses, rotation=90)
    plt.ylabel('avg speed')
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual4.jpeg')
    
    plt.close()
    return render_template('basicVisual.html', title_no='4', title='Average speed of buses', fig='basicVisual4.jpeg', caption='Average speed of buses')

@app.route('/visualization5')
def visualization5():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    df1 = df
    df1_group_by = df1.groupby(['deviceId'],as_index=False)
    buses = []
    max_speeds = []
    for x in df1_group_by:
        buses.append(x[0])
        max_speeds.append(x[1]['speed'].max())
    plt.bar(buses,max_speeds)
    plt.xticks(buses, rotation=90)
    plt.ylabel('max speed')
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual5.jpeg')
    
    plt.close()
    return render_template('basicVisual.html', title_no='5', title='Maximum speed of buses', fig='basicVisual5.jpeg', caption='Maximum speed of buses')


@app.route('/visualization6')
def visualization6():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    hour=df["recorded_at_hour"].values
    ap=df["AM/PM"].values
    for i in range(len(hour)):
        hour[i]=int(math.floor(hour[i]))
    d={}
    for i in range(24):
        d[i]=0
    for i in range(len(hour)):
        if ap[i]=="AM":
            if hour[i]==12:
                d[0]+=1
            else:
                d[hour[i]]+=1
        elif ap[i]=="PM":
            if hour[i]==12:
                d[12]+=1
            else :
                d[hour[i]+12]+=1

    l1=[]
    for i in range(len(d)):
        l1.append(d[i])
    l2=[]
    for i in d:
        l2.append(i)
    p1=plt.bar(range(len(l2)),l1,0.42,color='orange')
    plt.xticks(range(len(l2)), l2,fontsize=10)
    plt.yticks(range(0,max(l1)+500,500),fontsize=10)
    plt.ylabel('hour',fontsize=10)
    plt.xlabel('frequency',fontsize=10)
    plt.title("frequency count of alarm in the ith hour",fontsize=10)
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual6.jpeg')
    plt.close()
    return render_template('basicVisual.html', title_no=6, title='Frequency count of alarm in the ith hour', fig='basicVisual6.jpeg', caption='Frequency count of alarm in the ith hour')

@app.route('/visualization7_1')
def visualization7_1():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    alarm_type=df["alarmType"].values
    hour=df["recorded_at_hour"].values
    ap=df["AM/PM"].values
    for i in range(len(hour)):
        hour[i]=int(math.floor(hour[i]))
    d={}
    for i in range(24):
        d[i]=0

    for i in range(len(hour)):
        if ap[i]=="AM":
            if hour[i]==12:
                d[0]+=1
            else:
                d[hour[i]]+=1
        elif ap[i]=="PM":
            if hour[i]==12:
                d[12]+=1
            else :
                d[hour[i]+12]+=1
    d1={}
    d2={}
    d3={}
    d4={}
    d5={}
    for i in range(24):
        d1[i]=0
        d2[i]=0
        d3[i]=0
        d4[i]=0
        d5[i]=0

    for i in range(len(hour)):
        if ap[i]=="AM":
            if hour[i]==12:
                if alarm_type[i]=="HMW":
                    d3[0]+=1
            else:
                if alarm_type[i]=="HMW":
                    d3[hour[i]]+=1
        elif ap[i]=="PM":
            if hour[i]==12:
                if alarm_type[i]=="HMW":
                    d3[12]+=1
            else :
                if alarm_type[i]=="HMW":
                    
                    d3[hour[i]+12]+=1

    for i in range(len(hour)):
        if ap[i]=="AM":
            if hour[i]==12:
                if alarm_type[i]=="HMW":
                    d3[0]+=1
            else:
                if alarm_type[i]=="HMW":
                    d3[hour[i]]+=1
        elif ap[i]=="PM":
            if hour[i]==12:
                if alarm_type[i]=="HMW" :
                    d3[12]+=1
            else :
                if alarm_type[i]=="HMW":
                    d3[hour[i]+12]+=1
    l1=[]
    for i in range(len(d3)):
        l1.append(d3[i])
    l2=[]
    for i in d:
        l2.append(i)
    p1=plt.bar(range(len(l2)),l1,0.42,color='yellow')
    plt.xticks(range(len(l2)), l2)
    plt.yticks(range(0,max(l1)+500,500))
    plt.ylabel('frequency of HMW')
    plt.xlabel('hour')
    plt.rcParams['figure.figsize'] = (10,10)
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual7_1.jpeg')
    plt.close()
    return render_template('basicVisual.html', title_no=7, title='Frequency of HMW', fig='basicVisual7_1.jpeg', caption='Frequency of HMW')

@app.route('/visualization7_2')
def visualization7_2():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    alarm_type=df["alarmType"].values
    hour=df["recorded_at_hour"].values
    ap=df["AM/PM"].values
    for i in range(len(hour)):
        hour[i]=int(math.floor(hour[i]))
    d={}
    for i in range(24):
        d[i]=0

    for i in range(len(hour)):
        if ap[i]=="AM":
            if hour[i]==12:
                d[0]+=1
            else:
                d[hour[i]]+=1
        elif ap[i]=="PM":
            if hour[i]==12:
                d[12]+=1
            else :
                d[hour[i]+12]+=1
    d1={}
    d2={}
    d3={}
    d4={}
    d5={}
    for i in range(24):
        d1[i]=0
        d2[i]=0
        d3[i]=0
        d4[i]=0
        d5[i]=0

    for i in range(len(hour)):
        if ap[i]=="AM":
            if hour[i]==12:
                if alarm_type[i]=="FCW":
                    d3[0]+=1
            else:
                if alarm_type[i]=="FCW":
                    d3[hour[i]]+=1
        elif ap[i]=="PM":
            if hour[i]==12:
                if alarm_type[i]=="FCW":
                    d3[12]+=1
            else :
                if alarm_type[i]=="FCW":
                    
                    d3[hour[i]+12]+=1

    for i in range(len(hour)):
        if ap[i]=="AM":
            if hour[i]==12:
                if alarm_type[i]=="FCW":
                    d3[0]+=1
            else:
                if alarm_type[i]=="FCW":
                    d3[hour[i]]+=1
        elif ap[i]=="PM":
            if hour[i]==12:
                if alarm_type[i]=="FCW" :
                    d3[12]+=1
            else :
                if alarm_type[i]=="FCW":
                    d3[hour[i]+12]+=1
    l1=[]
    for i in range(len(d3)):
        l1.append(d3[i])
    l2=[]
    for i in d:
        l2.append(i)
    p1=plt.bar(range(len(l2)),l1,0.42,color='green')
    plt.xticks(range(len(l2)), l2)
    plt.yticks(range(0,max(l1)+500,500))
    plt.ylabel('frequency of FCW')
    plt.xlabel('hour')
    plt.rcParams['figure.figsize'] = (10,10)
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual7_2.jpeg')
    plt.close()
    return render_template('basicVisual.html', title_no=8, title='Frequency of FCW', fig='basicVisual7_2.jpeg', caption='Frequency of FCW')

@app.route('/visualization7_3')
def visualization7_3():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    alarm_type=df["alarmType"].values
    hour=df["recorded_at_hour"].values
    ap=df["AM/PM"].values
    for i in range(len(hour)):
        hour[i]=int(math.floor(hour[i]))
    d={}
    for i in range(24):
        d[i]=0

    for i in range(len(hour)):
        if ap[i]=="AM":
            if hour[i]==12:
                d[0]+=1
            else:
                d[hour[i]]+=1
        elif ap[i]=="PM":
            if hour[i]==12:
                d[12]+=1
            else :
                d[hour[i]+12]+=1
    d1={}
    d2={}
    d3={}
    d4={}
    d5={}
    for i in range(24):
        d1[i]=0
        d2[i]=0
        d3[i]=0
        d4[i]=0
        d5[i]=0

    for i in range(len(hour)):
        if ap[i]=="AM":
            if hour[i]==12:
                if alarm_type[i]=="PCW":
                    d3[0]+=1
            else:
                if alarm_type[i]=="PCW":
                    d3[hour[i]]+=1
        elif ap[i]=="PM":
            if hour[i]==12:
                if alarm_type[i]=="PCW":
                    d3[12]+=1
            else :
                if alarm_type[i]=="PCW":
                    
                    d3[hour[i]+12]+=1

    for i in range(len(hour)):
        if ap[i]=="AM":
            if hour[i]==12:
                if alarm_type[i]=="PCW":
                    d3[0]+=1
            else:
                if alarm_type[i]=="PCW":
                    d3[hour[i]]+=1
        elif ap[i]=="PM":
            if hour[i]==12:
                if alarm_type[i]=="PCW" :
                    d3[12]+=1
            else :
                if alarm_type[i]=="PCW":
                    d3[hour[i]+12]+=1
    l1=[]
    for i in range(len(d3)):
        l1.append(d3[i])
    l2=[]
    for i in d:
        l2.append(i)
    p1=plt.bar(range(len(l2)),l1,0.42,color='blue')
    plt.xticks(range(len(l2)), l2)
    plt.yticks(range(0,max(l1)+500,500))
    plt.ylabel('frequency of PCW')
    plt.xlabel('hour')
    plt.rcParams['figure.figsize'] = (10,10)
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual7_3.jpeg')
    plt.close()
    return render_template('basicVisual.html', title_no=9, title='Frequency of PCW', fig='basicVisual7_3.jpeg', caption='Frequency of PCW')


@app.route('/visualization7_5')
def visualization7_5():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df1 = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    alarm_type=df1["alarmType"].values
    hour=df1["recorded_at_hour"].values
    ap=df1["AM/PM"].values

    for i in range(len(hour)):
        hour[i]=int(math.floor(hour[i]))

    df = {}
    df['type'] = []
    df['hour'] = []
    df['count'] = []
    d1={}
    d2={}
    d3={}
    d4={}
    d5={}
    for i in range(24):
        d1[i]=0
        d2[i]=0
        d3[i]=0
        d4[i]=0
        d5[i]=0
    for i in range(len(hour)):
        if ap[i]=="AM":
            if hour[i]==12:
                if alarm_type[i]=="FCW":
                    d1[0]+=1
                elif alarm_type[i]=="HMW":
                    d2[0]+=1
                elif alarm_type[i]=="PCW":
                    d3[0]+=1
                elif alarm_type[i]=="HB":
                    d5[0]+=1
            else:
                if alarm_type[i]=="FCW":
                    d1[hour[i]]+=1
                elif alarm_type[i]=="HMW":
                    d2[hour[i]]+=1
                elif alarm_type[i]=="PCW":
                    d3[hour[i]]+=1
                elif alarm_type[i]=="HB":
                    d5[hour[i]]+=1
        elif ap[i]=="PM":
            if hour[i]==12:
                if alarm_type[i]=="FCW":
                    d1[12]+=1
                elif alarm_type[i]=="HMW":
                    d2[12]+=1
                elif alarm_type[i]=="PCW":
                    d3[12]+=1
                elif alarm_type[i]=="HB":
                    d5[12]+=1
            else :
                if alarm_type[i]=="FCW":
                    d1[hour[i]+12]+=1
                elif alarm_type[i]=="HMW":
                    d2[hour[i]+12]+=1
                elif alarm_type[i]=="PCW":
                    d3[hour[i]+12]+=1
                elif alarm_type[i]=="HB":
                    d5[hour[i]+12]+=1

    for i in range(24):
        df['type'].append('FCW')
        df['hour'].append(i)
        df['count'].append(d1[i])
        df['type'].append('HMW')
        df['hour'].append(i)
        df['count'].append(d2[i])
        df['type'].append('PCW')
        df['hour'].append(i)
        df['count'].append(d3[i])
        df['type'].append('HB')
        df['hour'].append(i)
        df['count'].append(d5[i])
    data = pd.DataFrame(df)
    sns.scatterplot(x="hour", y="count", hue="type",
                         data=data)
    plt.xticks(range(24),range(24))
    plt.xlabel("Hour")
    plt.ylabel("Frequency")
    plt.rcParams['figure.figsize'] = (10,10)
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual7_4.jpeg')
    plt.close()
    return render_template('basicVisual.html', title_no=9, title='Frequency of Alerts', fig='basicVisual7_4.jpeg', caption='Frequency of Alerts')

@app.route('/visualization8_1')
def visualization8_1():
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
    plt.ylabel("speed",fontsize=10)
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual8_1.jpeg')
    plt.close()
    return render_template('basicVisual.html', title_no=10, title='Speed variation for FCW', fig='basicVisual8_1.jpeg', caption='Speed variation for FCW')

@app.route('/visualization8_2')
def visualization8_2():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    alarm_type=df["alarmType"].values
    speed=df["speed"].values
    ls1=[]
    for i in range(len(speed)):
        if alarm_type[i]=='HMW':
            ls1.append(speed[i])
    sns.set(style="whitegrid")
    ax = sns.boxplot(y=ls1,color="green")
    plt.yticks(fontsize=10)
    plt.xlabel("speed variation for HMW",fontsize=10)
    plt.ylabel("speed",fontsize=10)
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual8_2.jpeg')
    plt.close()
    return render_template('basicVisual.html', title_no=11, title='Speed variation for HMW', fig='basicVisual8_2.jpeg', caption='Speed variation for HMW')

@app.route('/visualization8_3')
def visualization8_3():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    alarm_type=df["alarmType"].values
    speed=df["speed"].values
    ls1=[]
    for i in range(len(speed)):
        if alarm_type[i]=='PCW':
            ls1.append(speed[i])
    sns.set(style="whitegrid")
    ax = sns.boxplot(y=ls1,color="green")
    plt.yticks(fontsize=10)
    plt.xlabel("speed variation for PCW",fontsize=10)
    plt.ylabel("speed",fontsize=10)
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual8_3.jpeg')
    plt.close()
    return render_template('basicVisual.html', title_no=12, title='Speed variation for PCW', fig='basicVisual8_3.jpeg', caption='Speed variation for PCW')


@app.route('/visualization10')
def visualization10():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df1 = df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    sns.distplot(df1['speed'])
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual10.jpeg')
    
    plt.close()
    return render_template('basicVisual.html', title_no='10', title='Distribution of alerts over speed-ranges', fig='basicVisual10.jpeg', caption='Distribution of alerts over speed-ranges')


@app.route('/visualization11_1')
def visualization11_1():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df1 = df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    alarmType = 'FCW'
    df1 = df1[df1['alarmType']==alarmType]
    sns.distplot(df1['speed']).set_title("Distribution for "+alarmType)
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual11_1.jpeg')
    
    plt.close()
    return render_template('basicVisual.html', title_no='11_1', title='Distribution of FCW over speed ranges', fig='basicVisual11_1.jpeg', caption='Distribution of FCW over speed ranges')

@app.route('/visualization11_2')
def visualization11_2():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df1 = df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    alarmType = 'PCW'
    df1 = df1[df1['alarmType']==alarmType]
    sns.distplot(df1['speed']).set_title("Distribution for "+alarmType)
    plt.savefig(os.getcwd() + '/static/' + 'basicVisual11_2.jpeg')
    
    plt.close()
    return render_template('basicVisual.html', title_no='11_2', title='Distribution of PCW over speed ranges', fig='basicVisual11_2.jpeg', caption='Distribution of PCW over speed ranges')
 

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
    plt.close()
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

@app.route('/distribution_of_alerts_over_time')
def v1():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    times = []
    for time in df['recorded_at_time'].values:
        times.append(float(time.split(':')[0]))
    df['Times']=times
    sns.distplot(df['Times'],color='brown').set_title('Distribution of alerts over time')
    plt.xlabel('Time')
    plt.savefig(os.getcwd() + '/static/' + 'v1.jpeg')
    
    plt.close()
    return render_template('basicVisual.html', title_no='10', title='Distribution of alerts over time', fig='v1.jpeg', caption='Distribution of alerts over time')

@app.route('/distribution_of_HMW_alerts_over_time')
def v2():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    times = []
    for time in df['recorded_at_time'].values:
        times.append(float(time.split(':')[0]))
    df['Times']=times
    df = df[df['alarmType']=='HMW']
    sns.distplot(df['Times'],color='brown').set_title('Distribution of HMW alerts over time')
    plt.xlabel('Time')
    plt.savefig(os.getcwd() + '/static/' + 'v2.jpeg')
    
    plt.close()
    return render_template('basicVisual.html', title_no='12', title='Distribution of HMW alerts over time', fig='v2.jpeg', caption='Distribution of HMW alerts over time')


@app.route('/distribution_of_PCW_alerts_over_time')
def v4():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    times = []
    for time in df['recorded_at_time'].values:
        times.append(float(time.split(':')[0]))
    df['Times']=times
    df = df[df['alarmType']=='PCW']
    sns.distplot(df['Times'],color='brown').set_title('Distribution of PCW alerts over time')
    plt.xlabel('Time')
    plt.savefig(os.getcwd() + '/static/' + 'v4.jpeg')
    
    plt.close()
    return render_template('basicVisual.html', title_no='12', title='Distribution of PCW alerts over time', fig='v4.jpeg', caption='Distribution of PCW alerts over time')

@app.route('/distribution_of_FCW_alerts_over_time')
def v3():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    times = []
    for time in df['recorded_at_time'].values:
        times.append(float(time.split(':')[0]))
    df['Times']=times
    df = df[df['alarmType']=='FCW']
    sns.distplot(df['Times'],color='brown').set_title('Distribution of FCW alerts over time')
    plt.xlabel('Time')
    plt.savefig(os.getcwd() + '/static/' + 'v3.jpeg')
    
    plt.close()
    return render_template('basicVisual.html', title_no='12', title='Distribution of FCW alerts over time', fig='v3.jpeg', caption='Distribution of FCW alerts over time')

import datetime
import matplotlib
@app.route('/alert freqs on diff days')
def v5():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    recorded_at_day=[]
    for i in range(len(df)):
        date = df['recorded_at_date'].values[i]
        items = date.split('-')
        index = datetime.datetime(int(items[0]),int(items[1]),int(items[2])).weekday()
        recorded_at_day.append(days[index])
    df['recorded_at_day']=recorded_at_day
    font = {'family' : 'normal',
    'size'   : 7}

    plt.rc('font', **font)
    sns.set()

    sns.countplot(df['recorded_at_day'],hue=df[
        'alarmType'])

    plt.savefig(os.getcwd() + '/static/' + 'v5.jpeg')
    
    plt.close()
    return render_template('basicVisual.html', title_no='12', title='Alert frequencies on different days of the week', fig='v5.jpeg', caption='')



@app.route('/avg speeds on diff days')
def v6():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    recorded_at_day=[]
    for i in range(len(df)):
        date = df['recorded_at_date'].values[i]
        items = date.split('-')
        index = datetime.datetime(int(items[0]),int(items[1]),int(items[2])).weekday()
        recorded_at_day.append(days[index])
    df['recorded_at_day']=recorded_at_day
    font = {'family' : 'normal','size'   : 7}

    plt.rc('font', **font)
    sns.set()

    avg_speeds={}
    for day in df['recorded_at_day'].unique():
        sdf = df[df['recorded_at_day']==day]
        avg_speeds[day]=np.average(sdf['speed'].values)
        
    plt.scatter(days,avg_speeds.values())
    axes = plt.gca()
    axes.set_ylim([35,45])
    plt.xlabel("Day")
    plt.ylabel("Average Speed")
    plt.savefig(os.getcwd() + '/static/' + 'v6.jpeg')
    
    plt.close()
    return render_template('basicVisual.html', title_no='12', title='Average bus speeds on different days of the week', fig='v6.jpeg', caption='')


@app.route('/dist of speeds on diff days')
def v7():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    recorded_at_day=[]
    for i in range(len(df)):
        date = df['recorded_at_date'].values[i]
        items = date.split('-')
        index = datetime.datetime(int(items[0]),int(items[1]),int(items[2])).weekday()
        recorded_at_day.append(days[index])
    df['recorded_at_day']=recorded_at_day
    font = {'family' : 'normal',
    'size'   : 7}

    plt.rc('font', **font)
    sns.set()

    sns.violinplot(x="recorded_at_day", y="speed", data=df)

    plt.savefig(os.getcwd() + '/static/' + 'v7.jpeg')
    
    plt.close()
    return render_template('basicVisual.html', title_no='12', title='Distribution of speeds on different days of the week', fig='v7.jpeg', caption='')

@app.route('/Day of the week and Time of the day')
def v8():
    files = os.listdir(os.getcwd() + '/static')
    csvfiles = [file for file in files if file.endswith('.csv')]
    csvfiles.sort()
    csvfile = csvfiles[0]
    df = pd.read_csv(os.getcwd() + '/static/' + csvfile)
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    recorded_at_day=[]
    for i in range(len(df)):
        date = df['recorded_at_date'].values[i]
        items = date.split('-')
        index = datetime.datetime(int(items[0]),int(items[1]),int(items[2])).weekday()
        recorded_at_day.append(days[index])
    df['recorded_at_day']=recorded_at_day
    font = {'family' : 'normal',
    'size'   : 7}

    plt.rc('font', **font)
    sns.set()

    sns.violinplot(x="recorded_at_day", y="recorded_at_hour", data=df)

    plt.savefig(os.getcwd() + '/static/' + 'v8.jpeg')
    
    plt.close()
    return render_template('basicVisual.html', title_no='12', title='Day of the week and Time of the day', fig='v8.jpeg', caption='')



if __name__ == '__main__':
    app.run(debug=True)