import os
import streamlit as st
from phi.agent import Agent, AgentKnowledge
from phi.vectordb.pgvector import PgVector
from phi.embedder.ollama import OllamaEmbedder
from phi.model.ollama import Ollama
from phi.knowledge.pdf import PDFKnowledgeBase
from phi.knowledge.text import TextKnowledgeBase
import boto3
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from atlassian import Confluence
import io

import streamlit as st
# Display the logo
st.image("/logo.png", width=400)  # Adjust the width as needed


st.title("RAGForge")
st.subheader("RAG Application with Ollama Embedding and Agent")

# Sidebar for Knowledge Base Settings
st.sidebar.title("Knowledge Base Settings")

# Database Settings
st.sidebar.subheader("Database Settings")
db_url_input = st.sidebar.text_input("Database URL", value='postgresql://ai:ai@localhost:5532/ai')
embeddings_table_input = st.sidebar.text_input("Embeddings Table Name", value='embeddings')
reload_knowledge_base = st.sidebar.button("Reload Knowledge Base")

# Update the database connection
db_url = db_url_input
embeddings_table = embeddings_table_input

# Create knowledge base with updated settings
def create_knowledge_base():
    vector_db = PgVector(
        db_url=db_url,
        table_name=embeddings_table,
        embedder=OllamaEmbedder(),
    )
    knowledge_base = AgentKnowledge(
        vector_db=vector_db,
        num_documents=5,
        include_sources=True,
    )
    return knowledge_base

# Initialize knowledge base
if 'knowledge_base' not in st.session_state or reload_knowledge_base:
    st.session_state['knowledge_base'] = create_knowledge_base()
    st.session_state['selected_files'] = []

knowledge_base = st.session_state['knowledge_base']

# Section to select local files using file browser
st.sidebar.subheader("Local Files")
if 'selected_files' not in st.session_state:
    st.session_state['selected_files'] = []

# Function to browse and select files
def file_browser(base_path):
    files = []
    for root, dirs, filenames in os.walk(base_path):
        for filename in filenames:
            if filename.lower().endswith(('.pdf', '.txt', '.md')):
                files.append(os.path.join(root, filename))
    return files

base_path = '/app/application_materials/knowledge_files'
if os.path.exists(base_path):
    all_files = file_browser(base_path)
    selected_files = st.sidebar.multiselect('Select files to load', all_files)
    if st.sidebar.button("Load Selected Files"):
        for file in selected_files:
            if file.lower().endswith('.pdf'):
                kb = PDFKnowledgeBase(
                    path=file,
                    vector_db=knowledge_base.vector_db
                )
            elif file.lower().endswith(('.txt', '.md')):
                kb = TextKnowledgeBase(
                    path=file,
                    vector_db=knowledge_base.vector_db
                )
            else:
                st.warning(f"Unsupported file format: {file}")
                continue
            kb.load()
        st.session_state['selected_files'].extend(selected_files)
        st.success(f"Loaded {len(selected_files)} files into the knowledge base.")
else:
    st.error(f"Base path does not exist: {base_path}")

# Add Drag and Drop File Uploader
st.sidebar.subheader("Upload Files")
uploaded_files = st.sidebar.file_uploader(
    "Drag and drop files here, or click to select files",
    type=['pdf', 'txt', 'md'],
    accept_multiple_files=True
)

