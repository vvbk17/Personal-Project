import streamlit as st
import json
import boto3

import boto3.session

# Load tenant config
with open("tenant_config.json") as f:
    TENANT_CONFIGS = json.load(f)

# Get tenant from URL query param
query_params = st.query_params
tenant_id = query_params.get("tenant", "companyA")
tenant = TENANT_CONFIGS.get(tenant_id, TENANT_CONFIGS["companyA"])

# Claude model config

aws_profile = "dev_account"  # your SSO profile name
aws_region = "us-east-1"     # your Bedrock region

session = boto3.session.Session(profile_name=aws_profile, region_name=aws_region)
bedrock = session.client("bedrock-runtime")
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

# Claude message formatter
def query_claude(messages, system_prompt):
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.7,
        "system": system_prompt,
        "messages": messages
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(payload),
        contentType="application/json"
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"] if "content" in result else result["completion"]

# Streamlit page setup
st.set_page_config(page_title=tenant["title"])
st.title(tenant["title"])
st.markdown(f"**Instructions:** {tenant['instructions']}")

# Chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input box
user_input = st.text_input("Ask something:")

# When user submits a message
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    response_text = query_claude(
        messages=st.session_state.chat_history,
        system_prompt=tenant["instructions"]
    )

    st.session_state.chat_history.append({"role": "assistant", "content": response_text})

# Display chat history
for msg in st.session_state.chat_history:
    role = "You" if msg["role"] == "user" else "Bot"
    st.markdown(f"**{role}:** {msg['content']}")
