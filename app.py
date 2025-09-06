from flask import Flask, render_template, jsonify, request
from src.helper import download_huggingface_model
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
import os

load_dotenv()

app=Flask(__name__)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

embeddings=download_huggingface_model()



index_name = 'medicalbot'


# embedding each chunks and upsetting it in the pinecone index
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings)


# Create retriever from the vector store
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1
    )

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}")
    ]
)



question_answering_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answering_chain)

    
@app.route("/")
def index():
    return render_template("chatbot.html")

@app.route("/get", methods=["POST"])  
def chat():
    try:
        data = request.get_json()
        msg = data.get("message", "")
        
        if not msg:
            return jsonify({"error": "No message provided"}), 400
            
        print(f"User input: {msg}")
        
        # Get response from RAG chain
        response = rag_chain.invoke({"input": msg})
        bot_response = response["answer"]
        
        print(f"Bot response: {bot_response}")
        
        return jsonify({"response": bot_response})
        
    except Exception as e:
        print(f"Error in chat route: {e}")
        return jsonify({"response": "Sorry, I encountered an error. Please try again."}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
