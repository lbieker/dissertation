# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib
import os, sys
import numpy as np
import subprocess
import seaborn as sns
import pandas as pd
from scipy.stats import ttest_ind

import math

def roundup(x):
    return int(round(x / 200.0)) * 200

XML2CSV= True
flows= [1,400,800,1200,1600,2000,2200,2400,2600,2800]#,2000,2200]
output= file('results_pandas.csv' , 'w')
output.write('run,flow,duration,waitingtime,timeloss,ev,method,start,delay,flowl\n')
fn='corridor100_results'
titlen= u'bei einem Korridor (100 Meter)'
counterflow= 8.0
skip= 325

methods= ['without', 'fast', 'stream', 'walabi100']#['fast' , 'walabi', 'stream', 'without']
methodsLabel= ['Ohne Vorfahrt', 'FAST', 'Stream','Walabi']# ['FAST', 'Walabi', 'Stream', 'Ohne Vorfahrt']
#methodsLabel= ['FAST', 'Walabi', 'Stream', 'without application']
index=-1
for method in methods:
    index +=1
    for flow in flows:
        runs= range(50)
        meanDurations= []
        meanWait= []
        meanTimeLoss= []
        evD= []
        evW=[]
        evT=[]
        routes= "routedist2"

        for run in runs:
            if XML2CSV:
                xmlProcess = subprocess.Popen("python C:\\sumo-git\\sumo\\tools\\xml\\xml2csv.py %s_corridor_%s\\tripinfos%s_%s.xml" % (method, flow, run, routes), shell=True, stdout=sys.stdout)
                xmlProcess.wait()
                
            #vehicle count
            input= file('%s_corridor_%s\\tripinfos%s_%s.csv' % (method,flow, run, routes), 'r')
            data=str(input.readline())
            vehicleNum= 0
            while True:
                data=str(input.readline())
                if not data:
                    break
                vehicleNum += 1
            input.close()
            #file durch lesen
            vehicleNum = roundup(vehicleNum) /counterflow#flow/4.0#roundup(vehicleNum) /4.0
            flowl= flow/8.0
            if vehicleNum >1400:
                print('%s,%s' %(run, flow))
            input= file('%s_corridor_%s\\tripinfos%s_%s.csv' % (method,flow, run, routes), 'r')
            durations= []
            wait=  []
            timeLoss= []
            data=str(input.readline())
            evStart= 100000
            while True:
                data=str(input.readline())
                if not data:
                    break
                data=data.split(';')
                duration= float(data[10])
                waitingtime= float(data[20])
                loss= float(data[16])
                
                #alt
                durations.append(float(data[10]))
                wait.append(float(data[20]))
                timeLoss.append(float(data[16]))
                if data[11]== "emergency":
                    evD.append(float(data[10]))
                    evW.append(float(data[20]))
                    evT.append(float(data[16]))
                    evStart=float(data[4])
                    output.write('%s,%s,%s,%s,%s,1,%s,%s,%s,%s\n' %(run, vehicleNum,duration, waitingtime, loss,methodsLabel[index],data[4],data[5], flowl))
                else:
                    if float(data[4]) > evStart and float(data[4]) < (evStart + 900):
                        output.write('%s,%s,%s,%s,%s,0,%s,%s,%s,%s\n' %(run, vehicleNum,duration, waitingtime, loss,methodsLabel[index],data[4],data[5],flowl))
            meanDurations.append(np.mean(durations))
            meanWait.append(np.mean(wait))
            meanTimeLoss.append(np.mean(timeLoss))
            
        print(np.mean(meanDurations),np.mean(evD))


output.close()

datapanda= pd.read_csv('results_pandas.csv')
print datapanda.head()


ev_demand= datapanda.loc[datapanda['ev'] == 1]
ev= ev_demand.loc[ev_demand['flow'] <= skip]
datapanda= datapanda.loc[datapanda['flow'] <= skip]
#print(datapanda.loc[datapanda['ev'] == 1])
#print ev.head()
ax= sns.lineplot(x="flow", y="duration",  hue="method", data= ev)
ax.set(xlabel=u'Traffic volume per lane (vehicles/hour)', ylabel='Average travel time (seconds)')
ax.set_title(u'Comparison of prioritization algorithms for emergency vehicles \n at a simple intersection')
legend = ax.legend()
legend.texts[0].set_text("Approach")
plt.savefig(fn+'.png', dpi=400)
plt.close()

