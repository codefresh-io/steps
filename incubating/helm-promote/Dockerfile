FROM mikefarah/yq:4.12.2

WORKDIR /workdir

COPY --chown=yq promote.sh .

RUN chmod +x promote.sh

ENTRYPOINT ["/workdir/promote.sh"]