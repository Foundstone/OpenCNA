#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

__author__ = "Jorge Couchet"

import math
import pickle
import traceback
import itertools
import utils

SCALING_FACTOR_UNSEEN = 5
ALMOST_NULL_PROB = 0.00000001
ENTROPY_THRESHOLD = 3


def calculate_ngram(n, line, is_normalize=True):
    res = []
    if is_normalize:
        line = utils.normalize_line(line)
    for start in range(0, len(line) - n + 1):
        res.append(line[start:start + n])
    return res


def update_n_gram_transition_counter(ngcomps, n_gram_transition_counts):
    if len(ngcomps) == 1:
        ng1 = ngcomps[0]
        if ng1 not in n_gram_transition_counts:
            n_gram_transition_counts[ng1] = 0
        n_gram_transition_counts[ng1] += 1
    else:
        ng1 = ngcomps[0]
        if ng1 not in n_gram_transition_counts:
            n_gram_transition_counts[ng1] = {}
        update_n_gram_transition_counter(
            ngcomps[1:], n_gram_transition_counts[ng1])


def sum_total(n_gram_transition_counts):
    if not isinstance(n_gram_transition_counts, dict):
        return n_gram_transition_counts
    else:
        sumt = 0
        for ngtc in n_gram_transition_counts.keys():
            sumt += sum_total(n_gram_transition_counts[ngtc])
        return sumt


def update_log_prob(n_gram_transition_counts, total, min_prob):
    for ngc in n_gram_transition_counts.keys():
        if not isinstance(n_gram_transition_counts[ngc], dict):
            # Normalize the counts to become probabilities:
            #    - It is used log probabilities to avoid numeric issues
            log_prob = math.log(n_gram_transition_counts[ngc] / total)
            n_gram_transition_counts[ngc] = log_prob
            if log_prob < min_prob:
                min_prob = log_prob
        else:
            min_prob = update_log_prob(
                n_gram_transition_counts[ngc], total, min_prob)
    return min_prob


def normalize_log_prob(n_gram_transition_counts, min_prob):
    total = float(sum_total(n_gram_transition_counts))
    if total != 0.0:
        min_prob = update_log_prob(n_gram_transition_counts, total, min_prob)
    return min_prob


def normalize_freqs(freqs):
    total = float(sum(freqs.values()))
    if total != 0.0:
        for char in freqs.keys():
            freq = freqs[char] / total
            if freq != 0.0:
                freqs[char] = freq
            else:
                freqs[char] = ALMOST_NULL_PROB


def model_entropy(file_name, epsilon=utils.EPSILON_CHARACTER):
    chars_freq = {}
    try:
        with open(file_name, 'r+') as handler:
            for line in handler:
                line = utils.normalize_line(line)
                line_without_epsilon = line.replace(epsilon, '')
                for idx in range(0, len(line_without_epsilon)):
                    char = line_without_epsilon[idx]
                    if char not in chars_freq:
                        chars_freq[char] = 0
                    chars_freq[char] += 1
            normalize_freqs(chars_freq)
    except:
        print 'There was a problem processing the file: {}'.format(file_name)
        traceback.print_exc()
        chars_freq = {}
    finally:
        return chars_freq


def calculate_str_entropy(query_str, model, is_normalize=True):
    entr = 0
    if is_normalize:
        query_str = utils.normalize_line(query_str)
    for idx in range(0, len(query_str)):
        char = query_str[idx]
        if char in model:
            prob = model[char]
        else:
            prob = ALMOST_NULL_PROB
        entr -= prob * math.log(prob)
    return entr


def model_n_gram(file_name, entr_model, is_filter, n=2, is_epsilon=True,
                 epsilon=utils.EPSILON_CHARACTER, is_entr=True,
                 entropy_threshold=ENTROPY_THRESHOLD):
    res_min_prob = 0
    n_gram_transition_counts = {}
    try:
        if n > 0:
            with open(file_name, 'r+') as handler:
                for line in handler:
                    line = utils.normalize_line(line)
                    if is_filter:
                        line_split = line.split('.')
                        line = '.'.join(line_split[0:-1])
                    is_process = True
                    if is_entr:
                        if calculate_str_entropy(line, entr_model) > entropy_threshold:
                            is_process = False
                    if is_process:
                        if is_epsilon:
                            line = epsilon + line + epsilon
                        ngs = calculate_ngram(n, line)
                        for ng in ngs:
                            update_n_gram_transition_counter(
                                list(ng), n_gram_transition_counts)
                res_min_prob = 0
                if n == 1:
                    res_min_prob = normalize_log_prob(
                        n_gram_transition_counts, res_min_prob)
                else:
                    for n_gram in n_gram_transition_counts:
                        res_min_prob = normalize_log_prob(
                            n_gram_transition_counts[n_gram], res_min_prob)
    except:
        print 'There was a problem processing the file: {}'.format(file_name)
        traceback.print_exc()
        n_gram_transition_counts = {}
        res_min_prob = 0
    finally:
        return n_gram_transition_counts, res_min_prob


def save_model(transition_probs, min_prob, entr_model, file_name):
    try:
        with open(file_name, 'wb') as handler:
            pickle.dump({'transition_probs': transition_probs,
                         'entr_model': entr_model, 'min_prob': min_prob}, handler)
    except:
        print 'There was a problem saving the model to the file: {}'.format(file_name)
        traceback.print_exc()


