package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"os"
	"strings"

	log "github.com/sirupsen/logrus"
)

type (
	// Jenkins Job parameters
	JenkinsJobParams struct {
		Username  string
		Token     string
		Host      string
		Job       string
		Jobparams string
	}
)

func main() {

	host := os.Getenv("JENKINS_URL")
	token := os.Getenv("JENKINS_TOKEN")
	user := os.Getenv("JENKINS_USERNAME")
	job := os.Getenv("JENKINS_JOB_NAME")
	jobparams := ""

	jenkins := NewJenkinsJobParams(user, token, host, job, jobparams)
	jenkins.trigger()

}

func NewJenkinsJobParams(user string, token string, host string, job string, jobparams string) *JenkinsJobParams {
	host = strings.TrimRight(host, "/")

	return &JenkinsJobParams{
		Username:  user,
		Token:     token,
		Host:      host,
		Job:       job,
		Jobparams: jobparams,
	}
}

func (jenkins *JenkinsJobParams) trigger() {
	if err := jenkins.validate(); err == false {
		os.Exit(1)
	}
	path := fmt.Sprintf("%s/job/%s/%s", jenkins.Host, jenkins.Job, "build")
	log.Info(fmt.Sprintf("Going to trigger %s job on %s", jenkins.Job, jenkins.Host))
	requestURL := jenkins.buildURL(path, url.Values{})
	req, err := http.NewRequest("POST", requestURL, nil)
	if err != nil {
		log.Error(err.Error())
		os.Exit(1)
	}

	resp, err := jenkins.sendRequest(req)
	if err != nil {
		log.Error(err)
		os.Exit(1)
	}
	if resp.StatusCode == 404 {
		log.Error(fmt.Sprintf("The trigger is failed! Job '%s' not found!", jenkins.Job))
		os.Exit(1)
	}
	if resp.StatusCode == 201 || resp.StatusCode == 200 {
		log.Info(resp.Status)
		log.Info(fmt.Sprintf("The %s is triggered successfully", jenkins.Job))
	} else {
		log.Error(fmt.Sprintf("The trigger is failed with status: %s", resp.Status))
		os.Exit(1)
	}

}

func (jenkins *JenkinsJobParams) buildURL(path string, params url.Values) (requestURL string) {
	requestURL = path
	if params != nil {
		queryString := params.Encode()
		if queryString != "" {
			requestURL = requestURL + "?" + queryString
		}
	}
	return
}

func (jenkins *JenkinsJobParams) sendRequest(req *http.Request) (*http.Response, error) {

	req.SetBasicAuth(jenkins.Username, jenkins.Token)
	return http.DefaultClient.Do(req)
}

func (jenkins *JenkinsJobParams) parseResponse(resp *http.Response, body interface{}) (err error) {
	defer resp.Body.Close()

	if body == nil {
		return
	}

	data, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return
	}

	return json.Unmarshal(data, body)
}

func (jenkins *JenkinsJobParams) validate() bool {
	if len(jenkins.Host) == 0 && !strings.HasPrefix(jenkins.Host, "${{") {
		log.Error("JENKINS_URL is required!")
		return false
	} else if len(jenkins.Token) == 0 && !strings.HasPrefix(jenkins.Token, "${{") {
		log.Error("JENKINS_TOKEN is required!")
		return false
	} else if len(jenkins.Username) == 0 && !strings.HasPrefix(jenkins.Username, "${{") {
		log.Error("JENKINS_USERNAME is required!")
		return false
	} else if len(jenkins.Job) == 0 && !strings.HasPrefix(jenkins.Job, "${{") {
		log.Error("JENKINS_JOB is required!")
		return false
	} else {
		return true
	}
}