sns.lineplot(x="flow", y="duration", hue="method", data= datapanda)
plt.savefig(fn+'_all.png', dpi=400)
plt.close()

#result = ev.pivot(columns='flow', values='duration')
#sns.heatmap(result, annot=True, fmt="g", cmap='viridis')
sns.boxenplot(x="flow", y="duration", hue="method", data=ev, linewidth=2.5)
#sns.stripplot(x="flow", y="duration", data=ev, hue="method", size=4, jitter=True, color="gray")
plt.savefig(fn+'_boxenplot.png', dpi=400)
plt.close()


sns.violinplot(x="flow", y="duration", data=ev, hue="method", inner="points")
plt.savefig(fn+'_violinplot.png', dpi=400)
plt.close()

sns.jointplot(x="flow", y="duration", kind="hex", data=datapanda)
plt.savefig(fn+'_hex_alltraffic.png', dpi=400)
plt.close()

#histo= ev.hist(bins=10, column="waitingtime")
#print histo.head()
sns.distplot(ev['waitingtime'], kde=False)
plt.savefig(fn+'_histogramm.png', dpi=400)
plt.close()

g = sns.FacetGrid(ev, col="method", margin_titles=True)
bins = np.linspace(0, 600, 100)
g.map(plt.hist, "waitingtime", color="steelblue", bins=bins)
plt.savefig(fn+'_facegrid.png', dpi=400)
plt.close()

#german plots



fig, ax=plt.subplots()
ax.set( yscale='log')#xscale='log',
lines= sns.lineplot(x="flow", y="duration", hue="method", data= datapanda).get_lines()
ax.set(xlabel=u'Verkehrsstärke pro Spur (Fahrzeuge/Stunde)', ylabel='Durchschnittliche Reisezeit (Sekunden)')
ax.set_title(u'Vergleich der Reisezeit des Gesamtverkehrs  \n '+titlen)
legend = ax.legend()
legend.texts[0].set_text("Ansatz")
plt.savefig(fn+'_deu_all.png', dpi=400)
plt.close()

data= []
xticks= []
for line in lines:
    data.append(line.get_data()[1])
    xticks.append(line.get_data()[0])
    print line.get_data()
text= ['FAST', 'Walabi', 'Stream']
for i in range(3):
    ax=sns.lineplot(x=xticks[i], y=data[3]-data[i], label= text[i])
ax.set(xlabel=u'Verkehrsstärke pro Spur (Fahrzeuge/Stunde)', ylabel=u'Durchschnittliche Änderung der Reisezeit (Sekunden)')
ax.set_title(u'Durchschnittliche Änderung der Reisezeit des Gesamtverkehrs \n '+titlen)
plt.savefig(fn+'_deu_all_abweichung.png', dpi=400)
plt.close()

for i in range(3):
    ax=sns.lineplot(x=xticks[i], y=((data[3]-data[i])/data[3] )*100, label= text[i])
    
#cat1 = datapanda[datapanda['Category']=='cat1']
#cat2 = datapanda[datapanda['Category']=='cat2']

#print ttest_ind(cat1['duration'], cat2['duration'])

ax.set(xlabel=u'Verkehrsstärke pro Spur (Fahrzeuge/Stunde)', ylabel=u'Durchschnittliche Änderung der Reisezeit (%)')
ax.set_title(u'Durchschnittliche Änderung der Reisezeit des Gesamtverkehrs \n '+titlen)
plt.savefig(fn+'_deu_all_abweichung_prozent.png', dpi=400)
plt.close()

