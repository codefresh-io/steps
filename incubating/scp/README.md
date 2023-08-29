# scp-plugin

This plugin allow upload file or directory to remote machine using scp protocol.

Required variables:
	CF_SCP_HOST
	CF_SCP_USER_NAME
	CF_SCP_PASSWORD
	CF_SCP_SOURCE= path to resource which will be uploaded, example /codefresh/volume/test.txt
	CF_SCP_TARGET - path to resource on remote machine where resource will be created, example /home/test.txt

Other variables:
	CF_SCP_PORT - default port is 22, use this variable to specify different port.
