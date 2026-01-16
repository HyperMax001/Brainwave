"""
LangGraph Gmail Agent with OAuth2 authentication
Reads credentials from .env file and provides Gmail operations
"""

import os
from typing import TypedDict, Annotated, Literal
from datetime import datetime
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


class GmailAgentState(TypedDict):
    """State for the Gmail agent"""
    messages: list
    action: str
    action_input: dict
    result: str
    error: str | None


class GmailAgent:
    """Gmail agent that can read, send, and manage emails"""

    def __init__(self):
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API using credentials from .env"""
        creds = None

        # Check for token file
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Read credentials from .env
                client_id = os.getenv('GMAIL_CLIENT_ID')
                client_secret = os.getenv('GMAIL_CLIENT_SECRET')

                if not client_id or not client_secret:
                    raise ValueError(
                        "GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET must be set in .env file"
                    )

                # Create credentials config
                client_config = {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost"]
                    }
                }

                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)

    def read_emails(self, max_results: int = 10, query: str = "") -> str:
        """Read emails from inbox"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return "No messages found."

            email_list = []
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

                # Get snippet
                snippet = message.get('snippet', '')

                email_list.append(f"From: {sender}\nSubject: {subject}\nDate: {date}\nPreview: {snippet}\n")

            return "\n---\n".join(email_list)

        except HttpError as error:
            return f"An error occurred: {error}"

    def send_email(self, to: str, subject: str, body: str) -> str:
        """Send an email"""
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject

            msg = MIMEText(body)
            message.attach(msg)

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            return f"Email sent successfully! Message ID: {send_message['id']}"

        except HttpError as error:
            return f"An error occurred: {error}"

    def search_emails(self, query: str, max_results: int = 10) -> str:
        """Search emails with a query"""
        return self.read_emails(max_results=max_results, query=query)

    def mark_as_read(self, message_id: str) -> str:
        """Mark an email as read"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return f"Message {message_id} marked as read"
        except HttpError as error:
            return f"An error occurred: {error}"


def parse_action(state: GmailAgentState) -> GmailAgentState:
    """Parse the user's request to determine action"""
    last_message = state["messages"][-1].content.lower()

    # Simple keyword-based routing
    if any(word in last_message for word in ["read", "show", "list", "get"]):
        state["action"] = "read_emails"
        # Extract max results if specified
        state["action_input"] = {"max_results": 10}

    elif "send" in last_message:
        state["action"] = "send_email"
        # You'd parse the to, subject, body from the message
        state["action_input"] = {}

    elif "search" in last_message or "find" in last_message:
        state["action"] = "search_emails"
        state["action_input"] = {}

    else:
        state["action"] = "unknown"
        state["action_input"] = {}

    return state


def execute_action(state: GmailAgentState) -> GmailAgentState:
    """Execute the Gmail action"""
    agent = GmailAgent()

    try:
        if state["action"] == "read_emails":
            max_results = state["action_input"].get("max_results", 10)
            state["result"] = agent.read_emails(max_results=max_results)

        elif state["action"] == "send_email":
            to = state["action_input"].get("to")
            subject = state["action_input"].get("subject")
            body = state["action_input"].get("body")
            state["result"] = agent.send_email(to, subject, body)

        elif state["action"] == "search_emails":
            query = state["action_input"].get("query", "")
            state["result"] = agent.search_emails(query=query)

        else:
            state["result"] = "I don't understand that action. I can read, send, or search emails."

        state["error"] = None

    except Exception as e:
        state["error"] = str(e)
        state["result"] = f"Error executing action: {str(e)}"

    return state


def format_response(state: GmailAgentState) -> GmailAgentState:
    """Format the response message"""
    if state["error"]:
        response = AIMessage(content=f"Error: {state['error']}")
    else:
        response = AIMessage(content=state["result"])

    state["messages"].append(response)
    return state


# Build the graph
def create_gmail_agent_graph():
    """Create the LangGraph workflow for Gmail agent"""
    workflow = StateGraph(GmailAgentState)

    # Add nodes
    workflow.add_node("parse_action", parse_action)
    workflow.add_node("execute_action", execute_action)
    workflow.add_node("format_response", format_response)

    # Add edges
    workflow.set_entry_point("parse_action")
    workflow.add_edge("parse_action", "execute_action")
    workflow.add_edge("execute_action", "format_response")
    workflow.add_edge("format_response", END)

    return workflow.compile()


# Create a tool-callable interface for orchestrator
def gmail_agent_tool(query: str) -> str:
    """
    Gmail agent tool that can be called by orchestrator agent.

    Args:
        query: Natural language query about Gmail operations

    Returns:
        Result of the Gmail operation
    """
    graph = create_gmail_agent_graph()

    initial_state = {
        "messages": [HumanMessage(content=query)],
        "action": "",
        "action_input": {},
        "result": "",
        "error": None
    }

    final_state = graph.invoke(initial_state)

    # Return the last AI message content
    return final_state["messages"][-1].content


# Example usage
if __name__ == "__main__":
    # Test the agent
    result = gmail_agent_tool("Read my last 5 emails")
    print(result)