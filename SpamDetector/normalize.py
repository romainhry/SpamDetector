#import csv
#import sys
#import os
#from math import sqrt

import csv
import math
import os

class Normalizer(object):

    def __init__(self):
        pass
    '''
    def __init__(self,dataset):
        self.load_csv(dataset)
        self.data_to_tab()
    '''
    def load_csv(self,s):
        file=s
        datafile= open(file,'r')
        self.data=csv.reader(datafile)
        self.data_to_tab()
        return self.myTab

    def data_to_tab(self):
        tab=[]
        for l in self.data:
            ligne=[]
            for c in l:
                try:
                    v=float(c)
                    ligne.append(v)
                except ValueError or TypeError:
                    ligne.append(c)
            if len(ligne)!=0:
                tab.append(ligne)
        self.myTab=tab

    def get_col(self,tab,x):
        t=[]
        for l in tab:
            t.append(l[x])
        return t

    def max(self,data):
        max=data[0]
        for l in data:
            if max<l:
                max=l
        return max

    def min(self,data):
        min=data[0]
        for l in data:
            if min>l:
                min=l
        return min

    def normalize_col(self,col, min, max,Min,Max):
        t=[]
        for l in col:
            t.append((math.fabs(max)+math.fabs(min))*(l-Min)/(Max-Min)-math.fabs(min))
        return t

    def normalization(self):
        i=0
        res=[]
        while i < 58:
            colonne=self.get_col(self.myTab, i)
            max=self.max(colonne)
            min=self.min(colonne)
            res.append(self.normalize_col(colonne, 0, 1.0, min, max))
            i+=1
        return res;

    def moyenne(self,tableau):
        return sum(tableau, 0.0) / len(tableau)

    def variance(self,tableau):
        m=self.moyenne(tableau)
        return self.moyenne([(x-m)**2 for x in tableau])

    def ecartype(self,tableau):
        return self.variance(tableau)**0.5

    def stats(self,spam,nospam):
    #def stats(self,spam):
        stat = []
        s =[]
        ns=[]
        tab_avg = []
        tab_min = []
        tab_max = []
        tab_et=[]
        for l in spam:
            tab_avg.append(self.truncate(self.moyenne(l),5))
            tab_et.append(self.truncate(self.ecartype(l),5))
            tab_max.append(self.truncate(self.max(l),5))
            tab_min.append(self.truncate(self.min(l),5))
            '''
            tab_avg.append(self.moyenne(l))
            tab_et.append(self.ecartype(l))
            tab_max.append(self.max(l))
            tab_min.append(self.min(l))
            '''
        s.append(tab_min)
        s.append(tab_max)
        s.append(tab_avg)
        s.append(tab_et)
        stat.append(s)
        tab_avg = []
        tab_min = []
        tab_max = []
        tab_et=[]
        for l in nospam:
            tab_avg.append(self.truncate(self.moyenne(l),5))
            tab_et.append(self.truncate(self.ecartype(l),5))
            tab_max.append(self.truncate(self.max(l),5))
            tab_min.append(self.truncate(self.min(l),5))
        ns.append(tab_min)
        ns.append(tab_max)
        ns.append(tab_avg)
        ns.append(tab_et)
        stat.append(ns)
        return stat

    def split(self,data):
        res = []
        data_spam =[]
        data_nospam =[]
        for j in range(len(data)):
            ligneSpam=[]
            ligneNonSpam=[]
            for i in range(len(data[57])):
                if(data[57][i] == 1.0):
                    ligneSpam.append(data[j][i])
                else:
                    ligneNonSpam.append(data[j][i])
            data_spam.append(ligneSpam)
            data_nospam.append(ligneNonSpam)
        res.append(data_spam)
        res.append(data_nospam)
        return res

    def truncate(self, f, n):
        '''Truncates/pads a float f to n decimal places without rounding'''
        s = '%.5f' % f
        i, p, d = s.partition('.')
        return '.'.join([i, (d+'0'*n)[:n]])

    def get_splitedData(self,champs):
        spams =[]
        nospams = []
        for j in range(len(self.myTab)):
            ligne=[]
            for k in champs:
                ligne.append(self.myTab[j][k])
            if(self.myTab[j][57]==1.0):
                spams.append(ligne)
            else:
                nospams.append(ligne)
        res =[]
        res.append(spams)
        res.append(nospams)
        return res

if __name__ == '__main__':
    norm = Normalizer()
    workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
    datafile = os.path.join(workpath, 'dataset/spambase.data.txt')
    data = norm.load_csv(datafile)
    champs = [0,1,2]
    normalizedData = norm.normalization()
    normSplitedData = norm.split(normalizedData)
    normNospams = normSplitedData[1]
    normSpams = normSplitedData[0]
    splitedData = norm.get_splitedData(champs)
    spams = splitedData[0]
    nospams = splitedData[1]
    print "@@@@@@@@@@@@@@@@@@@@@ SPAMS @@@@@@@@@@@@@@@@@@@@@"
    for s in spams:
        print s
    print "@@@@@@@@@@@@@@@@@@@@@ NO SPAMS @@@@@@@@@@@@@@@@@@@@@"
    for s in nospams:
        print s

    stat = norm.stats(normSpams,normNospams)
    print("STATS SPAM")
    for s in stat[0]:
        print s
    print("STATS NO SPAM")
    for s in stat[1]:
        print s

    print stat[0][0][57]==norm.truncate(1,5)
