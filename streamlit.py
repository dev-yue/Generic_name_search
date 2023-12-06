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
_ = load_dotenv(find_dotenv())  # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

# Load and prepare data (Consider doing this outside the main function to load only once)
file_path = './results/formatted_generic_name_count.json'
data = json.loads(Path(file_path).read_text())

def metadata_func(record, metadata):
    metadata["count"] = str(record.get("count"))
    return metadata

loader = JSONLoader(
    file_path=file_path,
    content_key="term",
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
    st.title('Generic Name Search')

    # User query input
    query = st.text_input('Enter your keyword:', '')
    num_results = st.number_input('Number of results', min_value=1, max_value=100, value=10)  # Number input for results

    if query:
        # Perform similarity search with specified number of results
        retrieved_docs = vectordb.similarity_search(query, k=num_results)

        # Process and display results
        documents = re.findall(r"Document\(page_content='(.*?)', metadata=\{(.*?)\}\)", str(retrieved_docs))

        seen_issues = set()  # Set to keep track of seen issues
        count = 0  # Count to track displayed results

        for idx, doc in enumerate(documents, start=1):
            if count >= num_results:
                break  # Break loop if desired number of results is reached

            content, metadata = doc

            # Skip if this issue has already been seen
            if content in seen_issues:
                continue
            seen_issues.add(content)

            metadata_dict = ast.literal_eval("{" + metadata + "}")
            count_str = metadata_dict.get('count', 'N/A')

            # Display each unique issue with its count
            st.markdown(f"**Name {idx}:** {content}")
            st.markdown(f"**Count:** {count_str}")

            count += 1

if __name__ == '__main__':
    main()
