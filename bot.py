#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import pickle
import os
import time
import re
import wget


debug = False

# GLOBAL PROPERTIES
articles_filename = "articles.p"
articles = {}
max_article_length = 300
period_in_minutes = 10
picture_temp_path = 'temp.jpg'

# Toggle it off to not remove links


# Load Telegram params
# See params file on how to use it
import params_sniviktest as params
bot_url = params.bot_url
channel_id = params.channel_id
vk_public_domain = params.vk_public_domain
remove_links = params.remove_links
include_article_link = params.include_article_link
include_article_link_text = params.include_article_link_text

# Delimiters
delimiters = ['.', '?', '!', '...', ' ']


def get_vk_articles(count=10, domain='bfguns'):

    vk_request_params = {
                          'domain': domain,
                          'count': count,
    }

    vk_url = 'https://api.vk.com/method/wall.get'
    response = requests.post(vk_url, data=vk_request_params)

    return response


def load_existing_articles():

    print "Loading Existing Articles..."
    global articles_filename
    global articles

    if os.path.exists(articles_filename):
        articles = pickle.load(open(articles_filename, 'r'))


def get_article_link(wall, id):
    return 'http://vk.com/bfguns?w=wall-{wall}_{id}'.format(wall=abs(int(wall)), id=abs(int(id)))


def get_adapted_text(text):
    global max_article_length
    global delimiters
    global remove_links

    adapted = text
    # Get rid of all links encoded in proper html
    if remove_links:
        adapted = re.sub("<a>.*</a>", "", text)

    # Replace BRs with spaces, telegram can't handle them
    adapted = re.sub("<br/?>", " ", adapted)

    # Get rid of other brackets
    adapted = re.sub("</?[a-z]+/?>", "", adapted)



    # Cut the string if it exceeds char length
    if len(adapted) > max_article_length:
        adapted = adapted[0:max_article_length]

        # Beautify string
        delim_index = -1

        # Find first suitable delimiter
        for delim in delimiters:
            if delim_index > 0:
                break
            delim_index = adapted.rfind(delim)

        if delim_index < 0:
            print "Following text has no delimiters"
            print adapted
            return None

        adapted = adapted[0:delim_index+1]

    return adapted


def post_article_to_chat(text, file):
    global bot_url
    global channel_id
    global picture_temp_path

    post_url = bot_url+'sendMessage'
    post_picture_url = bot_url+'sendPhoto'
    request_body = {'chat_id': channel_id, 'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': True}

    resp = requests.post(post_url, json=request_body)
    if file is not None:
        if debug:
            print "Sending Picture..."
        im_upload_resp = requests.post(post_picture_url, files=file, data={'chat_id': channel_id}).json()

        if debug:
            print im_upload_resp
            try:
                print im_upload_resp.json()
            except Exception as e:
                print e

        os.remove(picture_temp_path)

    return resp


def post_article_to_telegram(article, processed_article_ids):

    global picture_temp_path
    global articles

    # Check if this article has ID at all
    if 'id' not in article:
        print 'Following article has no ID'
        print article
        return

    # Check if have already added this article
    if article['id'] in articles:
        if debug:
            print "Article is already processed"
            print article
        processed_article_ids.append(article['id'])
        return

    # Check if it's a post with text
    if ('post_type' not in article) or (not (not (article['post_type'] != 'post') or (
            article['post_type'] == 'copy' and article['copy_post_type'] == 'post'))):
        print 'Article is not a post'
        print article
        return

    # Try to compile a Telegram post

    # Step 1, adapt text
    article_text = ''
    if article['post_type'] == 'post':
        article_text = get_adapted_text(article['text'])
    elif article['post_type'] == 'copy':
        article_text = get_adapted_text(article['copy_text'])

    if article_text is None:
        print "Failed to parse article's text"
        print article
        return

    global include_article_link_text
    global include_article_link

    if include_article_link:
        article_text += u' <a href="{link}">{text}</a>'.format(
            link=get_article_link(article['from_id'], article['id']),
            text=include_article_link_text)

    # See if there are any attachments to download
    file = None
    if 'attachment' in article and article['attachment']['type'] == 'photo':
        wget.download(article['attachment']['photo']['src_big'], picture_temp_path)
        file = {'photo': ('bfg_attachment.jpg', open(picture_temp_path, 'rb'))}

    # Post article to Telegram
    response = post_article_to_chat(article_text, file)

    if debug:
        print response
    articles[article['id']] = article

    # Add it to he list of processed articles
    processed_article_ids.append(article['id'])



def main():

    global vk_public_domain

    # Load what we've already parsed
    load_existing_articles()

    print "Existing articles loaded...";

    while True:


        # Load Existing articles
        try:
            if debug:
                print "Downloading articles...";
            vk_articles = get_vk_articles(domain=vk_public_domain).json()['response']

            processed_article_ids = []

            # Go through all articles
            vk_articles.reverse()
            for article in vk_articles:
                if type(article) is dict:
                    post_article_to_telegram(article, processed_article_ids)

            # Do cleanup of articles
            for key in articles.keys():
                if key not in processed_article_ids:
                    del articles[key]

            pickle.dump(articles, open(articles_filename, 'w+'))
        except Exception as e:
            print "Exception raised while trying to download & post articles"
            print e

        # Wait until next refresh
        time.sleep(60 * period_in_minutes)


main()

