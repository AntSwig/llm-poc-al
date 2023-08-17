import os

from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain.vectorstores import FAISS

llm = OpenAI(
    model_name="text-davinci-003",
)

example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="Example Input: {input}\nExample Output: {output}",
)

# Examples of locations that nouns are found
examples = [
    {"input": "burpsuite enterprise, unlimited scans", "output": "£44,999 per year"},
    {
        "input": "burpsuite enterprise, 20 concurrent scans",
        "output": "£14,480 per year",
    },
    {
        "input": "burpsuite enterprise, pay as you scan",
        "output": "£1,999 per year plus £9 per hour scanned",
    },
    {"input": "burpsuite pro", "output": "£399 per year, one user"},
    {"input": "burpsuite community", "output": "free"},
]
# SemanticSimilarityExampleSelector will select examples that are similar to your input by semantic meaning

example_selector = SemanticSimilarityExampleSelector.from_examples(
    # This is the list of examples available to select from.
    examples,
    # This is the embedding class used to produce embeddings which are used to measure semantic similarity.
    OpenAIEmbeddings(),
    # This is the VectorStore class that is used to store the embeddings and do a similarity search over.
    FAISS,
    # This is the number of examples to produce.
    k=3,
)

similar_prompt = FewShotPromptTemplate(
    # The object that will help select examples
    example_selector=example_selector,
    # Your prompt
    example_prompt=example_prompt,
    # Customizations that will be added to the top and bottom of your prompt
    prefix="Give the price an item usually costs per year",
    suffix="Input: {noun}\nOutput:",
    # What inputs your prompt will receive
    input_variables=["noun"],
)
# Select a noun!
my_noun = "enterprise"

print(similar_prompt.format(noun=my_noun))
