
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import tweepy
import pickle 
import sqlite3
from sqlite3 import Error
from fake_useragent import UserAgent
import time 
 

def random_header():
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    return(headers)

# ----------------------------- SQLite DB Code Start ------------------------
def make_db(db_file):
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    finally:
        conn.close()

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None
 
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
# ---------------------------- SQLite DB End ----------------------------------


# ---------------------------- Ebay Handling of Email addresses ---------------
def insert_ebay(conn, ebay_data):
    sql = ''' INSERT INTO ebay(email, link)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, ebay_data)
    conn.commit()
    return cur.lastrowid

def search_ebay(search_word, search_page):

    list_long_link = []

    # NON EU ITEMS MAY NOT HAVE SELLER EMAIL
    list_global_ebay = [
        "eBay.de",
        "ebay.at",
        "eBay.be",
        "eBay.fr",
        "eBay.it",
        "eBay.nl",
        "eBay.pl",
        "eBay.es"
    ]

    for ebay_country in list_global_ebay:
        #----------------------------------ebay.x---------searchitem--page---itemsperpage
        repsonse= requests.get('https://www.{0}/sch/i.html?_nkw={1}&_pgn={2}&_ipg=200'.format(ebay_country, search_word, search_page),headers=random_header())

        soup = BeautifulSoup(repsonse.text, 'html.parser')

        all_links = soup.findAll('a', attrs={'class' : 'vip'})

        for a_link in all_links:
            link = a_link["href"]
            list_long_link.append(link)

    return list_long_link

def get_email(link):
    """
    Only works on business ebay Accounts
    Only works on EU Accounts(only they have Impressum)
    """
    ebay_link = link
    ebay_email_list = []
    final_email_list = []

    response = requests.get(link,headers=random_header())

    email_list = re.findall(r'[\w\.-]+@[\w\.-]+', response.text)
    dirty_mail = []
    for email in email_list:
        if len(email.split(".")[0]) > 3:
            dirty_mail.append(email)
        else:
            email = email[::-1]
            dirty_mail.append(email)
    
    email_set = set(dirty_mail)
    clean_email = list(email_set)

    for mail in clean_email:

        ebay_email_list.append(mail)

    for stil_dirty_mail in ebay_email_list:
        if str(str(stil_dirty_mail)[-1]) == ".":
            clean_dirty_mail = stil_dirty_mail[:-1]
            final_email_list.append(clean_dirty_mail)
        else:
            final_email_list.append(stil_dirty_mail)
            
    if len(final_email_list) > 0:
        return ebay_link, final_email_list
    else:
        return "nothing", ["nothing"]

def check_email(conn, tuple_data, table_name):
    tuple_data = tuple_data[0]
    sql = "SELECT count(*) as count FROM {0} WHERE email = '{1}'".format(table_name, tuple_data)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    
    in_db = rows[0][0]

    return in_db, table_name, tuple_data

def write_ebay_table(conn, list_ebay_links):

    for link in list_ebay_links:

        ebay_link, ebay_email_list = get_email(link)

        if ebay_link == "nothing":
            pass
        else:
            for email in ebay_email_list:

                ebay_data = (email, ebay_link)
                in_db_count, table_name, email_name = check_email(conn, ebay_data, "ebay")

                if int(in_db_count) != 0:
                    log_output("- {0} is already in \"{1}\" table.".format(email_name, table_name))
                        
                else:
                    insert_ebay(conn, ebay_data)
                    log_output("+ {0} added to table \"{1}\"".format(email_name, table_name))

# ---------------------------- Ebay Handling of Email addresses End ---------------


# ---------------------------- Pasetbin Password and Email Handling ---------------
def insert_pastebin_password(conn, pastebin_data):
    sql = ''' INSERT INTO pastebin(email, password)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, pastebin_data)
    conn.commit()
    return cur.lastrowid

def insert_tweet_id(conn, tweet_id):
    cur = conn.cursor()
    cur.execute('INSERT INTO tweets VALUES (NULL,\"{}\")'.format(tweet_id))
    conn.commit()
    return cur.lastrowid

def check_pastebin_tweet(conn, tweet_id):

    sql = "SELECT count(*) as count FROM tweets WHERE tweet_id = '{0}'".format(tweet_id)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    
    in_db = rows[0][0]

    if in_db > 0:
        return True
    else:
        return False


def tuple_switcher(tuple_to_switch):
    item_one = tuple_to_switch[0]
    item_two = tuple_to_switch[1]

    tuple_to_switch = item_two,item_one

    return(tuple_to_switch)


