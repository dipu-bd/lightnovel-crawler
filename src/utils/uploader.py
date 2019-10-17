#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Uploader for google drive"""
import os
import logging

logger = logging.getLogger('UPLOADER')


try:
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
except Exception:
    logger.error('`pydrive` was not setup properly')
# end try


def upload(file_path):
    try:
        gauth = GoogleAuth()
        # gauth.LocalWebserverAuth()

        # Try to load saved client credentials
        gauth.LoadCredentialsFile("mycreds.txt")
        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved creds
            gauth.Authorize()
        # end if

        # Save the current credentials to a file
        gauth.SaveCredentialsFile("mycreds.txt")

        drive = GoogleDrive(gauth)
        folder_id = '118iN1jzavVV-9flrLPZo7DOi0cuxrQ5F'
        filename_w_ext = os.path.basename(file_path)
        filename, file_extension = os.path.splitext(filename_w_ext)

        # Upload file to folder
        f = drive.CreateFile(
            {"parents": [{"kind": "drive#fileLink", "id": folder_id}]})
        f['title'] = filename_w_ext

        # Make sure to add the path to the file to upload below.
        f.SetContentFile(file_path)
        f.Upload()

        logger.info(f['id'])
        return f['id']
    except Exception:
        logger.exception('Failed to upload %s', file_path)
    # end try
    return None
# end def