if uploaded_files:
    uploaded_file_paths = []
    for uploaded_file in uploaded_files:
        # Save uploaded files to the knowledge_files directory
        save_path = os.path.join(base_path, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        uploaded_file_paths.append(save_path)
    
    # Load uploaded files into the knowledge base
    for file in uploaded_file_paths:
        if file.lower().endswith('.pdf'):
            kb = PDFKnowledgeBase(
                path=file,
                vector_db=knowledge_base.vector_db
            )
        elif file.lower().endswith(('.txt', '.md')):
            kb = TextKnowledgeBase(
                path=file,
                vector_db=knowledge_base.vector_db
            )
        else:
            st.warning(f"Unsupported file format: {file}")
            continue
        kb.load()
    st.success(f"Uploaded and loaded {len(uploaded_file_paths)} files into the knowledge base.")

# Section for AWS S3 connection
st.sidebar.subheader("AWS S3")
aws_access_key = st.sidebar.text_input("AWS Access Key ID")
aws_secret_key = st.sidebar.text_input("AWS Secret Access Key", type="password")
aws_bucket_name = st.sidebar.text_input("S3 Bucket Name")
load_s3_files = st.sidebar.button("Load Files from S3")

# Section for Google Drive connection
st.sidebar.subheader("Google Drive")
gdrive_credentials_json = st.sidebar.text_area("Google Drive Credentials JSON")
load_gdrive_files = st.sidebar.button("Load Files from Google Drive")

# Section for Confluence connection
st.sidebar.subheader("Confluence")
confluence_url = st.sidebar.text_input("Confluence URL")
confluence_username = st.sidebar.text_input("Confluence Username")
confluence_api_token = st.sidebar.text_input("Confluence API Token", type="password")
load_confluence_files = st.sidebar.button("Load Files from Confluence")

# Function to load files from AWS S3
def load_s3_files_to_kb(access_key, secret_key, bucket_name):
    if access_key and secret_key and bucket_name:
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )
            # List supported files in the bucket
            s3_objects = s3.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in s3_objects:
                supported_keys = [obj['Key'] for obj in s3_objects['Contents'] if obj['Key'].lower().endswith(('.pdf', '.txt', '.md'))]
                if supported_keys:
                    # Download files to a temporary directory
                    os.makedirs('/tmp/s3_files', exist_ok=True)
                    downloaded_files = []
                    for key in supported_keys:
                        local_path = f'/tmp/s3_files/{os.path.basename(key)}'
                        s3.download_file(bucket_name, key, local_path)
                        downloaded_files.append(local_path)
                    # Load files into knowledge base
                    for file in downloaded_files:
                        if file.lower().endswith('.pdf'):
                            kb = PDFKnowledgeBase(
                                path=file,
                                vector_db=knowledge_base.vector_db
                            )
                        elif file.lower().endswith(('.txt', '.md')):
                            kb = TextKnowledgeBase(
                                path=file,
                                vector_db=knowledge_base.vector_db
                            )
                        else:
                            st.warning(f"Unsupported file format: {file}")
                            continue
                        kb.load()
                    st.success(f"Loaded {len(downloaded_files)} files from S3 bucket {bucket_name}")
                else:
                    st.warning("No supported files found in the specified S3 bucket.")
            else:
                st.warning("No files found in the specified S3 bucket.")
        except Exception as e:
            st.error(f"An error occurred while accessing S3: {e}")
    else:
        st.error("Please provide AWS credentials and bucket name.")

# Function to load files from Google Drive
def load_gdrive_files_to_kb(credentials_json):
    if credentials_json:
        try:
            creds = service_account.Credentials.from_service_account_info(eval(credentials_json), scopes=['https://www.googleapis.com/auth/drive'])
            drive_service = build('drive', 'v3', credentials=creds)
            # List supported files in Drive
            query = "mimeType='application/pdf' or mimeType='text/plain' or mimeType='text/markdown'"
            results = drive_service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name)"
            ).execute()
            items = results.get('files', [])
            if items:
                # Download files to a temporary directory
                os.makedirs('/tmp/gdrive_files', exist_ok=True)
                downloaded_files = []
                for item in items:
                    file_id = item['id']
                    file_name = item['name']
                    request = drive_service.files().get_media(fileId=file_id)
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                    fh.seek(0)
                    local_path = f'/tmp/gdrive_files/{file_name}'
                    with open(local_path, 'wb') as f:
                        f.write(fh.read())
                    downloaded_files.append(local_path)
                # Load files into knowledge base
                for file in downloaded_files:
                    if file.lower().endswith('.pdf'):
                        kb = PDFKnowledgeBase(
                            path=file,
                            vector_db=knowledge_base.vector_db
                        )
                    elif file.lower().endswith(('.txt', '.md')):
                        kb = TextKnowledgeBase(
                            path=file,
                            vector_db=knowledge_base.vector_db
                        )
                    else:
                        st.warning(f"Unsupported file format: {file}")
                        continue
                    kb.load()
                st.success(f"Loaded {len(downloaded_files)} files from Google Drive")
            else:
                st.warning("No supported files found in Google Drive.")
        except Exception as e:
            st.error(f"An error occurred while accessing Google Drive: {e}")
    else:
        st.error("Please provide Google Drive credentials.")

