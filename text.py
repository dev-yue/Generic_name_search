# Import necessary libraries
import streamlit as st
import json
from pathlib import Path
import ast
import re
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from jq_mimic import JSONLoader
from langchain.embeddings.openai import OpenAIEmbeddings

import os
import openai

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

# Load and prepare data (Consider doing this outside the main function to load only once)
file_path = 'transformed_data.json'
data = json.loads(Path(file_path).read_text())

def metadata_func(record, metadata):
    metadata["case_number"] = str(record.get("case_number"))
    metadata["main_cat"] = record.get("main_cat")
    metadata["sub_cat"] = record.get("sub_cat")
    return metadata

loader = JSONLoader(
    file_path=file_path,
    jq_schema='issues[]',
    content_key="content",
    metadata_func=metadata_func
)

docs = loader.load()
embedding = OpenAIEmbeddings()
persist_directory = 'vector_db'

vectordb = Chroma.from_documents(
documents=docs,
embedding=embedding,
persist_directory=persist_directory
)

# vectordb.persist()

# Streamlit app
def main():
    st.title('Problem Matcher')

    # User query input
    query = st.text_input('Enter your problem query:', '')

    if query:
        # Perform similarity search
        retrieved_docs = vectordb.similarity_search(query)

        # Process and display results
        documents = re.findall(r"Document\(page_content='(.*?)', metadata=\{(.*?)\}\)", str(retrieved_docs))

        seen_issues = set()  # Set to keep track of seen issues

        for idx, doc in enumerate(documents, start=1):
            content, metadata = doc

            # Skip if this issue has already been seen
            if content in seen_issues:
                continue
            seen_issues.add(content)

            metadata_dict = ast.literal_eval("{" + metadata + "}")
            case_numbers = ast.literal_eval(metadata_dict['case_number'])

            # Create hyperlinks
            links = [f"<a href='https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfMAUDE/detail.cfm?mdrfoi__id={num}' target='_blank'>{num}</a>" for num in case_numbers]
            links_str = ", ".join(links)

            # Display each unique issue with its case numbers
            st.markdown(f"**Issue {idx}:** {content}")
            st.markdown(f"**Case Numbers:** {links_str}", unsafe_allow_html=True)

if __name__ == '__main__':
    main()