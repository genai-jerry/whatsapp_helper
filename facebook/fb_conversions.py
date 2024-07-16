import requests
import json
from store.fb_events_store import check_events_fired, update_event_fired

url = "https://connect.pabbly.com/workflow/sendwebhookdata/IjU3NjUwNTY1MDYzNzA0MzI1MjY1NTUzNDUxM2Ii_pc"
    
def add_lead(opportunity, status_value):
    # If the event is of type "VSL Shared", send a POST request to the external API
    events_fired = check_events_fired(opportunity['id'])
    if status_value in ['3', '4', '5', '8', '10', '15']:
        if 'lead_event_fired' not in events_fired or not events_fired['lead_event_fired']:
            fire_event(opportunity, "NewLead")
            update_event_fired(opportunity['id'], 'lead_event_fired')
            print('Lead event fired')
    if status_value in ['8']:
        if 'submit_application_event_fired' not in events_fired or not events_fired['submit_application_event_fired']:
            fire_event(opportunity, "SubmitApplication")
            update_event_fired(opportunity['id'], 'submit_application_event_fired')
            print('SubmitApplication event fired')

def video_watched(opportunity):
    events_fired = check_events_fired(opportunity['id'])
    print(f'Firing VideoWatched event {events_fired["video_watched"]}')
    if events_fired['video_watched'] == 0:
        fire_event(opportunity, "VideoWatched")
        update_event_fired(opportunity['id'], 'video_watched')
        print('VideoWatched event fired')

def add_sale(opportunity):
    fire_event(opportunity, "Sale")
    update_event_fired(opportunity['id'], 'sale_event_fired')

def fire_event(opportunity, event_name):
    full_name = opportunity['name']
    name_parts = full_name.split()
    first_name = name_parts[0]
    last_name = name_parts[-1]
    print(f'Opportunity ad account {opportunity["ad_account"]}')
    ad_account = opportunity['ad_account'] if 'ad_account' in opportunity and opportunity['ad_account'] != None else ''
    data = {
        "Email": opportunity['email'],
        "First Name": first_name,
        "Last Name": last_name,
        "Phone": opportunity['phone'],
        "FBP": opportunity['fbp'],
        "FBC": opportunity['fbc'],
        "Event Name": event_name,
        "Account ID": ad_account
    }
    headers = {"Content-Type": "application/json"}


