#!/bin/sh
set -e

msg() { echo -e "INF---> $1"; }
err() { echo -e "ERR---> $1" ; exit 1; }

JSON_PAYLOAD={\"tag\":{\"registry\":\"$REGISTRY\",\"repo\":\"$IMAGE_NAME\",\"tag\":\"$IMAGE_TAG\"}}
SETTINGS=$(echo $JSON_PAYLOAD | jq ".tag" )
msg "Settings used:\n$SETTINGS"

curl -X POST -k -s \
  -u $PC_USERNAME:$PC_PASSWORD \
  -H 'Content-Type: application/json' \
  -d $JSON_PAYLOAD $PC_PROTOCOL://$PC_HOSTNAME:$PC_PORT/api/v1/registry/scan

OUT=$?
if [ $OUT -ne 0 ];then
   err "Security Scan could not be initiated"
fi

msg "Security Scan initiated"
TIMEOUT_SECS=$((10 * 60))
until [[ "$SCAN_FINISH_STATUS" = "completed" ]] || [[ $TIMEOUT_SECS -lt 0 ]]; do
  sleep 2
  TIMEOUT_SECS=$((TIMEOUT_SECS-2))
  scan_current_status=$(curl -X GET -k -s -u $PC_USERNAME:$PC_PASSWORD -G $PC_PROTOCOL://$PC_HOSTNAME:$PC_PORT/api/v1/registry -d search=$IMAGE_NAME:$IMAGE_TAG -d limit=1 | cut -c5-6)
  if [ "$scan_current_status" = id ]; then  
    SCAN_FINISH_STATUS="completed"
    msg "Scan completed"
  elif [ "$scan_current_status" = '' ]; then  
    SCAN_FINISH_STATUS="Running scan"
    msg "$SCAN_FINISH_STATUS"
  else
    err $scan_current_status
  fi
done

if [ $TIMEOUT_SECS -le 2 ]; then 
  err "Timeout while trying to scan the image, or image was not found in registry"
fi

REPORT_NAME=$(echo ''$IMAGE_NAME:$IMAGE_TAG | tr /: _)
curl -X GET -ks -u $PC_USERNAME:$PC_PASSWORD -G $PC_PROTOCOL://$PC_HOSTNAME:$PC_PORT/api/v1/registry -d search=$IMAGE_NAME:$IMAGE_TAG -d limit=1 -o TL_report_$REPORT_NAME.json
msg "Report Downloaded to $(pwd)/TL_report_$REPORT_NAME.json"

COMPLIANCE_RISK_SCORE=$(cat TL_report_$REPORT_NAME.json | jq ".[0].complianceRiskScore")
VULNERABILITY_RISK_SCORE=$(cat TL_report_$REPORT_NAME.json | jq ".[0].vulnerabilityRiskScore")
COMPLIANCE_VULNERABILITIES_CNT=$(cat TL_report_$REPORT_NAME.json | jq ".[0].complianceIssuesCount")
CVE_VULNERABILITIES_CNT=$(cat TL_report_$REPORT_NAME.json | jq ".[0].vulnerabilitiesCount")

msg "Compliance Risk Score: $COMPLIANCE_RISK_SCORE"
msg "Count of Compliance Violations: $COMPLIANCE_VULNERABILITIES_CNT"
msg "CVE Vulnerability Risk Score: $VULNERABILITY_RISK_SCORE"
msg "Count of CVE Vulnerabilties: $CVE_VULNERABILITIES_CNT"

case $COMPLIANCE_THRESHOLD in
     low)      
          COMPLIANCE_THRESHOLD=1
          ;;
     medium)      
          COMPLIANCE_THRESHOLD=10
          ;;
     high)
          COMPLIANCE_THRESHOLD=100
          ;; 
     critical)
          COMPLIANCE_THRESHOLD=1000
          ;;
     *)
          echo COMPLIANCE_THRESHOLD must be low|medium|high|critical
          ;;
esac

case $VULNERABILITY_THRESHOLD in
     low)      
          VULNERABILITY_THRESHOLD=1
          ;;
     medium)      
          VULNERABILITY_THRESHOLD=10
          ;;
     high)
          VULNERABILITY_THRESHOLD=100
          ;; 
     critical)
          VULNERABILITY_THRESHOLD=1000
          ;;
     *)
          echo VULNERABILITY_THRESHOLD must be low|medium|high|critical
          ;;
esac

if [ $COMPLIANCE_RISK_SCORE -ge $COMPLIANCE_THRESHOLD ]; then 
  err "COMPLIANCE_THRESHOLD ($COMPLIANCE_THRESHOLD) EXEECED => $COMPLIANCE_VULNERABILITIES_CNT issue(s) found. COMPLIANCE_RISK_SCORE = $COMPLIANCE_RISK_SCORE (lower is better)"
else
  msg "COMPLIANCE CHECK => PASSED"
fi
if [ $VULNERABILITY_RISK_SCORE -ge $VULNERABILITY_THRESHOLD ]; then 
  err "VULNERABILITY_THRESHOLD ($VULNERABILITY_THRESHOLD) EXEECED => $CVE_VULNERABILITIES_CNT issue(s) found. VULNERABILITY_RISK_SCORE = $VULNERABILITY_RISK_SCORE (lower is better)"
else 
  msg "CVEVULNERABILITY CHECK => PASSED"
fi