import pandas as pd
import time
from scipy import stats
from statsmodels.stats import weightstats as stests
from statsmodels.stats.proportion import proportions_ztest
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import math
from datetime import datetime
from geopy.geocoders import Nominatim

xls=pd.ExcelFile('DataInAction.xlsx')

def basic_analysis_1():
	df1=pd.read_excel(xls,'AlertData')
	df2=pd.read_excel(xls,'FuelInfo')
	print(str(len(set(df1['deviceId']))) + ' devices in AlertData')
	print(str(len(set(df2['VehicleId']))) + ' devices in FuelInfo')

def basic_analysis_2():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    dict_ = {}
    df1_group_by = df1.groupby(['deviceId'],as_index=False)
    for x in df1_group_by:
        dict_[x[0]] = x[1]
    for bus,val in dict_.items():
        print(bus)
        x = val.iloc[[0,-1]]['recorded_at_date']
        print('Start date : ',x.iloc[0])
        print('End date : ',x.iloc[1])
        print('-------------------------------------------------------------------------------------------------------------------')

def basic_analysis_3():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    for bus in df2['VehicleId'].unique():
        df = df2[(df2['VehicleId']==bus) & (df2['Total Distance']!=np.nan)]
        sumdist=0
        for i in df['Total Distance'].values:
            if not np.isnan(i):
                sumdist+=i
        print(bus,':',sumdist)

def basic_analysis_4():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    mils = []
    for i in df2['Mileage'].values :
        if not np.isnan(i):
            mils.append(i)
    print(np.average(mils))

def basic_analysis_5():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df = df1 = df2
    for bus in df['VehicleId'].unique():
        df = df1[(df1['VehicleId']==bus)]
        mils=[]
        for i in df['Mileage'].values :
            if not np.isnan(i):
                mils.append(i)
        print(bus,":",np.average(mils))

def basic_analysis_6():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    dict_ = {}
    # dict_ is a dictionary {'bus_id': info grouped by hours}
    df1_group_by = df1.groupby(['deviceId'],as_index=False)
    hrs = df1['recorded_at_time']
    hrs = list(map(int, list(map(lambda k : k[0]+k[1], hrs))))
    df1['hrs'] = hrs
    for x in df1_group_by:
        dict_[x[0]] = x[1]
    for bus,val in dict_.items():
        dict_[bus] = val.groupby(['hrs'])
    for bus,hrs in dict_.items():
        l = []
        i = 0
        for x in hrs:
            l.append((i,len(x[1])))
            i+=1
        # finding the hour during which maximum alerts were generated
        max_hr = max(l,key=lambda x:x[1])[0]
        low = str(max_hr)+':00'
        high = str(max_hr+1)+':00'
        t = time.strptime(low, "%H:%M")
        low = time.strftime( "%I:%M %p", t )
        t = time.strptime(high, "%H:%M")
        high = time.strftime( "%I:%M %p", t )
        print(bus, low[:2], low[-2:], 'to',high[:2], high[-2:])



def hypothesis_testing_1():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    #Chi squared test for Homogeneity - Distribution of Alarm types across  different buses
    cont =pd.crosstab(df1['deviceId'], 
                                df1['alarmType'],  
                                   margins = False) 
    chi,pval,dof,expected=stats.chi2_contingency(cont)
    print(chi,expected,cont)
    print('Since chi-squared stat is very high, we can reject null hypo that alarm types are identically distributed among the buses.')
    # distribution plot
    df1.groupby(['deviceId','alarmType']).size().unstack().plot(kind = 'bar',stacked=False,figsize=(8,8))
    plt.show()
    

def hypothesis_testing_2():
    #pre requirements
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    hr = df1['recorded_at_time'].str.slice(0,2)
    df1['hour'] = hr

    #Chi squared test for Homogeneity - Distribution of Alarm types across hours
    cont =pd.crosstab(df1['alarmType'], 
                                hr,  
                                   margins = False) 
    chi,pval,dof,expected=stats.chi2_contingency(cont)
    #print(chi,expected,cont)
    print(chi)
    print('Null hypothesis is rejected. Thus alarm types and hours are dependent')
    # distribution plot
    df1.groupby(['hour','alarmType']).size().unstack().plot(kind = 'bar',stacked=False,figsize=(8,8))
    plt.show()

