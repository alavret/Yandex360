import os
from dotenv import load_dotenv
from datetime import datetime
from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES, Tls, MODIFY_REPLACE, set_config_parameter
from ldap3.core.exceptions import LDAPBindError
from CycLog import CycleLogger
from lib.y360_api.api_script import API360


def get_ldap_users():

    set_config_parameter('DEFAULT_SERVER_ENCODING', 'utf-8')
    set_config_parameter('ADDITIONAL_SERVER_ENCODINGS', 'koi8-r')


    ldap_host = os.environ.get('LDAP_HOST')
    ldap_port = int(os.environ.get('LDAP_PORT'))
    ldap_user = os.environ.get('LDAP_USER')
    ldap_password = os.environ.get('LDAP_PASSWORD')
    ldap_search = []
    ldap_search.append([os.environ.get('LDAP_BASE_DN_1'), os.environ.get('SEARCH_FILTER_1')])
    ldap_search.append([os.environ.get('LDAP_BASE_DN_2'), os.environ.get('SEARCH_FILTER_2')])

    attrib_list = list(os.environ.get('ATTRIB_LIST').split(','))
    out_file = os.environ.get('OUT_FILE')

    users = {}
    server = Server(ldap_host, port=ldap_port, get_info=ALL, use_ssl=True) 
    try:
        conn = Connection(server, user=ldap_user, password=ldap_password, auto_bind=True)
    except LDAPBindError as e:
        saveToLog(message=f'Can not connect to LDAP - "automatic bind not successful - invalidCredentials". Exit.', status='Error', console=console)
        return {}
            
    all_users = {}
    for each_filter in ldap_search:
        users = {}
        conn.search(each_filter[0], each_filter[1], search_scope=SUBTREE, attributes=attrib_list, get_operational_attributes=True)
        if conn.last_error is not None:
            saveToLog(message=f'Can not connect to LDAP. Exit.', status='Error', console=console)
            return {}

        try:            
            for item in conn.entries:
                if len(item['mail']) > 0 and item['mail'].value is not None:
                    if item['department'].value is not None:
                        department = item['department'].value
                    else:
                        department = ''
                    users[item['mail'].value] = department.strip()
            all_users.update(users)

        except Exception as e:
            saveToLog(message=f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}", status='Error', console=console)
            return {}
        
    if out_file:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write("mail;department\n")
            for item in all_users:
                f.write(f"{item['mail']};{department}\n")

    return all_users

def get_file_users():

    file = os.environ.get('USERS_FILE')
    users = {}
    try:
        with open(file, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line and ';' in line:
                    mail, department = line.split(";")
                    users[mail.strip()] = department.strip()
    except Exception as e:
        saveToLog(message=f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}", status='Error', console=console)
    
    return users

def generate_deps_list_from_api():
    all_deps_from_api = organization.get_departments_list()
    if len(all_deps_from_api) == 1:
        #print('There are no departments in organozation! Exit.')
        return {}
    all_deps = {'1' : 'All'}
    for item in all_deps_from_api:  
        all_deps[item['id']] = item['name'].strip()

    return all_deps

def add_new_deps_to_y360(new_deps):
    for item in new_deps:
        department_info = {
                    "name": item,
                    "parentId": 1
                }
        saveToLog(message=f'Adding department {item} to Y360', status='Info', console=console)
        if not dry_run:
            organization.post_create_department(department_info)
    new_deps = generate_deps_list_from_api()
    return new_deps

def compare_with_y360():    
    users_org = {}
    users_id = {}

    #onprem_users = get_file_users()
    onprem_users = get_ldap_users()
    if not onprem_users:
        saveToLog(message=f'List of local users is empty. Exit.', status='Warning', console=console)
        return
    else:
        saveToLog(message=f'Got list of local users. Total count: {len(onprem_users)}' , status='Info', console=console)
    
    temp_deps = {k: v for k, v in onprem_users.items() if v}
    onprem_deps =  set(temp_deps.values())
    if not onprem_deps:
        saveToLog(message=f'List of local departments is empty. Exit.', status='Warning', console=console)
        return
    else:
        saveToLog(message=f'Got list of local departments. Total count: {len(onprem_deps)}' , status='Info', console=console)
    
    deps = generate_deps_list_from_api()
    if not deps:
        saveToLog(message=f'List of Y360 departments is empty. Exit.', status='Warning', console=console)
        return
    else:
        saveToLog(message=f'Got list of Y360 departments. Total count: {len(deps)}' , status='Info', console=console)

    
    set_deps = set(deps.values())
    diff_set = onprem_deps.difference(set_deps)
    if diff_set:
        saveToLog(message=f'List of local departments is not equal to Y360 departments. Add new departments.', status='Warning', console=console)
        for dep in diff_set:
            saveToLog(message=f'Deps for adding to Y360 - {dep}', status='Info', console=console)
        #return
    else:
        saveToLog(message=f'List of local departments is equal to Y360 departments.', status='Info', console=console)

    deps = add_new_deps_to_y360(diff_set)

    for user in organization.get_all_users():
        users_org[user['email']] = user['departmentId']
        users_id[user['email']] = user['id']

    if not users_org:
        saveToLog(message=f'List of Y360 users is empty. Exit.', status='Warning', console=console)
        return
    else:
        saveToLog(message=f'Got list of Y360 users. Total count: {len(users_org)}' , status='Info', console=console)

    try:
        for email in users_org.keys():
            if email in onprem_users: 
                #print(f"{email} - {onprem_users[email]}")   
                if not (len(onprem_users[email].strip()) == 0 or onprem_users[email].strip() =='[]') :
                    if onprem_users[email].strip() != deps[users_org[email]]:
                        new_deps_id = list(deps.keys())[list(deps.values()).index(onprem_users[email].strip())]
                        saveToLog(message=f'Try to change department of {email} user from _ {deps[users_org[email]]} _ to _ {onprem_users[email]} _', status='Info', console=console)
                        if not dry_run:
                            organization.patch_user_info(
                                uid = users_id[email],
                                user_data={
                                    "departmentId": new_deps_id,
                                })
                else:
                    if users_org[email] != 1:
                        saveToLog(message=f'Try to change department of {email} user from _ {deps[users_org[email]]} _ to _ All _', status='Info', console=console)
                        if not dry_run:
                            organization.patch_user_info(
                                    uid = users_id[email],
                                    user_data={
                                        "departmentId": 1,
                                    })
    except Exception as e:
        saveToLog(message=f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}", status='Error', console=console)
    
    return
                
def saveToLog(status = 'Info', message = '', console = False):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    logger.log(f'{current_time:<25} {status:>10} {message}')
    if console:
        print(f'{current_time:<25} {status:>10} {message}')

if __name__ == "__main__":
    denv_path = os.path.join(os.path.dirname(__file__), '.env_ldap')

    if os.path.exists(denv_path):
        load_dotenv(dotenv_path=denv_path,verbose=True, override=True)
    
    organization = API360(os.environ.get('orgId'), os.environ.get('access_token'))

    log_file = os.environ.get('LOG_FILE')
    max_lines = int(os.environ.get('LOG_MAX_LINES'))
    console = bool(os.environ.get('COPY_LOG_TO_CONSOLE'))
    logger = CycleLogger(file_name=log_file, max_lines=max_lines)
    dry_run = bool(os.environ.get('DRY_RUN'))

    saveToLog(status='Info',message =       '---------------Start-----------------', console=console)
    if dry_run:
        saveToLog(status='Warning',message ='- Режим тестового прогона включен (DRY_RUN = True)! Изменеия не сохраняются! -', console=console)

    compare_with_y360()

    saveToLog(status='Info',message ='---------------End------------------', console=console)
    #users = get_file_users(users_file)
    #print(users)
    #compare_with_y360()
  