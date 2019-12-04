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
		Username         string
		Token            string
		Host             string
		Job              string
		Buildparams      string
		Parameterizedjob string
	}
)

func main() {
	host := os.Getenv("jenkins_url")
	token := os.Getenv("jenkins_token")
	user := os.Getenv("jenkins_username")
	job := os.Getenv("jenkins_job_name")
	buildParams := GetBuildParams()
	parameterizedJob := os.Getenv("jenkins_parameterized_job")
	fmt.Println(buildParams)
	fmt.Println(parameterizedJob)
	jenkins := NewJenkinsJobParams(user, token, host, job, buildParams, parameterizedJob)
	jenkins.trigger()
}

func GetBuildParams() string {
	Values := url.Values{}
	for _, line := range os.Environ() {
		if strings.HasPrefix(line, "build_param_") {
			s := strings.TrimPrefix(line, "build_param_")
			pair := strings.SplitN(s, "=", 2)
			Values.Add(pair[0], pair[1])
		}
	}
	return Values.Encode()
}

func NewJenkinsJobParams(user string, token string, host string, job string, buildParams string, parameterizedJob string) *JenkinsJobParams {
	host = strings.TrimRight(host, "/")
	return &JenkinsJobParams{
		Username:         user,
		Token:            token,
		Host:             host,
		Job:              job,
		Buildparams:      buildParams,
		Parameterizedjob: parameterizedJob,
	}
}

func (jenkins *JenkinsJobParams) trigger() {
	if err := jenkins.validate(); err == false {
		os.Exit(1)
	}

	requestUrl := fmt.Sprintf("%s/job/%s/%s", jenkins.Host, jenkins.Job, "build")
	if jenkins.Parameterizedjob == "true" {
		if jenkins.Buildparams == "" {
			log.Info(fmt.Sprintf("No build parameters provided!"))
			log.Info(fmt.Sprintf("Continue with default parameters!"))
			requestUrl = fmt.Sprintf("%s/job/%s/%s", jenkins.Host, jenkins.Job, "buildWithParameters")
		} else {
			log.Info(fmt.Sprintf("Parameters provided!"))
			requestUrl = fmt.Sprintf("%s/job/%s/%s", jenkins.Host, jenkins.Job, "buildWithParameters"+"?"+jenkins.Buildparams)
		}
	}
	log.Info(fmt.Sprintf("Going to trigger %s job on %s", jenkins.Job, jenkins.Host))

	req, err := http.NewRequest("POST", requestUrl, nil)
	if err != nil {
		log.Error(err.Error())
		os.Exit(1)
	}
	req.SetBasicAuth(jenkins.Username, jenkins.Token)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		log.Error(err)
		os.Exit(1)
	}
	switch resp.StatusCode {
	case 404:
		log.Error(fmt.Sprintf("The trigger is failed! Job \"%s\" not found", jenkins.Job))
		os.Exit(1)
	case 200:
		log.Info(fmt.Sprintf("Parameterized job \"%s\" is triggered successfully", jenkins.Job))
		os.Exit(0)
	case 201:
		log.Info(fmt.Sprintf("Parameterized job \"%s\" is triggered successfully", jenkins.Job))
		os.Exit(0)
	case 400:
		log.Error(fmt.Sprintf("The trigger is failed with status: %s", resp.Status))
		log.Error(fmt.Sprintf("Seems like your jenkins project use parameters. Please set step argument 'jenkins_parameterized_job: true'"))
		os.Exit(1)
	case 500:
		log.Error(fmt.Sprintf("The trigger is failed with status: %s", resp.Status))
		log.Error(fmt.Sprintf("Seems like your jenkins project not use parameters. Please set step argument 'jenkins_parameterized_job: false'"))
		log.Error(fmt.Sprintf("Or set parameterized flag in jenkins project settings"))
	default:
		log.Error(fmt.Sprintf("The trigger is failed with status: %s", resp.Status))
		os.Exit(1)
	}
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
	if len(jenkins.Host) == 0 || strings.HasPrefix(jenkins.Host, "${{") {
		log.Error("jenkins_url is required!")
		return false
	} else if len(jenkins.Token) == 0 || strings.HasPrefix(jenkins.Token, "${{") {
		log.Error("jenkins_token is required!")
		return false
	} else if len(jenkins.Username) == 0 || strings.HasPrefix(jenkins.Username, "${{") {
		log.Error("jenkins_username is required!")
		return false
	} else if len(jenkins.Job) == 0 || strings.HasPrefix(jenkins.Job, "${{") {
		log.Error("jenkins_job_name is required!")
		return false
	} else {
		return true
	}
}