def hypothesis_testing_3():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df = df2.dropna()
    hrs = df['Duration(in milliseconds)']/3600000
    speeds = df['Total Distance']/hrs
    df['Avg speed'] = speeds

    df = df[df['Avg speed'] < 60]

    #Alternate : Average mileage is < 3.5kmpl for buses whose avg speeds are lesser than 60kmph
    #H0 : μ >= 3.5, H1 : μ < 3.5
    zstat ,pval = stests.ztest(x1=df['Mileage'],value=3.5,alternative='smaller')
    print(pval)
    print('As the pval is less than .05, we can conclude that avg mileage is < 3.5 kmpl for buses whose avg speeds are < 60kmph')
    print('With avg speeds being lesser than 60kmph, avg mileage you get is less than 3.5kmpl implying that speeds have to be lesser than 60 to achieve greater mileage')
    print('By trying various combinations, we came to the conclusion that if drivers maintain avg speed @40, theyll get avg mileage as >= 3.5')

def hypothesis_testing_4():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    #H1:Mean mileage of buses that travel > 100km is greater than 2.5kmpl
    df=df2[df2['Total Distance'] >=100]
    df=df.dropna()
    zstat ,pval = stests.ztest(x1=df['Mileage'],value=2.5,alternative='larger')
    print(pval)
    if pval<0.05:
        print("Reject null hypothesis")
    else:
        print("accept null hypothesis")

def hypothesis_testing_5():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    #pre requirements
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
    print(pval)
    if(pval < 0.05):
        print('Null hypothesis is rejected and hence the bus is driven by careless drivers')
    else:
        print('Bus drivers are careful')

def visualization1():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df1.groupby(['deviceId','alarmType']).size().unstack().plot(kind = 'bar',stacked=False,figsize=(8,8))
    plt.show()

def visualization2_1():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df = df1
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
    plt.xticks(range(len(ls)), ls,rotation=90,fontsize=20)
    plt.yticks(range(0,8500,500))
    plt.ylabel('device id')
    plt.xlabel('frequency')
    plt.title("frequency count of FCW alarm from 6am to 6pm")
    plt.rcParams['figure.figsize'] = (80.0, 50.0)
    plt.show()

def visualization2_2():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df = df1
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
    plt.show()

def visualization3():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df = df1
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
    plt.show()

def visualization4():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df1_group_by = df1.groupby(['deviceId'],as_index=False)
    buses = []
    avg_speeds = []
    for x in df1_group_by:
        buses.append(x[0])
        avg_speeds.append(x[1]['speed'].mean())
    plt.bar(buses,avg_speeds)
    plt.xticks(buses, rotation=90)
    plt.ylabel('avg speed')
    plt.show()

def visualization5():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df1_group_by = df1.groupby(['deviceId'],as_index=False)
    buses = []
    max_speeds = []
    for x in df1_group_by:
        buses.append(x[0])
        max_speeds.append(x[1]['speed'].max())
    plt.bar(buses,max_speeds)
    plt.xticks(buses, rotation=90)
    plt.ylabel('max speed')
    plt.show()

def visualization6():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df = df1
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
    plt.show()

def visualization7_1():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df = df1
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
    plt.show()

def visualization7_2():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df = df1
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
    plt.show()

def visualization7_3():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df = df1
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
    plt.show()

def visualization8_1():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df = df1
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
    plt.show()

def visualization8_2():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df = df1
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
    plt.show()

def visualization8_3():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df = df1
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
    plt.show()

def visualization9(busid):
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df = df1
    busdf = df1.loc[df['deviceId']==busid]  
    busdf.to_csv(busid + '.csv')
    df = pd.read_csv(busid + '.csv')
    df = df.sort_values(['latitude','longitude'])
    #adding coordinates as tuples to a lat_long list
    lat_long = []
    for i in range(len(df)):
        lat_long.append((df['latitude'][i],df['longitude'][i]))
    print(len(lat_long))
   
    lat_long_city = []
    geolocator = Nominatim(user_agent="my-application")
   
    i=1;k=0
    for i in range(1377,1677):
        try:
            location = geolocator.reverse(lat_long[i])
            d = location.raw['address']
            lat_long_city.append((t[0],t[1],d['state_district']))
            k+=1
            print(i,k,(t[0],t[1],d['state_district']))
        except:
            lat_long_city.append((t[0],t[1],np.nan))
            print('Getting null')
        i+=1
       
    df = df.replace('கோயம்புத்தூர் மாவட்டம்','Coimbatore')
    chart = sns.countplot(df['District'])
    chart.set_xticklabels(chart.get_xticklabels(), rotation=90, horizontalalignment='right')

def visualization10():
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    plt.hist(df1['speed'])
    plt.show()

def visualization11(alarmType):
    df1=pd.read_excel(xls,'AlertData')
    df2=pd.read_excel(xls,'FuelInfo')
    df1 = df1[df1['alarmType']==alarmType]
    plt.hist(df1['speed'])
    plt.title('Distribution for '+alarmType)
    plt.show()
