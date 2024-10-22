from flask import Blueprint, request, render_template, jsonify
from flask_login import login_required
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from datetime import datetime
import os
from facebook_business.exceptions import FacebookRequestError
from store.fb_ads_store import get_all_ad_accounts
from store.metrics_store import update_marketing_spend
facebook_blueprint = Blueprint('facebook', __name__)

def get_ad_spend_for_account(ad_account, start_date, end_date):
    FacebookAdsApi.init(ad_account['app_id'], ad_account['app_secret'], ad_account['ad_account_access_token'])
    # Create an AdAccount object
    account = AdAccount(f'act_{ad_account["ad_account_id"]}')
    # Define the fields and parameters for the API request
    fields = ['spend']
    params = {
        'time_range': {'since': start_date, 'until': end_date},
        'level': 'account',
    }

    try:
        # Make the API request to get the ad spend data
        insights = account.get_insights(fields=fields, params=params)

        # Extract the total spend for the month
        total_spend = sum(float(insight['spend']) for insight in insights)

        return total_spend
    except FacebookRequestError as e:
        error_message = f"Facebook API error: {e.api_error_message()}"
        print(error_message)  # Log the error
        return None
    
def get_ad_spend_for_month(month, year):
    # Initialize the Facebook Ads API
    ad_accounts = get_all_ad_accounts()

    # Set the date range for the specified month
    start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
    end_date = datetime(year, month + 1, 1).strftime('%Y-%m-%d') if month < 12 else datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
    total_ad_spend = 0
    for ad_account in ad_accounts:
        ad_spend = get_ad_spend_for_account(ad_account, start_date, end_date)
        if ad_spend is not None:
            total_ad_spend += ad_spend
    return total_ad_spend
    

# Add a route to display the ad spend
@facebook_blueprint.route('/ad_spend/<int:year>/<int:month>')
@login_required
def display_ad_spend(year, month):
    month_number = month
    if isinstance(month, str):
        # convert October to 10
        month_number = datetime.strptime(month, '%B').month
    ad_spend = get_ad_spend_for_month(month_number, year)
    if ad_spend is None:
        return jsonify({'error': 'Failed to retrieve ad spend data. Please check your permissions and try again.'}), 400
    update_marketing_spend(month, year, ad_spend)
    return jsonify({'ad_spend': ad_spend})
