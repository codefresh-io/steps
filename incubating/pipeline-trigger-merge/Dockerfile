FROM codefresh/cli

COPY merge.sh loop-merge.sh /

RUN chmod +x /*.sh

ENTRYPOINT ["/merge.sh"]
