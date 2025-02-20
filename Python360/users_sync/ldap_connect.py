import os
from dotenv import load_dotenv
# from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES, Tls, MODIFY_REPLACE, set_config_parameter
# from ldap3.core.exceptions import LDAPBindError

import getpass
#import ldb
from samba.auth import system_session
from samba.credentials import Credentials
from samba.dcerpc import security
from samba.dcerpc.security import dom_sid
from samba.ndr import ndr_pack, ndr_unpack
from samba.param import LoadParm
from samba.samdb import SamDB


# import redis
from CycLog import CycleLogger

if __name__ == "__main__":
    denv_path = os.path.join(os.path.dirname(__file__), '.env')

    if os.path.exists(denv_path):
        load_dotenv(dotenv_path=denv_path,verbose=True, override=True)

    set_config_parameter('DEFAULT_SERVER_ENCODING', 'utf-8')
    set_config_parameter('ADDITIONAL_SERVER_ENCODINGS', 'koi8-r')


    ldap_host = os.environ.get('LDAP_HOST')
    ldap_port = int(os.environ.get('LDAP_PORT'))
    ldap_user = os.environ.get('LDAP_USER')
    ldap_password = os.environ.get('LDAP_PASSWORD')
    ldap_filter = os.environ.get('SEARCH_FILTER')
    ldap_base_dn = os.environ.get('LDAP_BASE_DN')
    attrib_list = list(os.environ.get('ATTRIB_LIST').split(','))
    log_file = os.environ.get('LOG_FILE')
    max_lines = int(os.environ.get('LOG_MAX_LINES'))
    out_file = os.environ.get('OUT_FILE')

    logger = CycleLogger(file_name=log_file, max_lines=max_lines)
    logger.log('Start')

    lp = LoadParm()
    creds = Credentials()
    creds.guess(lp)
    creds.set_username(ldap_user)
    creds.set_password(ldap_password)
    samdb = SamDB(url=f'ldap://{ldap_host}:{ldap_port}', session_info=system_session(),credentials=creds, lp=lp)
  
    result = samdb.search(ldap_base_dn, expression=ldap_filter, scope=ldb.SCOPE_SUBTREE)
    for item in result:
        if 'sAMAccountName' in item:
            print(item['distinguishedName'])
            print(item['sAMAccountName'])
    # server = Server(ldap_host, port=ldap_port, get_info=ALL) 
    # try:
    #     conn = Connection(server, user=ldap_user, password=ldap_password, auto_bind=True)
    # except LDAPBindError as e:
    #     print(f'Can not connect to LDAP - "automatic bind not successful - invalidCredentials". Exit.')
    #     logger.log(f'Can not connect to LDAP - "automatic bind not successful - invalidCredentials". Exit.')
    #     exit(1)
            
    # conn.search(ldap_base_dn, ldap_filter, search_scope=SUBTREE, attributes=attrib_list, get_operational_attributes=True)
    # if conn.last_error is not None:
    #     print(f'Can not connect to LDAP. Exit.')
    #     logger.log(f'Error - Can not connect to LDAP. Exit.')
    #     exit(1)

    # for item in conn.entries:
    #         print(item['mail'])

    with open(out_file, "w") as f:
        f.write("mailaddress;Department\n")
        for item in result:
            if 'sAMAccountName' in item:
                f.write(f"{item['mailaddress']};{item['Department']}\n")
  


