package main

import (
	"bytes"
	"fmt"
	"net/http"
	"strings"

	log "github.com/sirupsen/logrus"
	"github.com/urfave/cli"
)

func sendToChannel(c *cli.Context) {

	var buffer bytes.Buffer

	url := c.String("webhook-url")
	message := &slackMessage{
		Message: c.String("message"),
	}

	buffer.WriteString(`{ "text": "`)
	buffer.WriteString(message.toString())
	buffer.WriteString(`"}`)

	log.Info(fmt.Sprintf("Sending message to url %s", url))
	log.Info(fmt.Sprintf("Sending message %s", buffer.String()))

	res, err := http.Post(url, "application/x-www-form-urlencoded", strings.NewReader(buffer.String()))
	if err != nil {
		log.Error(err.Error())
	}

	log.Info(res.Status)

	log.Warn("Done")

}

func (sm slackMessage) toString() string {
	return sm.Message
}

type slackMessage struct {
	Message string
}
