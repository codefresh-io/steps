Backblaze B2 upload step

This plugin helps to upload files to Backblaze B2 in any stage of pipeline.

The **APPLICATION_KEY**, **APPLICATION_KEY_ID** and **BUCKET_ID** must be set as the pipeline variables or as the step arguments.

To upload - add list of file paths to the **FILES** arguments: 
```
FILES:
 - /path/to/file-1
 - /path/to/file-2
```