def filter_tweets(tweet):

    list_user_pass = []

    if "username:password" in str(tweet._json["full_text"]):
        key_tweet_id = tweet._json["id_str"] # save to db to check if we have this tweet already 
        paste_link = tweet._json["entities"]["urls"]#[0]["expanded_url"] # gets the link to the pastebin site
        resp = requests.get(paste_link[0]["expanded_url"],headers=random_header())
        
        # only works when perfect xyz@gmail.com:password   format
        passw_list = re.findall(r"^(.*):(.+)",resp.text, re.MULTILINE)
        for passw in passw_list:

            email_passw = passw[1].strip() #-----------Y gets the password from the data

            if len(re.findall(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', email_passw)):
                correct_order = tuple_switcher(passw)   #------------------> gives the correct tuple back
                list_user_pass.append(correct_order)
            else:
                email_user = passw[0].strip()
                pass_user = passw[1].strip()
                if len(re.findall(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', email_user)):
                    user_pass = email_user, pass_user
                    list_user_pass.append(user_pass)
                else:
                    log_output("- Dirty Format: {}:{}".format(email_user, email_passw))

        return key_tweet_id, list_user_pass
    else:
        return "false", ["false"]

def write_pastebin_table(conn, list_pastebin_userpass):

    for userpass in list_pastebin_userpass:
        username = userpass[0]
        username = username.strip()
        passw    = userpass[1]
        pastebin_data = (username, passw)
        insert_pastebin_password(conn, pastebin_data)


def collect_pastebin_twitter(conn):

    with open('tokens_twitter.pickle', 'rb') as handle:
        tokens = pickle.load(handle)
        
    cons_key = tokens["cons_key"] 
    cons_sec = tokens["cons_sec"] 
    accs_tok = tokens["accs_tok"] 
    accs_sec = tokens["accs_sec"] 

    auth = tweepy.OAuthHandler(cons_key, cons_sec)
    auth.set_access_token(accs_tok, accs_sec)
    api = tweepy.API(auth)

    json_tweets = api.user_timeline(screen_name = 'leak_scavenger', count = 50, tweet_mode = 'extended')

    for tweet in json_tweets:
        tweet_id, list_user_pass = filter_tweets(tweet)

        in_db = check_pastebin_tweet(conn,tweet_id)
        if in_db:
            print("- Data from tweet_id:{} already in table.".format(tweet_id))
        else:
            if tweet_id != "false":
                write_pastebin_table(conn, list_user_pass)
        
                insert_tweet_id(conn, tweet_id)

# ---------------------------- Pasetbin Password and Email Handling End ---------------


def trending_ebay():
    from trending_ebay import Ebaytrend
    ebaytrend = Ebaytrend()
    list_ebay_trends = ebaytrend.get_items()

    return list_ebay_trends

def log_output(line_to_log):
    import logging 
    log = "ebay_email.log"
    logging.basicConfig(filename=log,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    logging.info(line_to_log)

def show_all_tables(conn):
    show_table(conn, "ebay")
    #show_table(conn, "tweets")
    show_table(conn, "pastebin")
    #show matches 
    find_matches_sql = "SELECT pastebin.email, pastebin.password FROM ebay, pastebin WHERE ebay.email = pastebin.email"
    df = pd.read_sql_query(find_matches_sql, conn)
    print(df)

def show_table(conn, table_name):
    df = pd.read_sql_query("select * from {0};".format(table_name), conn)
    print(df)

def main():
    database = "ebay_email.db"
    make_db(database)
    conn = create_connection(database)


    sql_create_ebay_table = """ CREATE TABLE IF NOT EXISTS ebay (
                                        id integer PRIMARY KEY,
                                        email text NOT NULL,
                                        link text NOT NULL
                                    ); """

    sql_create_password_table = """CREATE TABLE IF NOT EXISTS pastebin (
                                    id integer PRIMARY KEY,
                                    email text NOT NULL,
                                    password text NOT NULL
                                );"""

    sql_create_tweet_id_table = """CREATE TABLE IF NOT EXISTS tweets (
                                    id integer PRIMARY KEY,
                                    tweet_id text NOT NULL
                                );"""
    with conn:
        if conn is not None:

            print("Starting Twitter-Pastebin module...")
            # --- for pastebin
            collect_pastebin_twitter(conn)
            print("Twitter-Pastebin finished !")


            print("Starting eBay module....")
            # create ebay table
            create_table(conn, sql_create_ebay_table)
            # create pastebin password table
            create_table(conn, sql_create_password_table)
            # create tweet_id table to check if we parsed it
            create_table(conn, sql_create_tweet_id_table)

            
            # --- for ebay
            for trend in trending_ebay():
                for page in range(1, 6):
                    
                    list_ebay_links = search_ebay(trend,page)

                    try:
                        write_ebay_table(conn, list_ebay_links)
                    except:
                        sleeper = 15
                        log_output(" - CONNECT ERROR, GONNA SLEEP AND RETRY IN {}".format(sleeper))
                        print("Got an ERROR gonna retry conenction in {} sconds.".format(sleeper))
                        time.sleep(sleeper)
                        log_output("RETRY NOW")

                print("eBay module ist finished.")

            # show our db at the end of the script     
            show_all_tables(conn)
            
        else:
            print("Error! cannot create the database connection.")

    conn.close()

main()

