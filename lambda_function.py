"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6
 
For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""
 
import requests
import xml.etree.ElementTree as etree
from datetime import datetime as dt
from bs4 import BeautifulSoup
import logging


def get_papers(num_papers):
    url = "https://arxiv.org/list/cs.LG/recent"
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    papers = soup.find_all("div", attrs={"class":"meta"})
    paper_info = []
    for cnt, paper in enumerate(papers):
        title = ":".join(paper.find_all("div", attrs = {"class":"list-title mathjax"})[0].text.split(":")[1:])[:-1].strip()
        authors = paper.find("div", attrs = {"class":"list-authors"}).find_all("a")
        author_names = []
        for author in authors:
            author_names.extend([author.text])
        authors = ", ".join(author_names[:-1])+" and "+author_names[-1]
        paper_info.extend(["{}, published by {}".format(title, authors)])
        if cnt == (num_papers-1):
            break

    return paper_info
 
def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    logging.info("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
 
    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")
 
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
 
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
 
 
def on_session_started(session_started_request, session):
    """ Called when the session starts """
 
    logging.info("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])
 
 
def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
 
    logging.info("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()
 
 
def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
 
    logging.info("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
 
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
 
    # Dispatch to your skill's intent handlers
    if intent_name == "GetPapersIntent":
        return get_machine_learning_papers(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        session_attributes = {}
        card_title = "Good Bye"
        speech_output = "Leaving Machine Learning Paper Fetcher"
        reprompt_text = ""
        should_end_session = True
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    else:
        raise ValueError("Invalid intent")
 
 
def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
 
    Is not called when the skill returns should_end_session=true
    """
    logging.info("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here
 
# --------------- Functions that control the skill's behavior ------------------
 
 
def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
 
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa Machine Learning Paper Fetcher. " \
                    "Please ask me for machine learning papers by saying, " \
                    "Catch me up, or by saying, What are the latest papers that have been published?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask me for machine learning papers by saying by saying, " \
                    "Catch me up, or by saying, What are the latest papers that have been published?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
 
 
def get_machine_learning_papers(intent, session):
    """ Grabs our bus times and creates a reply for the user
    """
 
    card_title = "Fetching Machine Learning papers"
    slots = intent['slots']
    num_papers = int(slots['numPapers']['value'])
    session_attributes = {}
    should_end_session = True
    papers = get_papers(num_papers)
    speech_output = "Listing all papers. " + ". The next paper is, ".join(papers)
    reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

 
 
# --------------- Helpers that build all of the responses ----------------------
 
 
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }
 
 
def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }