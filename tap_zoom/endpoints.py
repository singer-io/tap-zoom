
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
                        'pk': ['uuid'],
                        'provides': {
                            'webinar_uuid': 'uuid'
                        },
                        'children': {
                            'webinar_absentees': {
                                'path': 'past_webinars/{webinar_uuid}/absentees',
                                'pk': ['webinar_uuid', 'id'],
                                'data_key': 'registrants',
                                'ignore_http_error_codes': [404]
                            },
                            'webinar_poll_results': {
                                'paginate': False,
                                'path': 'past_webinars/{webinar_uuid}/polls',
                                'pk': ['webinar_uuid', 'email'],
                                'data_key': 'questions'
                            },
                            'webinar_qna_results': {
                                'paginate': False,
                                'path': 'past_webinars/{webinar_uuid}/qa',
                                'pk': ['webinar_uuid', 'email'],
                                'data_key': 'questions'
                            },
                            'webinar_files': {
                                'paginate': False,
                                'path': 'past_webinars/{webinar_uuid}/files',
                                'pk': ['webinar_uuid', 'file_name'],
                                'data_key': 'in_meeting_files'
                            }
                        }
                    },
                    'webinar_panelists': {
                        'path': 'webinars/{webinar_id}/panelists',
                        'pk': ['webinar_id', 'id'],
                        'data_key': 'panelists'
                    },
                    'webinar_registrants': {
                        'path': 'webinars/{webinar_id}/registrants',
                        'pk': ['webinar_id', 'id'],
                        'data_key': 'registrants'
                    },
                    'webinar_polls': {
                        'path': 'webinars/{webinar_id}/polls',
                        'pk': ['webinar_id', 'id'],
                        'data_key': 'polls'
                    },
                    'webinar_questions': {
                        'paginate': False,
                        'path': 'webinars/{webinar_id}/registrants/questions',
                        'pk': ['webinar_id', 'id'],
                        'data_key': 'questions',
                        'ignore_zoom_error_codes': [3000]
                    },
                    'webinar_tracking_sources': {
                        'path': 'webinars/{webinar_id}/tracking_sources',
                        'pk': ['webinar_id', 'id'],
                        'data_key': 'tracking_sources'
                    }
                }
            }
        }
    }
}
