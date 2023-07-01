from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

from kor import from_pydantic, create_extraction_chain  
from pydantic import BaseModel, Field, validator
# from langchain.llms import OpenAI

from dotenv import dotenv_values
import os

config = dotenv_values(".env")
os.environ["OPENAI_API_KEY"] = config['OPENAI_API_KEY']
persist_directory = 'db'

embedding = OpenAIEmbeddings()
vectordb2 = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding,
)

retriever = vectordb2.as_retriever(search_kwargs={"k": 2})

 
llm = ChatOpenAI(
    temperature=0,
    model_name='gpt-3.5-turbo'
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)


class SingleSelection(BaseModel):
    question: str = Field(description="The question")
    option1: str = Field(description="option 1")
    option2: str = Field(description="option 2")
    option3: str = Field(description="option 3")
    option4: str = Field(description="option 4")
    correct: str = Field(description="The correct answer to the question")


schema, validator = from_pydantic(
    SingleSelection,
    description="The question",  
    examples=[ 
        (
            "What is the capital of France? a) London b) Paris c) Rome d) Berlin Correct answer: b) Paris",
            [
                {"question": "What is the capital of France? a) London b) Paris c) Rome d) Berlin"},
                {"option1": "a) London"},
                {"option2": "b) Paris"},
                {"option3": "c) Rome"},
                {"option4": "d) Berlin"},
                {"correct": "b) Paris"}
            ]
        )
    ],
    many=True,  # <-- Note Many = True
)


chain = create_extraction_chain(llm, schema, validator=validator)


def process_llm_response(llm_response):
    return llm_response['result']


def generate_mcqs(no_of_questions: int, topic: str):
    global qa_chain, chain
    query = f"Generate {no_of_questions} multiple choice questions(4 options) about {topic} along with the correct answer."
    llm_response = qa_chain(query)
    gen_questions = process_llm_response(llm_response)
    questions_json = chain.predict_and_parse(text=gen_questions)
    return questions_json['data']['singleselection']


# usage
# questions = generate_mcqs(3, "Ramadan")
# print(questions[0], sep='\n')
