
ENDPOINTS_CONFIG = {
    'users': {
        'path': 'users',
        'pk': ['id'],
        'data_key': 'users',
        'forced-replication-method': 'FULL_TABLE',
        'provides': {
            'user_id': 'id'
        },
        'children': {
            'list_meetings': {
                'parent': 'users',
                'persist': False,
                'path': 'users/{user_id}/meetings',
                'data_key': 'meetings',
                'provides': {
                    'meeting_id': 'id'
                },
                'children': {
                    'meetings': {
                        'parent': 'list_meetings',
                        'paginate': False,
                        'path': 'meetings/{meeting_id}',
                        'pk': ['uuid'],
                        'forced-replication-method': 'FULL_TABLE',
                        'provides': {
                            'meeting_uuid': 'uuid'
                        },
                        'children': {
                            'meeting_poll_results': {
                                'parent': 'meetings',
                                'paginate': False,
                                'path': 'past_meetings/{meeting_uuid}/polls',
                                'pk': ['meeting_uuid', 'email'],
                                'forced-replication-method': 'FULL_TABLE',
                                'data_key': 'questions'
                            }
                        }
                    },
                    'meeting_registrants': {
                        'parent': 'list_meetings',
                        'path': 'meetings/{meeting_id}/registrants',
                        'pk': ['meeting_id', 'id'],
                        'forced-replication-method': 'FULL_TABLE',
                        'data_key': 'registrants'
                    },
                    'meeting_polls': {
                        'parent': 'list_meetings',
                        'path': 'meetings/{meeting_id}/polls',
                        'pk': ['meeting_id', 'id'],
                        'forced-replication-method': 'FULL_TABLE',
                        'data_key': 'polls'
                    },
                    'meeting_questions': {
                        'parent': 'list_meetings',
                        'paginate': False,
                        'path': 'meetings/{meeting_id}/registrants/questions',
                        'pk': ['meeting_id'],
                        'forced-replication-method': 'FULL_TABLE',
                        'ignore_zoom_error_codes': [3000]
                    },
                    'report_meetings': {
                        'parent': 'list_meetings',
                        'paginate': False,
                        'path': 'report/meetings/{meeting_id}',
                        'pk': ['uuid'],
                        'forced-replication-method': 'FULL_TABLE'
                    },
                    'report_meeting_participants': {
                        'parent': 'list_meetings',
                        'path': 'report/meetings/{meeting_id}/participants',
                        'pk': ['meeting_id', 'id'],
                        'forced-replication-method': 'FULL_TABLE',
                        'data_key': 'participants'
                    }
                }
            },
            'list_webinars': {
                'parent': 'users',
                'persist': False,
                'path': 'users/{user_id}/webinars',
                'data_key': 'webinars',
                'ignore_zoom_error_codes': [200],
                'provides': {
                    'webinar_id': 'id'
                },
                'children': {
                    'webinars': {
                        'parent': 'list_webinars',
                        'paginate': False,
                        'path': 'webinars/{webinar_id}',
                        'pk': ['uuid'],
                        'forced-replication-method': 'FULL_TABLE',
                        'provides': {
                            'webinar_uuid': 'uuid'
                        },
                        'children': {
                            'webinar_absentees': {
                                'parent': 'webinars',
                                'path': 'past_webinars/{webinar_uuid}/absentees',
                                'pk': ['webinar_uuid', 'id'],
                                'forced-replication-method': 'FULL_TABLE',
                                'data_key': 'registrants',
                                'ignore_http_error_codes': [404]
                            },
                            'webinar_poll_results': {
                                'parent': 'webinars',
                                'paginate': False,
                                'path': 'past_webinars/{webinar_uuid}/polls',
                                'pk': ['webinar_uuid', 'email'],
                                'forced-replication-method': 'FULL_TABLE',
                                'data_key': 'questions'
                            },
                            'webinar_qna_results': {
                                'parent': 'webinars',
                                'paginate': False,
                                'path': 'past_webinars/{webinar_uuid}/qa',
                                'pk': ['webinar_uuid', 'email'],
                                'forced-replication-method': 'FULL_TABLE',
                                'data_key': 'questions'
                            }
                        }
                    },
                    'webinar_panelists': {
                        'parent': 'list_webinars',
                        'path': 'webinars/{webinar_id}/panelists',
                        'pk': ['webinar_id', 'id'],
                        'forced-replication-method': 'FULL_TABLE',
                        'data_key': 'panelists'
                    },
                    'webinar_registrants': {
                        'parent': 'list_webinars',
                        'path': 'webinars/{webinar_id}/registrants',
                        'pk': ['webinar_id', 'id'],
                        'forced-replication-method': 'FULL_TABLE',
                        'data_key': 'registrants'
                    },
                    'webinar_polls': {
                        'parent': 'list_webinars',
                        'path': 'webinars/{webinar_id}/polls',
                        'pk': ['webinar_id', 'id'],
                        'forced-replication-method': 'FULL_TABLE',
                        'data_key': 'polls'
                    },
                    'webinar_questions': {
                        'parent': 'list_webinars',
                        'paginate': False,
                        'path': 'webinars/{webinar_id}/registrants/questions',
                        'pk': ['webinar_id'],
                        'forced-replication-method': 'FULL_TABLE',
                        'ignore_zoom_error_codes': [3000]
                    },
                    'webinar_tracking_sources': {
                        'parent': 'list_webinars',
                        'path': 'webinars/{webinar_id}/tracking_sources',
                        'pk': ['webinar_id', 'id'],
                        'forced-replication-method': 'FULL_TABLE',
                        'data_key': 'tracking_sources'
                    },
                    'report_webinars': {
                        'parent': 'list_webinars',
                        'paginate': False,
                        'path': 'report/webinars/{webinar_id}',
                        'pk': ['uuid'],
                        'forced-replication-method': 'FULL_TABLE',
                    },
                    'report_webinar_participants': {
                        'parent': 'list_webinars',
                        'path': 'report/webinars/{webinar_id}/participants',
                        'pk': ['webinar_id', 'id'],
                        'forced-replication-method': 'FULL_TABLE',
                        'data_key': 'participants'
                    }
                }
            }
        }
    }
}
