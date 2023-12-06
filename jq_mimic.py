import json

class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self):
        return f"Document(page_content='{self.page_content}', metadata={self.metadata})"

class JSONLoader:
    def __init__(self, file_path, content_key, metadata_func):
        self.file_path = file_path
        self.content_key = content_key
        self.metadata_func = metadata_func

    def load(self):
        try:
            with open(self.file_path, 'r') as json_file:
                data = json.load(json_file)
                return self.create_documents(data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    def create_documents(self, data):
        documents = []
        for item in data:
            if not isinstance(item, dict):
                continue
            content = item.get(self.content_key, "")
            metadata = self.metadata_func(item, {})
            documents.append(Document(page_content=content, metadata=metadata))
        return documents


