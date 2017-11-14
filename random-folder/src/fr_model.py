#!/usr/bin/python
# -*- coding: utf-8 -*

import csv
import traceback
import os
import random as rnd
import pickle
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedShuffleSplit
from scipy.stats import randint as sp_randint
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score, recall_score
from sklearn.metrics import f1_score
from sklearn.model_selection import cross_val_predict
import tools
import ng_model as mdl

SCALING_FACTOR_UNSEEN = 5
TEST_SIZE = 0.2
RANDOM_SEED = 77
NUMBER_ITER = 50
TARGET_VARIABLE = 'Y'
PREDICTOR_VARIABLES = ['ENT', 'MK2_1', 'MK2_2', 'MK3_1', 'MK3_2'] 

def clf_report(clf, xset, yset, clfr):
    y_predictions = clf.predict(xset)
    report = clfr(yset, y_predictions)
    print
    print 'The classification report is:'
    print report
    return y_predictions

def print_best_model_report(clf, parameters):
    print
    print 'The best model report is:'
    print '\tBest score: {}'.format(clf.best_score_)
    print '\tBest parameters set:'
    best_parameters = clf.best_estimator_.get_params()
    for param_name in sorted(parameters.keys()):
        print '\t\t{}: {}'.format(param_name, best_parameters[param_name])
    return clf.best_score_

def calculate_features(line, entr_model, ng_models, is_filter, is_epsilon, epsilon, scaling_unseen, is_label=False, label=None):
    features = []
    features.append(mdl.calculate_str_entropy(line, entr_model))
    for ngm in ng_models:
        if is_epsilon:
            line_aux = epsilon + line + epsilon
        prob1, prob2 = mdl._compute_query_string_prob(line_aux, ngm[1], ngm[2], ngm[0], scaling_unseen)
        features.append(prob1)
        features.append(prob2)
    if is_label and (label is not None):
        features.append(label)
    return features

def generate_training_data(file_name_ok, file_name_neg, out_file_name, entr_model, ng_models, is_filter, cols, is_epsilon=True, epsilon=tools.EPSILON_CHARACTER, scaling_unseen=mdl.SCALING_FACTOR_UNSEEN):
    all_features = []
    try:
        with open(file_name_ok, 'r+') as f, open(file_name_neg, 'r+') as f2, open(out_file_name + '.csv', 'w+') as f3:
            csvwr = csv.writer(f3)
            csvwr.writerow(cols)
            label = 0
            for line in f:
                if is_filter:
                    line_split = line.split('.')
                    line = '.'.join(line_split[0:-1])
                features = calculate_features(line, entr_model, ng_models, is_filter, is_epsilon, epsilon, scaling_unseen, True, label)
                if len(features) > 0:
                    all_features.append(features)
            label = 1
            for line in f2:
                features = calculate_features(line, entr_model, ng_models, is_filter, is_epsilon, epsilon, scaling_unseen, True, label)
                if len(features) > 0:
                    all_features.append(features)
            rnd.shuffle(all_features)
            for fe in all_features:
                csvwr.writerow(fe)
    except:
        print 'There was a problem processing the files: {}, {}, {}'.format(file_name_ok, file_name_neg, out_file_name)
        traceback.print_exc()

