# -*- coding: utf-8 -*-
import matplotlib
import matplotlib.pyplot as plt
import os, sys
import numpy as np


def autolabel(scores, ax, y_pos):
    """
    Attach a text label above each bar in *rects*, displaying its height.

    *xpos* indicates which side to place the text w.r.t. the center of
    the bar. It can be one of the following {'center', 'right', 'left'}.
    """

    ypos = 'center'  # normalize the case of the parameter
    ha = {'center': 'center', 'right': 'left', 'left': 'right'}
    offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}  # x_txt = x + w*off
    i= 0
    for y in y_pos:
        ax.text(35,y - 0.3, str(round(scores[i], 1))+ '%')
        i += 1


def plotReasons(accidents):
    #analyse reasons
    reasons= {}
    numberAccidents= 0.0
    description= {'breaking': 'Abruptes Bremsen', 'turning': 'Abbiegen', 'oncoming traffic': 'Gegenverkehr', 'pedestrian': u'Kreuzender Fußgänger', 'rear-end collision': 'Auffahrunfall', 'Stop': 'Stoppschild', 'parking': 'Parken', 'misc': 'Sonstiges', 'Intention': 'Absicht', 'icy': u'Glätte', 'storm': 'Sturm', 'unknown': 'Unbekannte Ursache', 'Oneway': u'Einbahnstraße', 'intersection': 'Kreuzung', 'overtaking': u'Überholvorgang', 'red': 'Rote Lichtsignalanlage', 'alcohol': 'Alkohol'}
    for a in accidents:
        numberAccidents +=1
        if a[2] in reasons.keys():
            reasons[a[2]] += 1
        else:
            reasons[a[2]]= 1

    fig, ax = plt.subplots()
  
    outputFile= 'unfallsituation.png' 
    plt.title('Unfallsituation von Einsatzfahrzeugen (n= %s)' %int(numberAccidents))
    plt.ylabel(u'Gründe')
    plt.xlabel('Anteil [%]')
    labels= []
    #for k in reasons.keys():
    #    labels.append(description[k])
    performance= []
    #for v in reasons.values():
    #    performance.append(v /numberAccidents *100)
        
    #sort values in dict
    for key, value in sorted(reasons.iteritems(), key=lambda (k,v): (v,k)):
        labels.append(description[key])
        performance.append(value /numberAccidents *100)
    
    y_pos = np.arange(len(labels))
    scores= plt.barh(y_pos, performance, align='center', alpha=0.4)
    plt.subplots_adjust(left = 0.35, wspace = 0.2, hspace = 0.1)
    plt.yticks(y_pos, labels)
    autolabel(performance, ax, y_pos)    
    print performance
    plt.savefig(outputFile)
    plt.close(fig)
    
def plotInsured(accidents):
    #analyse reasons
    reasons= {}
    total= 0
    numberAccidents= 0.0
    description= {'breaking': 'Abruptes Bremsen', 'turning': 'Abbiegen', 'oncoming traffic': 'Gegenverkehr', 'pedestrian': u'Kreuzender Fußgänger', 'rear-end collision': 'Auffahrunfall', 'Stop': 'Stoppschild', 'parking': 'Parken', 'misc': 'Sonstiges', 'Intention': 'Absicht', 'icy': u'Glätte', 'storm': 'Sturm', 'unknown': 'Unknown reasons', 'Oneway': u'Einbahnstraße', 'intersection': 'Kreuzung', 'overtaking': u'Überholvorgang', 'red': 'Rote Lichtsignalanlage', 'alcohol': 'Alkohol'}
    for a in accidents:
        insured= 0
        serious= 0
        dead=0
        if a[6]!='':
            insured= int(a[6])
        if a[7]!='':    
            serious= int(a[7])
        if a[8]!='':
            dead= int(a[8])
        insured+= serious     
        if insured > 0:
            numberAccidents +=1
            total += insured
            if a[2] in reasons.keys():
                reasons[a[2]] += 1
            else:
                reasons[a[2]]= 1
    fig, ax = plt.subplots()

  
    outputFile= 'verletzt.png' 
    plt.title('Unfallsituationen mit verletzten Personen (n=%s)' %int(numberAccidents) )
    plt.ylabel(u'Gründe')
    plt.xlabel('Anteil [%]')
    labels= []
    #for k in reasons.keys():
    #    labels.append(description[k])
    performance= []
    #for v in reasons.values():
    #    performance.append(v /numberAccidents *100)
        
    #sort values in dict
    for key, value in sorted(reasons.iteritems(), key=lambda (k,v): (v,k)):
        labels.append(description[key])
        performance.append(value /numberAccidents *100)
    
    y_pos = np.arange(len(labels))
    plt.barh(y_pos, performance, align='center', alpha=0.4)
    plt.subplots_adjust(left = 0.35, wspace = 0.2, hspace = 0.1)
    plt.yticks(y_pos, labels)  
    print performance
    print total
    plt.savefig(outputFile)
    plt.close(fig) 
    
