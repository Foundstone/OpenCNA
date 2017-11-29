#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

__author__ = "Jorge Couchet"

import re

PUNYCODE = 'xn--'

def test_domain(domain):
    is_punycode = False
    is_non_ascii = False
    if domain.find(PUNYCODE) != -1:
        is_punycode = True
    if (re.sub('[ -~]', '', domain)) != '':
        is_non_ascii = True
    return is_punycode, is_non_ascii
