package main

import (
	"os"
)

func main() {
	app := setupCli()
	app.Run(os.Args)
}
