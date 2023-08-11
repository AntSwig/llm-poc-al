## Q&A Burpchatbot - Supercharge your knowledge base.

I used this blog post as inspiration:

https://www.paepper.com/blog/posts/build-q-and-a-bot-of-your-website-using-langchain/

### Prerequisites
- Go to "https://openai.com" , login and generate a API key.
- Set the API key as an environmental variable: `export OPENAI_API_KEY="xxxx-xxxx-xxxx-xxxx"`
- Minimum version requirement Python 3.8.3.

### Quickstart

1. Generate the faiss_store.pkl: `python ps-docs-chatbot.py ` (circa 30 mins)

2. Build the docker container: `docker build -t burpbot .`

3. Run the docker container: `docker run --rm -p 7860:7860 burpbot:latest`

4. Go here to start chatting with burpbot: `open http://127.0.0.1:7860/`

### Local development

There are __two__ scripts:

```ps-docs-chatbot.py```

```qa-gradio.py```

First load data:
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python ps-docs-chatbot.py
```

Then query data:

```sh
❯ python qa-gradio.py 
```

The Front end is provided with Gradio:

Gradio demos can easily be shared publicly by setting share=True in the launch() method. Like this:
```demo.launch(share=False)```

```demo.launch(share=True)```

 Although the link is served through a Gradio URL, it is only a proxy for your local server, and does not store any data sent through your app.


#### Steps

1. Use the website’s sitemap.xml to query all URLs
2. Download the HTML of each URL and extract the text only
3. Split each page’s content into a number of documents
4. Embed each document using OpenAI’s API
5. Create a vector store of these embeddings
6. When asking a question, query which documents are most relevant and send them as context to GPT3 to ask for a good answer
7. When answering, provide the documents which were used as the source and the answer