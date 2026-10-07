import streamlit as st  
from chatbot_backend import chatbot,llm,retrive_all_threads
from langchain_core.messages import HumanMessage
import uuid

# utility functions
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []
    
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable" : {"thread_id" : thread_id}})
    return state.values.get('messages',[])

# session setup
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
    
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = retrive_all_threads()


add_thread(st.session_state['thread_id'])

# sidebar UI 
st.sidebar.title('Langgraph-chatbot')

if st.sidebar.button('New-chat'):
    reset_chat()

st.sidebar.header('My conversation')

for thread_id in st.session_state['chat_thread'][::-1]:
     
    if st.sidebar.button(thread_id):
        
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)
        
        temp_messages = []
        for message in messages:
            if isinstance(message,HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({'role':role,'content':message.content})
            
        st.session_state['message_history'] = temp_messages   
        
# Main UI
# loading convo history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')
 
if user_input:
    # printing user message 
    st.session_state['message_history'].append({'role' : 'user', 'content' :user_input})
    with st.chat_message('user'):
        st.text(user_input)
    
    CONFIG = {"configurable" : {"thread_id" : st.session_state['thread_id']}}
    
    with st.chat_message('assistant'):
            ai_message = st.write_stream(
                message_chunk.content for message_chunk,metadata in  chatbot.stream(
                    {'messages': [ HumanMessage(content = user_input)]},
                    config=  CONFIG,
                    stream_mode= 'messages'
                )
            )   
    
    st.session_state['message_history'].append({'role' : 'assistant', 'content' :ai_message})
   
   