def train(file_name, test_size=TEST_SIZE, seed=RANDOM_SEED, n_iter_rs=NUMBER_ITER, cv_size=15):
    df = pd.read_csv(file_name)
    print df.head()
    print
    split = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    for train_index, test_index in split.split(df, df[TARGET_VARIABLE]):
        df_train_set = df.loc[train_index]
        df_test_set = df.loc[test_index]
    print df_train_set.head()
    print df_train_set.shape
    print
    print df_test_set.head()
    print df_test_set.shape
    print
    x_training = df_train_set[PREDICTOR_VARIABLES]
    y_training = df_train_set[TARGET_VARIABLE]
    x_test = df_test_set[PREDICTOR_VARIABLES]
    y_test = df_test_set[TARGET_VARIABLE]
    parameters = {
        'n_estimators': sp_randint(1, 25),
        'max_depth': sp_randint(1, 25),
        'max_features': sp_randint(1, len(PREDICTOR_VARIABLES)),
        'max_leaf_nodes': sp_randint(5, 30),
        'min_samples_split': sp_randint(2, 11),
        'min_samples_leaf': sp_randint(1, 11),
        'class_weight': ['balanced']
    }
    clf_rf = RandomForestClassifier()
    random_search_rf = RandomizedSearchCV(clf_rf, param_distributions=parameters, n_iter=n_iter_rs, cv=cv_size, n_jobs=-1,verbose=1, scoring='f1')
    random_search_rf.fit(x_training, y_training)
    rf_score = print_best_model_report(random_search_rf, parameters)
    yp_rf = clf_report(random_search_rf, x_training, y_training, classification_report)
    clf_winner = random_search_rf.best_estimator_
    y_probas = cross_val_predict(clf_winner, x_training, y_training, cv=cv_size, method='predict_proba')
    y_scores = y_probas[:, 1]
    yp_test = clf_report(clf_winner, x_test, y_test, classification_report)
    print
    print 'Confusion matrix:'
    print confusion_matrix(y_test, yp_test)
    print 'Precison:'
    print precision_score(y_test, yp_test)
    print 'Recall'
    print recall_score(y_test, yp_test)
    print 'F1 score:'
    print f1_score(y_test, yp_test)
    y_scores_test = clf_winner.predict_proba(x_test)[:, 1]
    return clf_winner

def predict_query_string(query_str, model, entr_model, ng_models, is_filter, is_epsilon=True, epsilon=tools.EPSILON_CHARACTER, folder_separator=tools.FOLDER_SEPARATOR, scaling_unseen=SCALING_FACTOR_UNSEEN):
    all_features = []
    df_ft = {}
    dfl = []
    query_str_sub_folders = query_str.split(folder_separator)
    explanations = []
    is_random = False
    # The drive names (as 'c:') are not processed
    first_sf = query_str_sub_folders[0]
    if (len(first_sf) == 2) and (first_sf[1] == ':'):
        query_str_sub_folders = query_str_sub_folders[1:]
    if len(query_str_sub_folders) > 0:
        for fd in query_str_sub_folders:
            if is_epsilon:
                fd_aux = epsilon + fd + epsilon
            features = calculate_features(fd_aux, entr_model, ng_models, is_filter, is_epsilon, epsilon, scaling_unseen)
            all_features.append(features)
        for fts in all_features:
            for ft, col in zip(fts, PREDICTOR_VARIABLES):
                if col not in df_ft:
                    df_ft[col] = []
                df_ft[col].append(ft)
        for col in PREDICTOR_VARIABLES:
            dfl.append((col, df_ft[col]))
        df = pd.DataFrame.from_items(dfl)
        predictions = model.predict(df)
        for idx, pred in enumerate(predictions):
            if pred == 1:
                is_random = True
                explanations.append(query_str_sub_folders[idx])
    return is_random, explanations

def load_all(ng_2_model_name, ng_3_model_name, fr_model_name):
    ng_model_2 = mdl.load_model(ng_2_model_name)
    ng_model_3 = mdl.load_model(ng_3_model_name)
    ng_models = []
    ng_models.append((2, ng_model_2['transition_probs'], ng_model_2['min_prob']))
    ng_models.append((3, ng_model_3['transition_probs'], ng_model_3['min_prob']))
    entr_model = ng_model_3['entr_model']
    fr_model = load_model(fr_model_name)
    return entr_model, ng_models, fr_model

def save_model(model, file_name):
    try:
        with open(file_name, 'wb') as f:
            pickle.dump(model, f)
    except:
        print 'There was a problem saving the model to the file: {}'.format(file_name)
        traceback.print_exc()

def load_model(file_name):
    model = None
    try:
        with open(file_name, 'rb') as f:
            model = pickle.load(f)
    except:
        print 'There was a problem loading the model from the file: {}'.format(file_name)
        traceback.print_exc()
    finally:
        return model