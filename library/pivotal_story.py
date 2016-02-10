#!/usr/bin/python

import json
BASE_URL = 'https://www.pivotaltracker.com/services/v5'

## borrowed from jira module: https://github.com/ansible/ansible-modules-extras/blob/devel/web_infrastructure/jira.py

def request(url, token, data=None, method='GET'):
    if data:
        data = json.dumps(data)

    response, info = fetch_url(module, url, data=data, method=method, 
                               headers={'Content-Type':'application/json', 'X-TrackerToken': token})

    if info['status'] not in (200, 201, 204):
        module.fail_json(msg=info['msg'])

    body = response.read()

    if body:
        return json.loads(body)
    else:
        return {}

def post(url, token, data):
    return request(url, token, data=data, method='POST')

def put(url, token, data):
    return request(url, token, data=data, method='PUT')

def delete(url, token):
    return request(url, token, method='DELETE')    

def get(url, token):
    return request(url, token)

def validate_inputs(required_fields):

    invalid_fields = [field for field in required_fields if module.params[field]]

    if len(invalid_fields) > 0:
        module.fail_json(msg="The following parameters are missing: %s" % (op, ",".join(invalid_fields)))
    

def _create_story(module, token):

    validate_inputs(required_fields = ['name', 'state'])

    project_id = module.params['project_id']
    url = '{0}/projects/{1}/stories' . format (BASE_URL, project_id)

    optional_fields = ['description', 'story_type', 'estimate']
    data = {
        'name': module.params['name'],
        'current_state': module.params['state']
    }        
    required_fields = ['name', 'state']

    for field in optional_fields:
        if module.params[field] is not None:
            data[field] = module.params[field]

    return post(url, token, data)

def _delete_story(module, token):

    validate_inputs(required_fields = ['story_id'])

    story_id = module.params['story_id']
    project_id = module.params['project_id']

    if story_id is None:
        return module.fail_json(msg='story_id is required to delete a story')

    url = '{0}/projects/{1}/stories/{2}' . format (BASE_URL, project_id, story_id)
    return delete(url, token)




def main():
    '''
    ../../ansible/hacking/test-module -m ./pivotal_story.py -a "state=unstarted project_id=1134194 name=test api_token=..."
    '''
    global module

    args = dict(
        state = dict(choices=['accepted', 'delivered', 'finished', 'started', 'rejected', 'planned', 'unstarted', 'unscheduled', 'absent'], default='unstarted'),
        project_id = dict(required=True, type='int'),
        name = dict(type='str'),
        api_token = dict(type='str'),
        story_id = dict(type='int'),
        description = dict(type='str'),
        story_type = dict(choices=['feature', 'bug', 'chore', 'release']),
        estimate = dict(type='int'),
        validate_certs = dict(type='bool', default='no'),
    )

    required_one_of = (['name', 'story_id'],)

    module = AnsibleModule(argument_spec=args, required_one_of=required_one_of, supports_check_mode=False)
    
    try:
        api_token = module.params['api_token'] or os.environ['PIVOTAL_API_TOKEN']
    except KeyError, e:
        module.fail_json(msg='no api_token provided')

    try:        
        state = module.params['state']
        if state is not 'absent':
            result = _create_story(module, api_token)
        else:
            result = _delete_story(module, api_token)
        module.exit_json(changed=True, meta=result)

    except Exception as e:
        return module.fail_json(msg=e.message)


from ansible.module_utils.basic import *
from ansible.module_utils.urls import *


if __name__ == '__main__':
    main()