def plotDead(accidents):
    #analyse reasons
    reasons= {}
    total= 0
    numberAccidents= 0.0
    description= {'breaking': 'Abruptes Bremsen', 'turning': 'Abbiegen', 'oncoming traffic': 'Gegenverkehr', 'pedestrian': u'Kreuzender Fußgänger', 'rear-end collision': 'Auffahrunfall', 'Stop': 'Stoppschild', 'parking': 'Parken', 'misc': 'Sonstiges', 'Intention': 'Absicht', 'icy': u'Glätte', 'storm': 'Sturm', 'unknown': 'Unknown reasons', 'Oneway': u'Einbahnstraße', 'intersection': 'Kreuzung', 'overtaking': u'Überholvorgang', 'red': 'Rote Lichtsignalanlage', 'alcohol': 'Alkohol'}
    for a in accidents:
        dead=0
        if a[8]!='':
            dead= int(a[8]) 
        if dead > 0:
            total += dead
            numberAccidents +=1
            if a[2] in reasons.keys():
                reasons[a[2]] += 1
            else:
                reasons[a[2]]= 1
    fig, ax = plt.subplots()

  
    outputFile= 'tot.png' 
    plt.title(u'Unfallsituationen mit getöteten Personen (n=%s)' %int(numberAccidents))
    plt.ylabel(u'Gründe')
    plt.xlabel('Anteil [%]')
    labels= []
    #for k in reasons.keys():
    #    labels.append(description[k])
    performance= []
    #for v in reasons.values():
    #    performance.append(v /numberAccidents *100)
        
    #sort values in dict
    for key, value in sorted(reasons.iteritems(), key=lambda (k,v): (v,k)):
        labels.append(description[key])
        performance.append(value /numberAccidents *100)
    
    y_pos = np.arange(len(labels))
    plt.barh(y_pos, performance, align='center', alpha=0.4)
    plt.subplots_adjust(left = 0.35, wspace = 0.2, hspace = 0.1)
    plt.yticks(y_pos, labels)  
    print performance
    print total
    plt.savefig(outputFile)
    plt.close(fig)    
        
    
