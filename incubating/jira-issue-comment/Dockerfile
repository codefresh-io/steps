FROM golang:alpine

# Set necessary environmet variables needed for our image
ENV GO111MODULE=auto \
    CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64

WORKDIR /app

# Copy the code into the container
COPY . .

# Build the application
RUN go build -o main .

ENTRYPOINT ["/app/main"]