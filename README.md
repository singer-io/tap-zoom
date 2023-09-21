# tap-zoom

This is a [Singer](https://www.singer.io/) tap that produces JSON-formatted data following the Singer spec.

See the getting [started guide for running taps.](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#running-singer-with-python)

This tap:

- Pulls raw data from the [Zoom API](https://marketplace.zoom.us/docs/api-reference/introduction)
- Extracts the following resources:
  - [users](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/users)
  - [meetings](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/meeting)
  - [meeting_registrants](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/meetingRegistrants)
  - [meeting_polls](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/meetingPolls)
  - [meeting_poll_results](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/listPastMeetingPolls)
  - [meeting_questions](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/meetingRegistrantsQuestionsGet)
  - [webinars](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/webinar)
  - [webinar_panelists](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/webinarPanelists)
  - [webinar_registrants](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/webinarRegistrants)
  - [webinar_absentees](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/webinarAbsentees)
  - [webinar_polls](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/webinarPolls)
  - [webinar_poll_results](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/listPastWebinarPollResults)
  - [webinar_questions](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/webinarRegistrantsQuestionsGet)
  - [webinar_tracking_sources](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/getTrackingSources)
  - [webinar_qna_results](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/listPastWebinarQA)
  - [report_meetings](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/reportMeetingDetails)
  - [report_meeting_participants](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/reportMeetingParticipants)
  - [report_webinars](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/reportWebinarDetails)
  - [report_webinar_participants](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/reportWebinarParticipants)
- Outputs the schema for each resource

### Data Replication

- The Zoom API does not support incremental replocation, all data is replicate everytime the tap runs.
- Zoom appears to "expire" meetings and webinars over time, making them unavailable to the API. Make sure your data lands in a trusted destination, as it may be the only place it eventually becomes available.

### Authentication

The Zoom tap supports two methods of authentication:
- JWT - A JWT token that can be [generated in the Zoom UI](https://marketplace.zoom.us/docs/guides/auth/jwt). This is probably the easiest option for tap users self-hosting. This is deprecating on 1st June 2023 [Ref link](https://developers.zoom.us/docs/platform/auth/jwt/). Hence, removing the jwt support from the code.
- OAuth 2.0 - [Zoom OAuth](https://marketplace.zoom.us/docs/guides/auth/oauth) using a refresh token.

#### OAuth Scopes

The following OAuth scopes are required:
- meeting:read:admin
- webinar:read:admin
- user:read:admin
- account:read:admin
- report:read:admin

### Config File

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
