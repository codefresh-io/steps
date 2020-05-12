package main

import (
	"bytes"
	b64 "encoding/base64"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
)

type Request struct {
	MethodType          string
	Url                 string
	AuthorizationHeader string
	ContentType         string
	Payload             *strings.Reader
}

func sendComment(environment Config) string {
	var request Request
	request = setupRequest(environment)
	if environment.Verbose {
		verboseLogging(environment, request)
	}

	client := &http.Client{}
	req, err := http.NewRequest(request.MethodType, request.Url, request.Payload)

	if err != nil {
		fmt.Println(err)
	}

	req.Header.Add("Authorization", request.AuthorizationHeader)
	req.Header.Add("Content-Type", "application/json")

	res, err := client.Do(req)
	defer res.Body.Close()
	body, err := ioutil.ReadAll(res.Body)

	responseBody := string(body)
	fmt.Println("Response Body\n" + string(responseBody))
	responseJson := map[string]interface{}{}
	json.Unmarshal([]byte(responseBody), &responseJson)
	commentId := responseJson["id"].(string)
	fmt.Println("\nNew Comment Id: ", commentId)
	return commentId
}

func setupRequest(environment Config) Request {
	var request Request
	if len(environment.JiraCommentId) > 0 {
		request.MethodType = "PUT"
		request.Url = environment.JiraBaseUrl + "rest/api/2/issue/" + environment.JiraIssueId + "/comment" +
			"/" + environment.JiraCommentId
	} else {
		request.MethodType = "POST"
		request.Url = environment.JiraBaseUrl + "rest/api/2/issue/" + environment.JiraIssueId + "/comment"
	}

	request.AuthorizationHeader = "Basic " + b64.StdEncoding.EncodeToString([]byte(environment.JiraUsername+":"+environment.JiraApiKey))
	request.Payload = strings.NewReader(buildCommentBody(environment))

	return request
}

func verboseLogging(environment Config, request Request) {
	fmt.Println("\nVerbose Logging")
	fmt.Println("Base Url: ", environment.JiraBaseUrl)
	fmt.Println("Jira Issue Key: " + environment.JiraIssueId)
	fmt.Println("Full Url: " + request.Url)
	fmt.Println("Username: ", environment.JiraUsername)
	fmt.Println("API Key: ", environment.JiraApiKey)
	fmt.Println("Authorization Header: ", request.AuthorizationHeader)
	fmt.Printf("Comment Info: %v\n", environment.InfoValues)
	fmt.Println("Comment Payload: ", request.Payload)
	fmt.Println()
}

func buildCommentBody(environment Config) string {
	var buffer bytes.Buffer
	buffer.WriteString("{\"body\": \"")

	for i, currentValue := range environment.InfoValues {
		i = i
		buffer.WriteString(currentValue.DisplayText + currentValue.Value + "\\n")
	}

	buffer.WriteString("\"}")

	return buffer.String()
}
