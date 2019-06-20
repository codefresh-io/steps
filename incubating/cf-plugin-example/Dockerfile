FROM alpine
LABEL MAINTAINER="Anton Weiss"  CATEGORY="Codefresh Plugins"
WORKDIR /home
ENV CF_PLUGIN_NAME="ExamplePlugin"
COPY . .
ENTRYPOINT /home/entrypoint.sh
