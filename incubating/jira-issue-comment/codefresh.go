package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
)

type Annotation struct {
	EntityId   string `json:"entityId"`
	EntityType string `json:"entityType"`
	Key        string `json:"key"`
	Value      string `json:"value"`
}

func createBuildAnnotation(environment Config) {
	annotation := Annotation{
		EntityId:   environment.CodefreshBuildId,
		EntityType: "build",
		Key:        "jira-issue-url",
		Value:      environment.JiraBaseUrl + "/browse/" + environment.JiraIssueId,
	}

	annotationJson, err := json.Marshal(annotation)
	if err != nil {
		fmt.Printf("Formatting annotation JSON failed with error %s\n", err)
	}

	request, err := http.NewRequest("POST", "https://g.codefresh.io/api/annotations", bytes.NewBuffer(annotationJson))
	if err != nil {
		fmt.Println(err)
	}

	request.Header.Add("Authorization", environment.CodefreshApiKey)
	request.Header.Add("Content-Type", "application/json")

	client := &http.Client{}
	response, err := client.Do(request)

	if err != nil {
		fmt.Printf("Codefresh annotation request failed with error %s\n", err)
	} else {
		data, _ := ioutil.ReadAll(response.Body)
		fmt.Println("Codefresh annotation creation successful")
		fmt.Println(string(data))
	}
}

func exportCommentIdVariable(environment Config) {
	fmt.Println("environment.JiraCommentId: " + environment.JiraCommentId)

	if fileExists(environment.CodefreshVolumePath + "/env_vars_to_export") {
		f, err := os.OpenFile(environment.CodefreshVolumePath+"/env_vars_to_export", os.O_APPEND|os.O_WRONLY, 0600)
		if err != nil {
			fmt.Println("Error opening env_vars_to_export file")
			panic(err)
		} else {
			defer f.Close()

			if _, err = f.WriteString("JIRA_COMMENT_ID=" + environment.JiraCommentId + "\n"); err != nil {
				fmt.Println("Error writing JIRA_COMMENT_ID to env_vars_to_export file")
				panic(err)
			}
		}
	} else {
		fmt.Println("File:" + environment.CodefreshVolumePath + "/env_vars_to_export" +
			"doesn't exist. Unable to write build variable JIRA_COMMENT_ID")
	}

}

func fileExists(filename string) bool {
	info, err := os.Stat(filename)
	if os.IsNotExist(err) {
		return false
	}
	return !info.IsDir()
}
