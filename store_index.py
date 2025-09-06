from src.helper import download_huggingface_model, load_pdf_file, text_split
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os


load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY


extracted_data=load_pdf_file(data='Data/')
text_chunks=text_split(extracted_data)
embeddings=download_huggingface_model()



# pinecone initialization
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = 'medicalbot'

# Create index 
pc.create_index(
    name=index_name,
    dimension=384,
    metric='cosine',
    spec=ServerlessSpec(cloud='aws', region='us-east-1')
)


#storing the vector embedding
#embedding the teach chunks and upsetting it in the pinecone index
from langchain_pinecone import PineconeVectorStore
 
docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,
    index_name = index_name,
    embedding=embeddings,
    ) 


