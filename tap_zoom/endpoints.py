
ENDPOINTS_CONFIG = {
    'users': {
        'path': 'users',
        'pk': ['id'],
        'data_key': 'users',
        'provides': {
            'user_id': 'id'
        },
        'children': {
            'list_webinars': {
                'persist': False,
                'path': 'users/{user_id}/webinars',
                'data_key': 'webinars',
                'provides': {
                    'webinar_id': 'id'
                },
                'children': {
                    'webinars': {
                        'paginate': False,
                        'path': 'webinars/{webinar_id}',
                        'pk': ['uuid']
                    },
                    'webinar_panelists': {
                        'path': 'webinars/{webinar_id}/panelists',
                        'pk': ['id'],
                        'data_key': 'panelists'
                    }
                }
            }
        }
    }
}
