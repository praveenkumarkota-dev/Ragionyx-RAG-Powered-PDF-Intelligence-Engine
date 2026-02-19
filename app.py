import streamlit as st
from PyPDF2 import PdfReader
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
#from langchain_classic.chains.question_answering import load_qa_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
import os



OpenAI_API_KEY = os.getenv("OPENAI_API_KEY")
st.header("NoteBot")

with st.sidebar:
    st.title("My Notes")
    file = st.file_uploader("Upload note PDF and start asking questions", type = "pdf")

#extracting the text from pdf file
if file is not None:
    my_pdf = PdfReader(file)
    text = ""
    for page in my_pdf.pages:
        text += page.extract_text()
        #st.write(text)


    # break it into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size = 200, chunk_overlap = 50,length_function = len)
    chunks = splitter.split_text(text)
    #st.write(chunks)

    #creating object of OpenEmbeddings class that let us connect with OpenAI's Embeddings Models
    embeddings = OpenAIEmbeddings(api_key = OpenAI_API_KEY)

    #Creating VectorDB & Storing embeddings into it
    vector_store = FAISS.from_texts(chunks, embeddings)

    #get user query
    user_query = st.text_input("Type your query here")

    #semantic search from vector store
    if user_query:
        matching_chunks = vector_store.similarity_search(user_query)

        #define our LLM
        llm = ChatOpenAI(
            api_key = OpenAI_API_KEY,
            max_tokens=200,
            temperature=0,
            model = "gpt-3.5-turbo"
        )

        #Generate response
        #chain = load_qa_chain(llm, user_type = "stuff")
        #output = chain.run(question = user_query, input_documents = matching_chunks)
        #st.write(output)

        customized_prompt = ChatPromptTemplate.from_template(
            """  You are my assistant tutor. Answer the question strictly based on the following context.
            If the answer is not in the context, say "I don't know praveen":
            Context:
            {context}
            Question: {input}
            """
        )

        chain = create_stuff_documents_chain(llm, customized_prompt)
        output = chain.invoke({"input": user_query, "input_documents": matching_chunks})
        st.write(output)





