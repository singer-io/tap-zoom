
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
                'ignore_zoom_error_codes': [200],
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
                    },
                    'webinar_registrants': {
                        'path': '/webinars/{webinar_id}/registrants',
                        'pk': ['id'],
                        'data_key': 'registrants'
                    },
                    'webinar_polls': {
                        'path': '/webinars/{webinar_id}/polls',
                        'pk': ['id'],
                        'data_key': 'polls'
                    },
                    'webinar_questions': {
                        'paginate': False,
                        'path': '/webinars/{webinar_id}/registrants/questions',
                        'pk': ['id'],
                        'data_key': 'questions',
                        'ignore_zoom_error_codes': [3000]
                    }
                }
            }
        }
    }
}
