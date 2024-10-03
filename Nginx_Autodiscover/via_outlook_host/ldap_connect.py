import os
from dotenv import load_dotenv
from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES, Tls, MODIFY_REPLACE, set_config_parameter
from ldap3.core.exceptions import LDAPBindError
import redis
from CycLog import CycleLogger

if __name__ == "__main__":
    denv_path = os.path.join(os.path.dirname(__file__), '.env')

    if os.path.exists(denv_path):
        load_dotenv(dotenv_path=denv_path,verbose=True, override=True)

    set_config_parameter('DEFAULT_SERVER_ENCODING', 'utf-8')
    set_config_parameter('ADDITIONAL_SERVER_ENCODINGS', 'koi8-r')


    ldap_host = os.environ.get('LDAP_HOST')
    ldap_port = os.environ.get('LDAP_PORT')
    ldap_user = os.environ.get('LDAP_USER')
    ldap_password = os.environ.get('LDAP_PASSWORD')
    ldap_filter = os.environ.get('SEARCH_FILTER')
    attrib_list = list(os.environ.get('ATTRIB_LIST').split(','))
    log_file = os.environ.get('LOG_FILE')
    max_lines = int(os.environ.get('LOG_MAX_LINES'))

    logger = CycleLogger(file_name=log_file, max_lines=max_lines)
    logger.log('Start')
  
    server = Server(ldap_host, port=ldap_port, get_info=ALL) 
    try:
        conn = Connection(server, user=ldap_user, password=ldap_password, auto_bind=True)
    except LDAPBindError as e:
        print(f'Can not connect to LDAP - "automatic bind not successful - invalidCredentials". Exit.')
        logger.log(f'Can not connect to LDAP - "automatic bind not successful - invalidCredentials". Exit.')
        exit(1)
            
    conn.search('OU=Office,dc=yandry,dc=ru', ldap_filter, search_scope=SUBTREE, attributes=attrib_list, get_operational_attributes=True)
    if conn.last_error is not None:
        print(f'Can not connect to LDAP. Exit.')
        logger.log(f'Error - Can not connect to LDAP. Exit.')
        exit(1)

    # for item in conn.entries:
    #         print(item['mail'])

    try:
        red = redis.Redis(host='localhost', db=0, charset="utf-8", decode_responses=True)
    except redis.exceptions.ConnectionError as e:
        print(f'Error connecting: {e}')
        logger.log(f'Error connecting: {e}. Exit.')
        exit(1)

    for item in conn.entries:
            if len(item['mail']) > 0:
                try:
                    if not red.exists(str(item['mail'])) :
                        print(f"Add new mail - {item['mail']}.")
                        logger.log(f"Add new mail - {item['mail']}.")
                        red.set(str(item['mail']), str(item['displayName']))
                except redis.exceptions.ConnectionError as e:
                    print(f'Error connecting: {e}')
                    logger.log(f'Error connecting: {e}. Exit.')
                    exit(1)
    
    mail_list = [e['mail'] for e in conn.entries]
    for key in red.scan_iter():
        if key not in mail_list and key != 'xml':
            print(f'Delete mail {str(key)} from cache.')
            logger.log(f'Delete mail {str(key)} from cache.')
            red.delete(key)


