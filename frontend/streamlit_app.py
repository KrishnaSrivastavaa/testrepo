import requests
import streamlit as st

API_BASE = st.sidebar.text_input('FastAPI URL', 'http://localhost:8000')

st.title('Lead Mail Agent Dashboard')
st.caption('Login, connect Gmail, trigger LangGraph classification, and reply via AI draft.')

if 'token' not in st.session_state:
    st.session_state.token = ''

with st.expander('1) Authentication', expanded=True):
    auth_mode = st.radio('Choose', ['Login', 'Register'], horizontal=True)
    email = st.text_input('Email')
    password = st.text_input('Password', type='password')

    if st.button('Submit Auth'):
        endpoint = '/auth/login' if auth_mode == 'Login' else '/auth/register'
        resp = requests.post(f'{API_BASE}{endpoint}', json={'email': email, 'password': password}, timeout=30)
        if resp.ok:
            st.session_state.token = resp.json()['access_token']
            st.success('Authenticated')
        else:
            st.error(resp.text)

headers = {'Authorization': f"Bearer {st.session_state.token}"} if st.session_state.token else {}

with st.expander('2) Connect Gmail', expanded=True):
    if st.button('Get Gmail Connect URL'):
        resp = requests.get(f'{API_BASE}/auth/gmail/connect', headers=headers, timeout=30)
        if resp.ok:
            url = resp.json()['authorization_url']
            st.write('Open this URL and approve Gmail permissions:')
            st.code(url)
        else:
            st.error(resp.text)

with st.expander('3) Trigger Email Agent', expanded=True):
    batch_size = st.slider('Emails to fetch', min_value=1, max_value=10, value=5)
    if st.button('Run Agent'):
        resp = requests.post(f'{API_BASE}/automation/trigger?batch_size={batch_size}', headers=headers, timeout=60)
        if resp.ok:
            st.json(resp.json())
        else:
            st.error(resp.text)

with st.expander('4) WhatsApp-approved Reply', expanded=True):
    to_email = st.text_input('Reply To')
    context = st.text_area('Original Email Context')
    intent = st.text_input('Intent for reply', 'Professional follow-up with meeting request')

    if st.button('Generate + Send Reply'):
        resp = requests.post(
            f'{API_BASE}/automation/reply',
            headers=headers,
            params={'to_email': to_email, 'original_context': context, 'intent': intent},
            timeout=60,
        )
        if resp.ok:
            st.success('Reply sent through Gmail API')
        else:
            st.error(resp.text)