def plotVehicleTypes(accidents):
    #analyse types
    vtypes= {}
    numberAccidents= 0.0
    for a in accidents:
        numberAccidents +=1
        name= a[0].lower()
        if name.startswith("rettungswagen") or name.startswith("rtw") or name.startswith("krankenwagen"):
            name= "Rettungsdienst"
        elif name.startswith("polizei"):
            name= "Polizei"
        elif name.startswith("feuerwehr") :
            name= u"Lösch-\nfahrzeug"
        elif name.startswith("nef") or name.startswith("organtransport") or name.startswith("notarzt") or name.startswith("einsatztfahrzeug") or name.startswith("kurier") or name.startswith("notfallmanager"):
            name= "Sonstige"
        else: 
            print name
            numberAccidents -=1
            continue
        if name in vtypes.keys():
            vtypes[name] += 1.
        else:
            vtypes[name]= 1.

    fig, ax = plt.subplots(figsize=(10,6))
  
    outputFile= 'fahrzeugtyp.png' 
    plt.title('Involvierte Fahrzeugtypen (n= %s)' % int(numberAccidents) )
    #plt.ylabel('Vehicle Type')
    #plt.xlabel('Percentage [%]')
    labels= []

    performance= []
        
    #sort values in dict
    for key, value in sorted(vtypes.iteritems(), key=lambda (k,v): (v,k)):
        p=value /numberAccidents *100.
        labels.append(key )#+ '\n'+str(round(p,1)) + '%')
        performance.append(p)
    
    cmap = plt.get_cmap('tab20c')
    outer_colors = cmap(np.array([1, 5,  9, 13,17]))
    pies = ax.pie(performance, labels= labels, colors=outer_colors, autopct='%1.1f%%', wedgeprops   = { 'linewidth' : 1,'edgecolor' : "black" })
    
    
    # y_pos = np.arange(len(labels))
    # plt.barh(y_pos, performance, align='center', alpha=0.4)
    # plt.subplots_adjust(left = 0.35, wspace = 0.2, hspace = 0.1)
    # plt.yticks(y_pos, labels)  
    print performance
    plt.savefig(outputFile)
    plt.close(fig)    
  
def plotRoadTypes(accidents):
    #analyse types
    vtypes= {}
    numberAccidents= 0.0
    for a in accidents:
        
        name= a[12].lower()
        if name.startswith("innerorts") :
            name= "Innerorts"
        elif name.startswith("land") or name.startswith("ausserorts"):
            name= u'Landstraßen'
        elif name.startswith("autobahn") :
            name= "Autobahn"
        else: 
            print name
            continue
        numberAccidents +=1
        if name in vtypes.keys():
            vtypes[name] += 1.0
        else:
            vtypes[name]= 1.0

    fig, ax = plt.subplots(figsize=(10,6))
  
    outputFile= 'strassentypen.png' 
    plt.title(u'Straßentypen (n= %s)' % int(numberAccidents))
    #plt.ylabel('Vehicle Type')
    #plt.xlabel('Percentage [%]')
    labels= []

    performance= []
        
    #sort values in dict
    for key, value in sorted(vtypes.iteritems(), key=lambda (k,v): (v,k)):
        p=value /numberAccidents *100.0
        labels.append(key )#+ '\n'+str(round(p, 1)) + '%')
        performance.append(p)
    
    cmap = plt.get_cmap('tab20c')
    outer_colors = cmap(np.array([1, 5,  9, 13,17]))
    pies = ax.pie(performance, labels= labels, colors=outer_colors, autopct='%1.1f%%', wedgeprops   = { 'linewidth' : 1,'edgecolor' : "black" })
     
    print performance
    plt.savefig(outputFile)
    plt.close(fig)     
    
def plotTime(accidents):
    #analyse types
    vtypes= {}
    numberAccidents= 0.0
    for a in accidents:
        
        name= a[10].lower()
        if name.startswith("morgen") :
            name= "Morgens \n(5-10Uhr)\n"
        elif name.startswith("mittag"):
            name= "(Vor-)Mittags (10-14Uhr)\n"
        elif name.startswith("nachmittag") :
            name= "Nachmittags \n(14-18Uhr)\n"
        elif name.startswith("abend") :
            name= "Abends (18-23Uhr)\n"
        elif name.startswith("nacht") :
            name= "Nachts \n(23-5Uhr)\n"            
        else: 
            print name
            continue
        numberAccidents +=1
        if name in vtypes.keys():
            vtypes[name] += 1
        else:
            vtypes[name]= 1

    fig, ax = plt.subplots(figsize=(10,6))
  
    outputFile= 'zeit.png' 
    plt.title(u'Tageszeit (n= %s)' % numberAccidents)
    #plt.ylabel('Vehicle Type')
    #plt.xlabel('Percentage [%]')
    labels= []

    performance= []
        
    #sort values in dict
    for key, value in sorted(vtypes.iteritems(), key=lambda (k,v): (v,k)):
        p=value /numberAccidents *100
        labels.append(key) #+ ' '+str(int(p)) + '%')
        performance.append(p)
    
    cmap = plt.get_cmap('tab20c')
    outer_colors = cmap(np.array([1, 5,  9, 13,17]))
    pies = ax.pie(performance, labels= labels, colors=outer_colors, autopct='%1.1f%%', wedgeprops   = { 'linewidth' : 1,'edgecolor' : "black" })
     
    print performance
    plt.savefig(outputFile)
    plt.close(fig)     

