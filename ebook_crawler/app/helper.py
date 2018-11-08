#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper methods used in crawling"""
import json
import os
import re
import urllib
import cfscrape


def retrieve_image(image_url, output_file):
    try:
        scraper = cfscrape.create_scraper()
        cfurl = scraper.get(output_file).content
        with open(output_file, 'wb') as f:
            f.write(cfurl)
        # end with
    except:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(image_url, output_file)
    # end try
# end def
