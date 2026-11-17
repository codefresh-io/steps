# ----- Go Builder ------
#
FROM golang:1.26.11-alpine3.23 AS go

WORKDIR /src

# download modules first to cache them between builds
COPY go.mod go.sum ./
RUN go mod download

# copy sources
COPY cfjenkins.go ./

RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /cfjenkins .

#
# ------ Release ------
#
FROM alpine:3.23

# Go on Linux reads the system CA pool, so ca-certificates decides which roots are trusted
RUN apk --no-cache add ca-certificates

COPY --from=go /cfjenkins /usr/local/bin/

# Run locally docker run -it --rm -e jenkins_url="http://192.168.1.73:8080" -e jenkins_username="vadim" -e jenkins_token="testtoken" -e jenkins_job_name="testjob" -e jenkins_parameterized_job="false" local/cfjenkins
CMD ["/usr/local/bin/cfjenkins"]