#result = ev.pivot(columns='flow', values='duration')
#sns.heatmap(result, annot=True, fmt="g", cmap='viridis')
ax=sns.boxenplot(x="flow", y="duration", hue="method", data=ev, linewidth=2.5)
ax.set(xlabel=u'Verkehrsstärke pro Spur (Fahrzeuge/Stunde)', ylabel='Durchschnittliche Reisezeit (Sekunden)')
ax.set_title(u'Vergleich von Priorisierungsalgorithmen  für Einsatzfahrzeuge \n '+titlen)
legend = ax.legend()
#legend.texts[0].set_text("Ansatz")
#sns.stripplot(x="flow", y="duration", data=ev, hue="method", size=4, jitter=True, color="gray")
plt.savefig(fn+'_boxenplot_deu.png', dpi=400)
plt.close()


ax=sns.violinplot(x="flow", y="duration", data=ev, hue="method", inner="points")
ax.set(xlabel=u'Verkehrsstärke pro Spur (Fahrzeuge/Stunde)', ylabel='Durchschnittliche Reisezeit (Sekunden)')
ax.set_title(u'Vergleich von Priorisierungsalgorithmen  für Einsatzfahrzeuge \n '+titlen)
legend = ax.legend()
#legend.texts[0].set_text("Ansatz")
plt.savefig(fn+'_violinplot_deu.png', dpi=400)
plt.close()

ax=sns.jointplot(x="flow", y="duration", kind="hex", data=datapanda)
ax.set_axis_labels(x=u'Verkehrsstärke pro Spur (Fahrzeuge/Stunde)', y='Durchschnittliche Reisezeit (Sekunden)')
#plt.title(u'Vergleichvon Priorisierungsalgorithmen  für Einsatzfahrzeuge \n '+titlen)
#legend = ax.legend()
#legend.texts[0].set_text("Ansatz")
#ax.legend("Ansatz")
#ax = ax.annotate(["Ansatz"])
plt.savefig(fn+'_hex_alltraffic_deu.png', dpi=400)
plt.close()

#histo= ev.hist(bins=10, column="waitingtime")
#print histo.head()
ax=sns.distplot(ev['waitingtime'], kde=False)
ax.set(xlabel=u'Verkehrsstärke pro Spur (Fahrzeuge/Stunde)', ylabel='Durchschnittliche Reisezeit (Sekunden)')
ax.set_title(u'Vergleich von Priorisierungsalgorithmen für Einsatzfahrzeuge \n '+titlen)
legend = ax.legend()
#legend.texts[0].set_text("Ansatz")
plt.savefig(fn+'_histogramm_deu.png', dpi=400)
plt.close()

#g = sns.FacetGrid(ev, col="method", margin_titles=True)
#bins = np.linspace(0, 600, 100)
#n, bins, patches = ax.hist(datapanda.groupby('method').waitingtime, 60, density=1)
#ax.hist(datapanda.groupby('method'))
#datapanda.groupby('method').waitingtime.hist(alpha=0, fc= None)
#ax.bar(x - width/2, men_means, width, label='Men')
#ax=sns.distplot(datapanda.groupby('method').waitingtime, bins=20)
#g = sns.catplot(x="waitingtime", y="method", data=datapanda, kind="bar")
#sns.lineplot(x="waitingtime", hue="method", data= datapanda)
#g.map(plt.hist, "waitingtime", color="steelblue", bins=bins)
df = datapanda[datapanda.method == 'Ohne Vorfahrt']
sns.distplot(df['waitingtime'], hist = False, kde = True, label='Ohne Vorfahrt')
df = datapanda[datapanda.method == 'FAST']
sns.distplot(df['waitingtime'], hist = False, kde = True, label='FAST')
df = datapanda[datapanda.method == 'Stream']
sns.distplot(df['waitingtime'], hist = False, kde = True, label='Stream')
df = datapanda[datapanda.method == 'Walabi']
sns.distplot(df['waitingtime'], hist = False, kde = True, label='Walabi')
# Plot formatting
plt.legend(prop={'size': 12})
plt.title('Verteilung der Wartezeiten aller Verkehrsteilnehmer ')
plt.xlabel('Wartezeit (Sekunden)')
plt.ylabel(u'Häufigkeit')  

plt.savefig(fn+'_facegrid_deu.png', dpi=400)
plt.close()

