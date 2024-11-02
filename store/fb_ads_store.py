from db.connection_manager import *

def get_all_ad_accounts():
    connection = create_connection()
    with connection.cursor() as cursor:
        cursor.execute('''SELECT ad_account_id, ad_account_name, ad_account_currency,
                        ad_account_access_token, app_id, app_secret, last_updated
                        FROM facebook_ad_accounts''')
        ad_accounts = cursor.fetchall()
        account_list = []
        for account in ad_accounts:
            account_list.append({
                'ad_account_id': account[0],
                'ad_account_name': account[1],
                'ad_account_currency': account[2],
                'ad_account_access_token': account[3],
                'app_id': account[4],
                'app_secret': account[5],
                'last_updated': account[6]
            })
        cursor.close()
        connection.close()
        return account_list
    
    