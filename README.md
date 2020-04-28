# tap-zoom

This is a [Singer](https://www.singer.io/) tap that produces JSON-formatted data following the Singer spec.

See the getting [started guide for running taps.](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#running-singer-with-python)

This tap:

- Pulls raw data from the [Zoom API](https://marketplace.zoom.us/docs/api-reference/introduction)
- Extracts the following resources:
  - [users](https://marketplace.zoom.us/docs/api-reference/zoom-api/users/users)
  - [meetings](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetings)
  - [meeting_registrants](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingregistrants)
  - [meeting_polls](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingpolls)
  - [meeting_poll_results](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/listpastmeetingpolls)
  - [meeting_questions](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingregistrantsquestionsget)
  - [meeting_files](https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/listpastmeetingfiles)
  - [webinars](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinars)
  - [webinar_panelists](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarpanelists)
  - [webinar_registrants](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarregistrants)
  - [webinar_absentees](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarabsentees)
  - [webinar_polls](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarpolls)
  - [webinar_poll_results](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/listpastwebinarpollresults)
  - [webinar_questions](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarregistrantsquestionsget)
  - [webinar_tracking_sources](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/gettrackingsources)
  - [webinar_qna_results](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/listpastwebinarqa)
  - [webinar_files](https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/listpastwebinarfiles)
  - [report_meetings](https://marketplace.zoom.us/docs/api-reference/zoom-api/reports/reportmeetingdetails)
  - [report_meeting_participants](https://marketplace.zoom.us/docs/api-reference/zoom-api/reports/reportmeetingparticipants)
  - [report_webinars](https://marketplace.zoom.us/docs/api-reference/zoom-api/reports/reportwebinardetails)
  - [report_webinar_participants](https://marketplace.zoom.us/docs/api-reference/zoom-api/reports/reportwebinarparticipants)
- Outputs the schema for each resource

### Data Replication

- The Zoom API does not support incremental replocation, all data is replicate everytime the tap runs.
- Zoom appears to "expire" meetings and webinars over time, making them unavailable to the API. Make sure your data lands in a trusted destination, as it may be the only place it eventually becomes available.

### Authentication

The Zoom tap supports two methods of authentication:
- JWT - A JWT token that can be [generated in the Zoom UI](https://marketplace.zoom.us/docs/guides/auth/jwt). This is probably the easiest option for tap users self-hosting.
- OAuth 2.0 - [Zoom OAuth](https://marketplace.zoom.us/docs/guides/auth/oauth) using a refresh token.

#### OAuth Scopes

The following OAuth scopes are required:
- meeting:read:admin
- webinar:read:admin
- user:read:admin
- account:read:admin
- report:read:admin

### Config File

#### Using JWT

```json
  {
      "jwt": <JWT>
  }
  ```

#### Using OAuth

```json
  {
      "client_id": <CLIENT_ID>,
      "client_secret": <CLIENT_SECRET>,
      "refresh_token": <REFRESH_TOKEN>
  }
  ```

---

Copyright &copy; 2020 Stitch