def load_model(file_name):
    model = None
    try:
        with open(file_name, 'rb') as handler:
            model = pickle.load(handler)
    except:
        print 'There was a problem loading the model from the file: {}'.format(file_name)
        traceback.print_exc()
    finally:
        return model


def _get_prob(ngcomps, model, min_prob, scaling_unseen):
    if len(ngcomps) == 1:
        if ngcomps[0] in model:
            return model[ngcomps[0]]
        else:
            return min_prob * scaling_unseen
    else:
        if ngcomps[0] in model:
            return _get_prob(ngcomps[1:], model[ngcomps[0]], min_prob, scaling_unseen)
        else:
            return min_prob * scaling_unseen


def compute_query_string_prob_helper(query_str, model, min_prob, n=2,
                                     scaling_unseen=SCALING_FACTOR_UNSEEN):
    log_prob = 0.0
    ngs = calculate_ngram(n, query_str)
    mkvc_transitions = len(ngs)
    for ng in ngs:
        log_prob += _get_prob(list(ng), model, min_prob, scaling_unseen)
    log_prob = log_prob / (mkvc_transitions or 1)
    return math.exp(log_prob), log_prob


def compute_query_string_prob(query_str, saved_model, n=2, is_epsilon=True,
                              epsilon=utils.EPSILON_CHARACTER,
                              folder_separator=utils.FOLDER_SEPARATOR,
                              scaling_unseen=SCALING_FACTOR_UNSEEN):
    sub_folder_probs = []
    query_str_sub_folders = query_str.split(folder_separator)
    # The drive names (as 'c:') are not processed
    first_sf = query_str_sub_folders[0]
    if first_sf.endswith(':'):
        query_str_sub_folders = query_str_sub_folders[1:]
    for fd in query_str_sub_folders:
        if is_epsilon:
            fd_aux = epsilon + fd + epsilon
        prob, _ = compute_query_string_prob_helper(
            fd_aux, saved_model['transition_probs'], saved_model['min_prob'], n, scaling_unseen)
        sub_folder_probs.append((fd, prob))
    return sub_folder_probs


def calculate_danger(query_string, saved_model, threshold, n=2, is_epsilon=True,
                     epsilon=utils.EPSILON_CHARACTER,
                     folder_separator=utils.FOLDER_SEPARATOR,
                     scaling_unseen=SCALING_FACTOR_UNSEEN):
    is_positive = False
    explanation = ''
    prob_decision = 1
    sub_folder_probs = compute_query_string_prob(
        query_string, saved_model, n, is_epsilon, epsilon, folder_separator, scaling_unseen)
    for fd in sub_folder_probs:
        if fd[1] < threshold:
            prob_decision = fd[1]
            explanation = fd[0]
            is_positive = True
            break
        else:
            if fd[1] < prob_decision:
                prob_decision = fd[1]
                explanation = fd[0]
    return is_positive, explanation, prob_decision


def calculate_mixed_danger(query_strings, models, mixed_coeffs, threshold, n=2,
                           is_epsilon=True, epsilon=utils.EPSILON_CHARACTER,
                           folder_separator=utils.FOLDER_SEPARATOR,
                           scaling_unseen=SCALING_FACTOR_UNSEEN):
    explanations = set()
    res_prob = 0
    for idx, model in enumerate(models):
        _, explanation, prob_decision = calculate_danger(query_strings, model,
                                                threshold, n, is_epsilon, epsilon,
                                                folder_separator, scaling_unseen)
        res_prob += mixed_coeffs[idx] * prob_decision
        explanations.add(explanation)
    return res_prob, list(explanations)


def calculate_distribution_over_corpus(folder_files_names, model, threshold, n=2,
                                       is_epsilon=True, epsilon=utils.EPSILON_CHARACTER,
                                       folder_separator=utils.FOLDER_SEPARATOR,
                                       scaling_unseen=SCALING_FACTOR_UNSEEN):
    distribution = {}
    total = 0
    total_under_threshold = 0
    total_under_threshold_with_exec = 0
    try:
        with open(folder_files_names, 'rb') as handler:
            ff_names = pickle.load(handler)
        total = len(ff_names)
        for fname in ff_names.keys():
            is_positive, explanation, prob_decision = calculate_danger(
                fname, model, threshold, n, is_epsilon, epsilon, folder_separator, scaling_unseen)
            percentage_executables = 0
            if ff_names[fname]['total_files'] != 0:
                percentage_executables = ff_names[fname]['total_execs'] / float(
                    ff_names[fname]['total_files'])
            if is_positive:
                total_under_threshold += 1
                if percentage_executables > 0:
                    total_under_threshold_with_exec += 1
            distribution[fname] = {
                'suspicious': is_positive,
                'len': ff_names[fname]['len'],
                'percent_execs': percentage_executables,
                'explanation': explanation,
                'prob_decision': prob_decision
            }
    except:
        print 'There was a problem loading the model from the file: ' + str(folder_files_names)
        traceback.print_exc()
        distribution = {}
        total = 0
        total_under_threshold = 0
        total_under_threshold_with_exec = 0
    finally:
        return distribution, total, total_under_threshold, total_under_threshold_with_exec
