package main

import (
	"fmt"
	"strings"
	"net/url"
	"net/http"
	"io/ioutil"
	"encoding/json"
	"os"
	log "github.com/sirupsen/logrus"
)

type (
	// Jenkins Job parameters
	JenkinksJobParams struct {
		Username string
		Token    string
		Host	string
		Job	string
		JobParams	string
	}

)

func main() {

	host:= os.Getenv("JENKINS_URL")
	token:= os.Getenv("JENKINS_TOKEN")
	user:= os.Getenv("JENKINS_USER")
	job:= os.Getenv("JENKINS_JOB")

	jenkins := NewJenkinksJobParams(user, token, host,job,"")
	jenkins.trigger()

}


func NewJenkinksJobParams(user string, token string, host string, job string, jobparams string) *JenkinksJobParams {
	host = strings.TrimRight(host, "/")
	return &JenkinksJobParams{
		Username:    user,
		Token:	token,
		Host: host,
		Job:job,
		JobParams:jobparams,
	}
}
func (jenkins *JenkinksJobParams) trigger() {
	if !jenkins.validate() {
		return
	}
	path := fmt.Sprintf("%s/job/%s/%s", jenkins.Host, jenkins.Job,"build")
	log.Info(fmt.Sprintf("Going to trigger %s job on %s", jenkins.Job, jenkins.Host))
	requestURL := jenkins.buildURL(path, url.Values{})
	req, err := http.NewRequest("POST", requestURL, nil)
	if err != nil {
		log.Error(err.Error())
		return
	}

	resp, err := jenkins.sendRequest(req)
	if err != nil {
		log.Error(err.Error())
		return
	}
	if resp.StatusCode == 404 {
		log.Error(fmt.Sprintf("The trigger is failed! Job '%s' not found!", jenkins.Job))
		return
	}
	if resp.StatusCode == 201 || resp.StatusCode == 200{
		log.Info(resp.Status)
		log.Info(fmt.Sprintf("The %s is triggered successfully", jenkins.Job))
	}else{
		log.Error(fmt.Sprintf("The trigger is failed with status: %s", resp.Status))
	}

}


func (jenkins *JenkinksJobParams) buildURL(path string, params url.Values) (requestURL string) {
	requestURL = path
	if params != nil {
		queryString := params.Encode()
		if queryString != "" {
			requestURL = requestURL + "?" + queryString
		}
	}
	return
}

func (jenkins *JenkinksJobParams) sendRequest(req *http.Request) (*http.Response, error) {

	req.SetBasicAuth(jenkins.Username, jenkins.Token)
	return http.DefaultClient.Do(req)
}

func (jenkins *JenkinksJobParams) parseResponse(resp *http.Response, body interface{}) (err error) {
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

func (jenkins *JenkinksJobParams) validate() bool{

	if len(jenkins.Host) == 0 {
		log.Error("JENKINS_URL is mandatory!")
		return false
	}
	if len(jenkins.Token) == 0 {
		log.Error("JENKINS_TOKEN is mandatory!")
		return false
	}
	if len(jenkins.Username) == 0 {
		log.Error("JENKINS_USER is mandatory!")
		return false
	}
	if len(jenkins.Job) == 0 {
		log.Error("JENKINS_JOB is mandatory!")
		return false
	}
	return true
}