# Function to load files from Confluence
def load_confluence_files_to_kb(url, username, api_token):
    if url and username and api_token:
        try:
            confluence = Confluence(
                url=url,
                username=username,
                password=api_token
            )
            # Get all pages
            all_pages = confluence.get_all_pages()
            downloaded_files = []
            os.makedirs('/tmp/confluence_files', exist_ok=True)
            for page in all_pages:
                attachments = confluence.get_attachments_from_content(page['id'])
                for attachment in attachments['results']:
                    if attachment['metadata']['mediaType'] in ['application/pdf', 'text/plain', 'text/markdown']:
                        file_name = attachment['title']
                        file_content = confluence.download_attachment(page['id'], file_name)
                        local_path = f'/tmp/confluence_files/{file_name}'
                        with open(local_path, 'wb') as f:
                            f.write(file_content)
                        downloaded_files.append(local_path)
            if downloaded_files:
                # Load files into knowledge base
                for file in downloaded_files:
                    if file.lower().endswith('.pdf'):
                        kb = PDFKnowledgeBase(
                            path=file,
                            vector_db=knowledge_base.vector_db
                        )
                    elif file.lower().endswith(('.txt', '.md')):
                        kb = TextKnowledgeBase(
                            path=file,
                            vector_db=knowledge_base.vector_db
                        )
                    else:
                        st.warning(f"Unsupported file format: {file}")
                        continue
                    kb.load()
                st.success(f"Loaded {len(downloaded_files)} files from Confluence")
            else:
                st.warning("No supported files found in Confluence.")
        except Exception as e:
            st.error(f"An error occurred while accessing Confluence: {e}")
    else:
        st.error("Please provide Confluence credentials.")

# Load Files from AWS S3
if load_s3_files:
    load_s3_files_to_kb(aws_access_key, aws_secret_key, aws_bucket_name)

# Load Files from Google Drive
if load_gdrive_files:
    load_gdrive_files_to_kb(gdrive_credentials_json)

# Load Files from Confluence
if load_confluence_files:
    load_confluence_files_to_kb(confluence_url, confluence_username, confluence_api_token)

# Add the knowledge base to the Agent, specify the Ollama model, and add instructions
agent = Agent(
    model=Ollama(id="llama3.2"),
    knowledge_base=knowledge_base,
    instructions=["Always include sources"],
    markdown=True,
    add_history_to_messages=True,
    num_history_responses=5,
)

# Initialize session state for chat history
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Display chat history
st.subheader("Chat History")
if st.session_state['history']:
    for chat in st.session_state['history']:
        st.markdown(f"**User:** {chat['user']}")
        st.markdown(f"**Agent:** {chat['agent']}")
else:
    st.write("No chat history yet.")

# User input
user_input = st.text_input("Ask a question:")

if user_input:
    # Use the run method and get the content
    run_response = agent.run(user_input)
    response = run_response.content
    # Store the interaction in the chat history
    st.session_state['history'].append({'user': user_input, 'agent': response})
    # Display the response
    st.markdown(f"**Agent:** {response}")