def plotCrashTypes(accidents):
    #analyse types
    vtypes= {}
    numberAccidents= 0.0
    for a in accidents:
        
        name= a[1].lower()
        if name.startswith("pkw") :
            name= "Pkw"
        elif name.startswith("tram") or name.startswith("strassenbahn") or name.startswith("bus") or name.startswith("linienbus"):
            name= u'ÖPNV'
        elif name.startswith("motorrad") :
            name= u"Motorrad\n"
        elif name.startswith("transporter") or name.startswith("lkw") or name.startswith("geldtransporter"):
            name= u"Lkw"
        elif name.startswith(u'fussgaenger')or name.startswith("kind") :
            name= u'Fußgänger'
        elif name.startswith('traktor') or name.startswith('baum') or name.startswith('fahrrad') or name.startswith('rettungswagen') or name.startswith('taxi'):
            name= u'Sonstiges'
        else: 
            print name
            continue
        numberAccidents +=1
        if name in vtypes.keys():
            vtypes[name] += 1.0
        else:
            vtypes[name]= 1.0

    fig, ax = plt.subplots(figsize=(10,6))
  
    outputFile= 'teilnehmer.png' 
    plt.title(u'Verkehrsteilnehmer (n= %s)' % int(numberAccidents))
    #plt.ylabel('Vehicle Type')
    #plt.xlabel('Percentage [%]')
    labels= []

    performance= []
        
    #sort values in dict
    for key, value in sorted(vtypes.iteritems(), key=lambda (k,v): (v,k)):
        p=value /numberAccidents *100.0
        labels.append(key + ' '+str(round(p, 1)) + '%')
        performance.append(p)
    
    cmap = plt.get_cmap('tab20')
    outer_colors = cmap(np.array([1, 3,  5, 7,9, 11, 13]))
    pies = ax.pie(performance, labels= labels, colors=outer_colors, wedgeprops   = { 'linewidth' : 1,'edgecolor' : "black" })
     
    print performance
    plt.savefig(outputFile)
    plt.close(fig)     


input= file('accidents.csv', 'r')
accidents= []
while True:
    data=str(input.readline())
    if not data:
        break
    data=data.split(';')
    accidents.append(data)

def videoEval():
    fig, ax = plt.subplots(figsize=(10,6))
  
    outputFile= 'reaktion.png' 
    plt.title(u'Reaktionsdistanz zum Einsatzfahrzeug (n=%s)' %(11+15+6))
    #plt.ylabel('Vehicle Type')
    #plt.xlabel('Percentage [%]')
    labels= ["Keine Reaktion", "<25 m", "25-50m"]

    performance= [11,15,6]
    i=-1
    #sort values in dict
    for v in performance:
        i+=1
        p=(v/(11.+15.+6.)) *100.0
        labels[i]= labels[i] #+ ' '+ str(round(p, 1)) + '%'
        #performance.append(p)
        print p  , v , (v/(11+15+6)) 
    cmap = plt.get_cmap('tab20')
    outer_colors = cmap(np.array([1, 3,  5]))
    pies = ax.pie(performance, labels= labels, colors=outer_colors, autopct='%1.1f%%', wedgeprops   = { 'linewidth' : 1,'edgecolor' : "black" })
     
    print performance
    plt.savefig(outputFile)
    plt.close(fig)        


plotReasons(accidents)
plotInsured(accidents)
plotDead(accidents)

matplotlib.rcParams.update({'font.size': 18})
plotRoadTypes(accidents)
plotTime(accidents)
plotCrashTypes(accidents)
plotVehicleTypes(accidents)

videoEval()