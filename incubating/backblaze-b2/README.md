Backblaze B2 upload step

This plugin helps to upload files to Backblaze B2 in any stage of pipeline.

You can upload several files at once. Use UPLOAD_FILE_ prefix for file variables.
Each file variable is an array of:
- file path (required)
- file name in bucket (required)
- file MIME type (optional, if omitted type will be detected from file extension)

```
List of env variables:
APPLICATION_KEY_ID - required
APPLICATION_KEY    - required
BUCKET_ID          - required
UPLOAD_FILE_N      - required, one or several file descriptions
```
