from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class EmailState(TypedDict):
    subject: str
    sender: str
    snippet: str
    is_relevant: bool
    confidence_reason: str


KEYWORDS = {'lead', 'pricing', 'quote', 'demo', 'partnership', 'proposal', 'buy'}
SPAM_HINTS = {'lottery', 'bitcoin', 'winner', 'prince', 'casino'}


def classify_email(state: EmailState) -> EmailState:
    text = f"{state['subject']} {state['snippet']}".lower()
    if any(token in text for token in SPAM_HINTS):
        state['is_relevant'] = False
        state['confidence_reason'] = 'Spam-like keywords detected.'
        return state

    if any(token in text for token in KEYWORDS):
        state['is_relevant'] = True
        state['confidence_reason'] = 'Lead-oriented keywords found.'
    else:
        state['is_relevant'] = False
        state['confidence_reason'] = 'No lead signal found.'
    return state


def build_agent():
    graph = StateGraph(EmailState)
    graph.add_node('classify_email', classify_email)
    graph.add_edge(START, 'classify_email')
    graph.add_edge('classify_email', END)
    return graph.compile()


email_agent = build_agent()
