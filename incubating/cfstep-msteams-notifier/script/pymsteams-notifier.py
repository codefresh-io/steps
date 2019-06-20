import json
import os
import pymsteams


def main():
    cf_account = os.getenv('CF_ACCOUNT')
    cf_commit_author = os.getenv('CF_COMMIT_AUTHOR')
    cf_branch = os.getenv('CF_BRANCH')
    cf_build_url = os.getenv('CF_BUILD_URL')
    cf_commit_message = os.getenv('CF_COMMIT_MESSAGE')
    cf_commit_url = os.getenv('CF_COMMIT_URL')
    cf_pull_request_action = os.getenv('CF_PULL_REQUEST_ACTION')
    cf_pull_request_number = os.getenv('CF_PULL_REQUEST_NUMBER')
    cf_status_message = os.getenv('CF_STATUS_MESSAGE', 'EXECUTED')
    cf_repo_name = os.getenv('CF_REPO_NAME')
    cf_revision = os.getenv('CF_REVISION')
    msteams_activity_image = os.getenv('MSTEAMS_ACTIVITY_IMAGE', 'https://steps.codefresh.io/assets/img/loading.gif')
    mstreams_activity_subtitle = os.getenv('MSTEAMS_ACTIVITY_SUBTITLE', 'Build Status: {}'.format(cf_status_message))
    msteams_activity_text = os.getenv('MSTEAMS_ACTIVITY_TEXT', 'Additional Information Below')
    msteams_link_text = os.getenv('MSTEAMS_LINK_TEXT', 'Codefresh Build Logs')
    msteams_link_text_2 = os.getenv('MSTEAMS_LINK_TEXT_2', 'Commit Information')
    msteams_link_url = os.getenv('MSTEAMS_LINK_URL', cf_build_url)
    msteams_link_url_2 = os.getenv('MSTEAMS_LINK_URL_2', cf_commit_url)
    msteams_new_webhook_url = os.getenv('MSTEAMS_NEW_WEBHOOK_URL')
    msteams_text = os.getenv('MSTEAMS_TEXT', 'Codefresh Account: {}'.format(cf_account))
    msteams_title = os.getenv('MSTEAMS_TITLE', 'Codefresh Build Notification')
    msteams_webhook_url = os.getenv('MSTEAMS_WEBHOOK_URL')

    # You must create the connectorcard object with the Microsoft Webhook URL
    myTeamsMessage = pymsteams.connectorcard(msteams_webhook_url)

    # Add title to the message
    myTeamsMessage.title(msteams_title)

    # Add text to the message.
    myTeamsMessage.text(msteams_text)

    # Add button and link to the message.
    if msteams_link_url:
        myTeamsMessage.addLinkButton(msteams_link_text, msteams_link_url)
    
    # Add button and link to the message.
    if msteams_link_url_2:
       myTeamsMessage.addLinkButton(msteams_link_text_2, msteams_link_url_2) 
    
    # create the section
    myMessageSection = pymsteams.cardsection()

    # Activity Elements
    myMessageSection.activitySubtitle(mstreams_activity_subtitle)
    myMessageSection.activityImage(msteams_activity_image)
    myMessageSection.activityText(msteams_activity_text)

    # Facts are key value pairs displayed in a list.
    if cf_repo_name:
        myMessageSection.addFact("GIT Repository", cf_repo_name)
    if cf_branch:
        myMessageSection.addFact("GIT Branch", cf_branch)
    if cf_revision:
        myMessageSection.addFact("GIT Revision", cf_revision)
    if cf_commit_author:
        myMessageSection.addFact("Commit Author", cf_commit_author)
    if cf_commit_message:
        myMessageSection.addFact("Commit Message", cf_commit_message)
    if cf_pull_request_number:
        myMessageSection.addFact("Pull Request Number", cf_pull_request_number)
    if cf_pull_request_action:
        myMessageSection.addFact("Pull Request Action", cf_pull_request_action)

    # Add your section to the connector card object before sending
    myTeamsMessage.addSection(myMessageSection)

    # Send to additional room
    myTeamsMessage.newhookurl(msteams_webhook_url)

    myTeamsMessage.printme()

    # send the message.
    myTeamsMessage.send()


if __name__ == "__main__":
    main()
