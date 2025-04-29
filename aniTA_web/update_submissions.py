#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

from users.arangodb import db

def update_submissions():
    # Get submission collection
    submission_collection = db.collection('submission')
    
    # Get all submissions
    all_submissions = list(submission_collection.find({}))
    print(f"Found {len(all_submissions)} submissions")
    
    # Update each submission
    updated_count = 0
    for submission in all_submissions:
        submission['is_autograded'] = True
        submission_collection.update(submission)
        updated_count += 1
    
    print(f"Updated {updated_count} submissions to be autograded")

if __name__ == "__main__":
    update_submissions()