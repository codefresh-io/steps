/**
 * Mark a deployment for an application in New Relic
 * https://docs.newrelic.com/docs/apm/new-relic-apm/maintenance/record-monitor-deployments/#api
 *
 * All payload parameters are optional except revision
 * payload data:
 *  revision
 *  changelog
 *  description
 *  user
 *  timestamp
**/

const axios = require('axios');
const util = require('util');
const fs = require('fs');
const { Console } = require('console');

const base_api_url = process.env.API_URL || "https://api.newrelic.com/v2";
const api_key = process.env.API_KEY;

const app_id = process.env.APPLICATION_ID;
let debug = false;

const deployment_marker_data = {
    deployment: {
        revision: process.env.REVISION,
        user: process.env.AUTHOR,
        changelog: process.env.CHANGELOG,
        description: process.env.DESCRIPTION,
        // Can include a timestamp, but newrelic will do this for us
        //timestamp: new Date().toISOString()
    }
}

// Mark a new relic deployment using the API
function markDeployment(){
    // Format the URL
    let url = util.format("%s/%s/%s/%s", base_api_url, "applications", app_id, "deployments.json");

    // Add request headers
    let headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    };

    console.log("Creating a deployment marker for %s",  app_id);
    if (debug) {
        console.log("Sending data %s to url %s with headers %s", JSON.stringify(deployment_marker_data.deployment), url, JSON.stringify(headers));
    }
    // POST to the API endpoint
    const res = axios({
        method: "post",
        url: url,
        headers: headers,
        data: deployment_marker_data
    }).then(res => { // Log out success
        if (debug){
            console.log(`Status Code: ${res.status}`);
            console.log(`Response: ${JSON.stringify(res.data)}`);
        }
        console.log("Success! Deployment marked it New Relic")
    }).catch(error => { // Log out error and quit
        console.error(`Status Code: ${error.status}`);
        console.error(`Error: ${JSON.stringify(error.data)}`);

        // Exit with error code if we run into an error
        process.exit(1);
    });

    return res
}

function main(){
    if(process.env.DEBUG){
        debug = (process.env.DEBUG.toLowerCase() === "true");
    }
    markDeployment();
}

main();