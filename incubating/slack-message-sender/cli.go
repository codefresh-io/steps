package main

import (
	log "github.com/sirupsen/logrus"
	"github.com/urfave/cli"
)

func setupCli() *cli.App {
	app := cli.NewApp()
	app.Name = "slack-message-sender"
	setupCommands(app)
	return app
}

func setupCommands(app *cli.App) {
	app.Commands = []cli.Command{
		{
			Name:        "send",
			Description: "Send message to slack channel using webhook",
			Action:      sendToChannel,
			Before: func(c *cli.Context) error {
				log.SetLevel(log.WarnLevel)
				log.SetFormatter(&log.TextFormatter{})
				if c.IsSet("verbose") {
					log.SetLevel(log.InfoLevel)
					log.Info("In verbose mode, dont be afraid... ")
				}
				return nil
			},
			Flags: []cli.Flag{
				cli.StringFlag{
					Name:   "webhook-url",
					EnvVar: "WEBHOOK_URL",
				},
				cli.BoolFlag{
					Name:   "verbose, v",
					EnvVar: "DEBUG",
				},
				cli.StringFlag{
					Name:   "message, m",
					EnvVar: "SLACK_MESSAGE",
				},
			},
		},
	}
}
