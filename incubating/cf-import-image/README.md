# Import Docker Images Codefresh Plugin

Import external Docker images into Codefresh

## Environment Variables

- `IMAGES`: list of comma separated image names (with tags)
- `REGISTRY`: registry DNS name (including port if needed, default to `docker.io`)
- `USERNAME`: Docker registry user name (optional)
- `PASSWORD`: Docker registry password (optional)
- `CF_URL`: Codefresh URL
- `CF_API_TOKEN`: Codefresh API Token
