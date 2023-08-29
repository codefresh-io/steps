FROM microsoft/azure-cli
WORKDIR /home
COPY . .
#ENTRYPOINT /home/entrypoint.sh
RUN chmod +x /home/entrypoint.sh
CMD ["/home/entrypoint.sh"]
