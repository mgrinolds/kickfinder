# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 10:26:05 2014

@author: Mike
"""

from __future__ import division
import kickfinder_settings as kfs
from pandas import DataFrame

import numpy as np
import pylab as pl
from sklearn import linear_model, datasets
from sklearn.cross_validation import train_test_split
from sklearn import cross_validation
from sklearn.metrics import accuracy_score, f1_score, average_precision_score
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import auc

class Predictor:
    
    def __init__(self):
        self.sql = kfs.project_graph_tbl

        self.outcome_field = "percent_raised"

        self.used_fields = ['goal',
                    'first_backed',
                    'first_created',
                    'npictures',
                    'has_video',
                    'nrewards',
                    'body_length',
                    'nexternal_links',
                    'project_duration']
                    
#                    'currency',
#                    'nquestions',
#                    'has_website',
#                    'website_length',
#                    'nlimited_rewards',
#                    'r0_10','r10_25','r25_40',
#                    'r40_60','r60_100','r100_200',
#                    'r200_500','r500']


        self.feature_fields = """nbackers, 
                    url,                    
                    name,                    
                    first_backed, 
                    first_created, 
                    hours_remaining,
                    goal,
                    connected_facebook,
                    pledged,
                    has_video,
                    project_duration,
                    latitude,
                    longitude,
                    body_length,
                    ncomments,
                    nrewards,
                    npictures,
                    nupdates,
                    nexternal_links,

                    """
#                    nlimited_rewards,
#                    r0_10,
#                    r10_25,
#                    r25_40,
#                    r40_60,
#                    r60_100,
#                    r100_200,
#                    r200_500,
#                    r500,
#                    currency,
#                    nquestions,
#                    has_website,
#                    website_length,              
        

    def predict(self,bupdate_db=0):
        results = self.sql.query_dict('SELECT %s FROM projects WHERE ncomments IS NOT NULL' % (self.feature_fields + self.outcome_field))

        df = DataFrame.from_records(results)
        
        df = df.fillna(0)

        df.goal = pow(df.goal,1/4)
        df.body_length = pow(df.body_length,1/2)
        df.nrewards = pow(df.nrewards,1/2)
        df.nlinks = pow(df.nexternal_links,1/2)

        df = df.fillna(0)

        X = df.as_matrix(self.used_fields)
                                   
        for row_ind in range(X.shape[1]):
            X[:,row_ind] = X[:,row_ind] - X[:,row_ind].mean()
            X[:,row_ind] = X[:,row_ind] / X[:,row_ind].std()

        y = df.percent_raised
        y[y > 1] = 1
        y[y < 1] = 0
       
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.3, random_state=1)
    
        logreg = linear_model.LogisticRegression(C=1e5, penalty='l2')
        print 'regressing...'
        logreg.fit(X_train, y_train)
        
        probs = logreg.predict_proba(X_test)[:,1]

        ap = average_precision_score(y_test,probs)
        print ap
        
        precision, recall, thresholds = precision_recall_curve(y_test,probs)
        area = auc(recall, precision)
        print("Area Under Curve: %0.2f" % area)

        names = df['url']
        
        pred = np.empty(names.shape)
        pred_prob = np.empty(names.shape)
        actual = np.empty(names.shape)
        for ind, name in enumerate(names):
            pred[ind] = logreg.predict(X[ind,:])
            pred_prob[ind] = logreg.predict_proba(X[ind,:])[:,1]
            actual[ind] = y[ind]
            names[ind] = name
            
            if bupdate_db:
                print (ind,actual[ind],pred_prob[ind])
                self.sql.update_value('prediction',pred_prob[ind],'url',name)
                 
        return (pred,pred_prob,actual)

        
if __name__ == '__main__': 
    pred = Predictor()
    p,pb,act = pred.predict(0)
#    df,X, y= pred.predict(0)    
    
    thresh = 0.25
    high_end_accuracy = sum((pb > 1 - thresh) & (act == 1))/sum((pb > 1- thresh))
    low_end_accuracy = sum((pb < thresh) & (act == 0))/sum((pb < thresh))
    print(thresh,high_end_accuracy,low_end_accuracy)
    
    out = pred.sql.query('SELECT prediction, percent_raised FROM projects')
    prob,results = zip(*out)
    
    results = np.array(results)
    prob = np.array(prob)
    
    results[results > 1] = 1
    results[results < 1] = 0
    prob[prob > 0.5] = 1
    prob[prob < 0.5] = 0
    
    ap = average_precision_score(results,prob)
    
    true = np.empty(prob.shape)
    ind = 0;
    for p,r in zip(prob,results):
        true[ind] = p == r
        ind += 1
