import os
from pdpyras import APISession
from pdpyras import ChangeEventsAPISession

def main():

    api_token = os.getenv('API_TOKEN')
    assignee_user_id = os.getenv('ASSIGNEE_USER_ID')
    cf_build_id = os.getenv('CF_BUILD_ID')
    cf_build_url = os.getenv('CF_BUILD_URL')
    event_source = os.getenv('EVENT_SOURCE')
    event_summary = os.getenv('EVENT_SUMMARY')
    from_email = os.getenv('FROM_EMAIL')
    service_id = os.getenv('SERVICE_ID')
    title = os.getenv('TITLE')
    pagerduty_type = os.getenv('PAGERDUTY_ALERT_TYPE')

    if pagerduty_type == 'incident':
        session = APISession(api_token, default_from=from_email)

        payload = {
            'type': 'incident',
            'title': '{}'.format(title),
            'service': {
                'id': '{}'.format(service_id),
                'type': 'service_reference'
            }
        }
        if assignee_user_id:
            payload['assignments'] =
            [
                {
                    'assignee': {
                        'id': '{}'.format(assignee_user_id),
                        'type': 'user_reference'
                    },
                }
            ],
        }

        pd_incident = session.rpost('incidents', json=payload)

    elif pagerduty_type == 'change_event':

        session = ChangeEventsAPISession(api_token)

        pd_change_event = session.submit(
            summary='{}'.format(event_summary),
            source='{}'.format(event_source),
            custom_details={"Build ID":'{}'.format(cf_build_id)},
            links=[{'href':'{}'.format(cf_build_url)}]
        )


if __name__ == "__main__":
    main()