g = sns.FacetGrid(datapanda, col="method", margin_titles=True)
bins = np.linspace(0, 500, 50)
(g.map(plt.hist, "waitingtime", color="steelblue", bins=bins, density= True).set_titles("{col_name}"))
plt.savefig(fn+'_facegrid_all_deu.png', dpi=400)
plt.close()


#output.write('%s;%s;%s;%s;%s;%s/n'%(meanDurations, meanWait, meanTimeLoss, evD, evW, evT))

# all traffic nur um die zeit des Einsatzfahrzeuges

#To select rows whose column value is in list 
ax=sns.boxenplot(x="flow", y="duration", hue="method", data=datapanda[datapanda.flow.isin([50.0, skip])], linewidth=2.5)
#lines= sns.lineplot(x="flow", y="duration", hue="method", data= datapanda).get_lines()
ax.set(xlabel=u'Verkehrsstärke pro Spur (Fahrzeuge/Stunde)', ylabel='Reisezeit (Sekunden)')
ax.set_title(u'Vergleich des Umgebungsverkehrs \n '+titlen)
legend = ax.legend()
#legend.texts[0].set_text("Ansatz")
plt.savefig(fn+'_deu_allselected.png', dpi=400)
plt.close()

#matplotlib.rcParams.update({'font.size': 18})
#fig, ax = plt.subplots(figsize=(16,9))
fig, ax=plt.subplots()
ax.set( yscale='log')#xscale='log',
sns.lineplot(x="flow", y="duration",  hue="method", data= ev)
ax.set(xlabel=u'Verkehrsstärke pro Spur (Fahrzeuge/Stunde)', ylabel='Durchschnittliche Reisezeit (Sekunden)')
ax.set_title(u'Vergleich von Priorisierungsalgorithmen für Einsatzfahrzeuge \n '+titlen)
legend = ax.legend()
legend.texts[0].set_text("Ansatz")
plt.savefig(fn+'_deu.png', dpi=400)
plt.close()

fig, ax=plt.subplots()
ax.set( yscale='log')#xscale='log',
sns.lineplot(x="flowl", y="duration",  hue="method", data= ev_demand)
ax.set(xlabel=u'Verkehrsnachfrage pro Spur (Fahrzeuge/Stunde)', ylabel='Durchschnittliche Reisezeit (Sekunden)')
ax.set_title(u'Vergleich von Priorisierungsalgorithmen für Einsatzfahrzeuge \n '+titlen)
legend = ax.legend()
legend.texts[0].set_text("Ansatz")
#ax = g.ax_joint
#ax.set_yscale('log')

#g.ax_marg_x.set_xscale('log')
#g.ax_marg_y.set_yscale('log')

plt.savefig(fn+'_demand_deu.png', dpi=400)
plt.close()


sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

# Initialize the FacetGrid object
pal = sns.cubehelix_palette(4, rot=-.25, light=.7)
g = sns.FacetGrid(datapanda.loc[datapanda["waitingtime"] <= 80], row="method", hue="method", aspect=3,  palette=pal)#height=.5, 

# Draw the densities in a few steps
g.map(sns.kdeplot, "waitingtime", clip_on=False, shade=True, alpha=1, bw=1)#, lw=1.5, bw=.2)
g.map(sns.kdeplot, "waitingtime", clip_on=False, color="w", bw=1)#, lw=2, bw=.2)
g.map(plt.axhline, y=0,  clip_on=False)#lw=2,

# Define and use a simple function to label the plot in axes coordinates
def label(x, color, label):
    ax = plt.gca()
    ax.text(1, .6, label, fontweight="bold", color=color,
            ha="right", va="center",fontsize=16, transform=ax.transAxes)


g.map(label, "waitingtime")

# Set the subplots to overlap
g.fig.subplots_adjust(hspace=-.25)

# Remove axes details that don't play well with overlap
g.set_titles("")
g.set(yticks=[0])
g.set_xlabels("Wartezeit (s)",  fontweight="bold", fontsize= 14)
g.despine(bottom=True, left=True)
g.fig.suptitle("Verteilung der Wartezeiten des Gesamtverkehrs\n "+ titlen, fontsize= 16, fontweight="bold")
plt.savefig(fn+'_ridgeplot.png', dpi=400)
plt.close()

