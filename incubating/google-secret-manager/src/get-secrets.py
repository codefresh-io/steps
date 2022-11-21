# Import the Secret Manager client library.
from google.cloud import secretmanager

import google_crc32c

import os, subprocess

def access_secret_version(project_id, secret_id, version_id):


    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

     # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"


    # Access the secret version.
    response = client.access_secret_version(request={"name": name})
     
    # Verify payload checksum.
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        print("Data corruption detected.")
        #return response

#test code to print secret in plain text
    
    #print("Plaintext: {}".format(payload))

    payload = response.payload.data.decode("UTF-8")

    env_file = open('/meta/env_vars_to_export', 'w')
    #env_file_test = open('test.txt', 'w')
    subprocess.call(["echo", f"{env_var_key}={payload}"], stdout=env_file)

    #subprocess.run(["echo", f"TEST={payload}", ">>", "/codefresh/volume/env_vars_to_export" ])
#    subprocess.run(["echo", f"TEST={payload}", ">>", "test.txt"])
 #   subprocess.popen(["echo", f"TEST={payload}", ">>", "test2.txt"])

#    subprocess.call(args=["export", "TEST=2"], shell=True)

#    os.environ["secret_var"] = payload

#    print(os.environ["secret_var"])


if __name__ == "__main__":
    # GCP project in which to store secrets in Secret Manager.
    project_id = os.getenv('GCP_PROJECT_ID')

    # ID of the secret to create.
    secret_id = os.getenv('GCP_SECRET_ID')

    version_id= os.getenv('GCP_SECRET_VERSION')
#what to name the environment variable
    env_var_key = os.getenv('ENV_VAR_KEY')

    access_secret_version(project_id, secret_id, version_id)