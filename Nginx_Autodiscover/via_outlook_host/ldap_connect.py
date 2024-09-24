import os
from dotenv import load_dotenv
from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES, Tls, MODIFY_REPLACE
import redis
from CycLog import CycleLogger

if __name__ == "__main__":
    denv_path = os.path.join(os.path.dirname(__file__), '.env')

    if os.path.exists(denv_path):
        load_dotenv(dotenv_path=denv_path,verbose=True, override=True)

    ldap_host = os.environ.get('LDAP_HOST')
    ldap_user = os.environ.get('LDAP_USER')
    ldap_password = os.environ.get('LDAP_PASSWORD')
    ldap_filter = os.environ.get('SEARCH_FILTER')
    attrib_list = list(os.environ.get('ATTRIB_LIST').split(','))
    log_file = os.environ.get('LOG_FILE')
    max_lines = int(os.environ.get('LOG_MAX_LINES'))

    logger = CycleLogger(file_name=log_file, max_lines=max_lines)
    logger.log('Start')

    #server = server = Server('ldap_host', get_info=ALL)    

    conn = Connection(ldap_host, user=ldap_user, password=ldap_password, auto_bind=True)
    conn.search('OU=Office,dc=yandry,dc=ru', ldap_filter, search_scope=SUBTREE, attributes=attrib_list, get_operational_attributes=True)
    if conn.last_error is not None:
        print(f"Can not connect to LDAP. Exit.")
        logger.log(f'Error - Can not connect to LDAP. Exit.')
        exit(1)

    # for item in conn.entries:
    #         print(item['mail'])

    try:
        red = redis.Redis(host='localhost', db=0, charset="utf-8", decode_responses=True)
    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting: {e}")
        logger.log(f"Error connecting: {e}. Exit.")
        exit(1)

    for item in conn.entries:
            if len(item['mail']) > 0:
                try:
                    if not red.exists(str(item['mail'])):
                        print(f"Add new mail - {item['mail']}.")
                        logger.log(f"Add new mail - {item['mail']}.")
                        red.set(str(item['mail']), str(item['displayName']))
                except redis.exceptions.ConnectionError as e:
                    print(f"Error connecting: {e}")
                    logger.log(f"Error connecting: {e}. Exit.")
                    exit(1)
    
    mail_list = [e['mail'] for e in conn.entries]
    for key in red.scan_iter():
        if key not in mail_list:
            print(f'Delete mail {str(key)} from cache.')
            logger.log(f'Delete mail {str(key)} from cache.')
            red.delete(key)


