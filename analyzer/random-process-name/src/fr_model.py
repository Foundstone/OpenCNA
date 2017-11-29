#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

__author__ = "Jorge Couchet"

import traceback
import cPickle as pickle
from urlparse import urlparse

import pandas as pd
import ng_model as mdl
import parse as prs

import utils

_SCALING_FACTOR_UNSEEN = 5
_PREDICTOR_VARIABLES = ['ENT', 'MK2_1', 'MK2_2', 'MK3_1', 'MK3_2']


def calculate_features(line, entr_model, ng_models, is_filter, is_epsilon,
                       epsilon, scaling_unseen, is_label=False, label=None):
    features = []
    features.append(mdl.calculate_str_entropy(line, entr_model))
    for ngm in ng_models:
        if is_epsilon:
            line_aux = epsilon + line + epsilon
        prob1, prob2 = mdl.compute_query_string_prob_helper(
            line_aux, ngm[1], ngm[2], ngm[0], scaling_unseen)
        features.append(prob1)
        features.append(prob2)
    if is_label and (label is not None):
        features.append(label)
    return features


def predict_query_string(query_str, model, entr_model, ng_models, is_filter,
                         is_folder=True, is_proc=False, is_fqdn=False,
                         is_fqdn_ready=True, is_epsilon=True,
                         epsilon=utils.EPSILON_CHARACTER,
                         folder_separator=utils.FOLDER_SEPARATOR,
                         scaling_unseen=_SCALING_FACTOR_UNSEEN):
    explanations = []
    observations = []
    is_random = False
    query_str_split = []
    all_features = []
    df_ft = {}
    dfl = []
    if is_folder:
        query_str_split = query_str.split(folder_separator)
        # The drive names (as 'c:') are not processed
        first_sf = query_str_split[0]
        if first_sf.endswith(':'):
            query_str_split = query_str_split[1:]
    else:
        if is_proc:
            query_str_split = [query_str]
        else:
            if is_fqdn:
                if not is_fqdn_ready:
                    query_str = urlparse(query_str).netloc
                is_punycode, is_non_ascii = prs.test_domain(query_str)
                if is_punycode or is_non_ascii:
                    if is_punycode:
                        observations.append('punycode')
                    if is_non_ascii:
                        observations.append('non ascii')
                else:
                    query_str_split = query_str.split('.')
    if query_str_split:
        for fd in query_str_split:
            # if is_epsilon:
            #    fd_aux = epsilon + fd + epsilon
            features = calculate_features(
                fd, entr_model, ng_models, is_filter, is_epsilon, epsilon, scaling_unseen)
            all_features.append(features)
        for fts in all_features:
            for ft, col in zip(fts, _PREDICTOR_VARIABLES):
                if col not in df_ft:
                    df_ft[col] = []
                df_ft[col].append(ft)
        for col in _PREDICTOR_VARIABLES:
            dfl.append((col, df_ft[col]))
        df = pd.DataFrame.from_items(dfl)
        predictions = model.predict(df)
        for idx, pred in enumerate(predictions):
            if pred == 1:
                is_random = True
                explanations.append(query_str_split[idx])
    return is_random, explanations, observations


def load_all(ng_2_model_name, ng_3_model_name, fr_model_name):
    ng_model_2 = mdl.load_model(ng_2_model_name)
    ng_model_3 = mdl.load_model(ng_3_model_name)
    ng_models = []
    ng_models.append(
        (2, ng_model_2['transition_probs'], ng_model_2['min_prob']))
    ng_models.append(
        (3, ng_model_3['transition_probs'], ng_model_3['min_prob']))
    entr_model = ng_model_3['entr_model']
    fr_model = load_model(fr_model_name)
    return entr_model, ng_models, fr_model


def load_model(file_name):
    model = None
    try:
        with open(file_name, 'rb') as handler:
            model = pickle.load(handler)
    except:
        print 'There was a problem loading the model from the file: ' + str(file_name)
        traceback.print_exc()
    finally:
        return model
