#### Detailed Steps:

Query your websites URL's using the sitemap.xml, in our case https://portswigger.net/sitemap.xml.
Now we have a pages array with the text and source URL per entry. There are approx 6487 row(s) of data for the website.
We use BeautifulSoup to extract the text from each url, removing trailing white space and dropping empty lines.
Split each page's content into a number of documents , then make sure documents aren't too long (due to llm context limits). We use text splitters to do this.
With all these neatly split documents and their source URLs, we can start the embedding process.
This is calling the OpenAI API to get text embeddings for your documents.
Each embedding is of size 1536, so that means that each document is represented by a vector of 1536 numbers.
The portswigger.net website has a lot more than 100k tokens, so the API cost to embed them was around $1.25.
Once the call completes we will have stored the resulting embeddings in a FAISS store as 'faiss_store.pkl'.
All of the above steps happen in the ```ps-docs-chatbot.py```

#### Prompt Analytics

I'm trialing https://promptlayer.com/ to surface some analytics around our prompt and api usage. 
[Avg latency; Total cost; Requests & tokens; total prompts; Models; All time cost by prompt template]
https://docs.promptlayer.com/why-promptlayer/how-it-works

PromptLayer is a devtool that allows you to track, manage, and share your GPT prompt engineering. It acts as a middleware between your code and OpenAI’s python library, recording all your API requests and saving relevant metadata for easy exploration and search in the PromptLayer dashboard.

​
How it Works
PromptLayer works by wrapping your OpenAI API requests and logging data about them after they are sent. This is all done from your machine, your API key is never sent. This means that it does not interfere with the functionality of your existing codebase or require any changes to your application’s architecture. All you need to do is add PromptLayer as an add-on to your existing LLM application and start making requests as usual.
#### Note: 

It can take a hot minute for the call to embedd our data to complete, circa 30 minutes, you might also see a RateLimitError. 

However I've found if you can see that last url in the sitemap.xml being processed it usually means you can query the vector store, even if openai's cloudflare cdn rate limits you and ends the call.

```Split https://portswigger.net/web-security/xxe/lab-xxe-via-file-upload into 4 chunks
Split https://portswigger.net/web-security/xxe/xml-entities into 5 chunks
Split https://portswigger.net/yandex_d2b892300e5f5498.html into 1 chunks
Retrying langchain.embeddings.openai.embed_with_retry.<locals>._embed_with_retry in 4.0 seconds as it raised RateLimitError: Rate limit reached for default-text-embedding-ada-002 in organization org-j7iaKKJ8Mr5prdMjCFTlPUyN on tokens per min. Limit: 1000000 / min. Current: 716823 / min. Contact us through our help center at help.openai.com if you continue to have issues..
```
#### ToDo: implement better api-request
Here is some further information on rate limits and an example for how to send request without being shutdown:
https://platform.openai.com/docs/guides/rate-limits/overview

https://github.com/openai/openai-cookbook/blob/main/examples/api_request_parallel_processor.py

Now for some fun, lets ask some questions.
It will answer your question and provide sources with links.
The second python script does the question asking and prompt queries. 
#### ToDo: explain prompt templates and options, add link to relevant docs
```python
python qa-gradio-cml-output.py "What is a sql injection?"
```

You can go to http://127.0.0.1:7860 to interact with the gradio ui.
Or you can rerun the script and ask questions in your terminal.

Expect output like:
```❯ python qa-gradio-cml-output.py "what is a sql injection"
Answer: SQL injection is a web security vulnerability that allows an attacker to interfere with the queries that an application makes to its database. It occurs when user-controllable data is incorporated into database SQL queries in an unsafe manner. By supplying crafted input, an attacker can break out of the data context and manipulate the structure of the query. This can lead to a wide range of damaging attacks, such as unauthorized access to sensitive data, modifying application data, escalating privileges, and taking control of the database server.

Sources:
1. https://portswigger.net/web-security/sql-injection
2. https://portswigger.net/kb/issues/00100200_sql-injection
Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://fa97da666968b66575.gradio.live

This share link expires in 72 hours.
```

Gotchas:

When pushing and pulling to the GitHub repo - bare in mind the file faiss_store.pkl is 219.48 MB; which exceeds GitHub's file size limit of 100.00 MB.

You might want to use Git Large File Storage - https://git-lfs.github.com and enable it in your GitHub settings in the archives section.


Further reading:

https://docs.management-prod.cloud.portswigger.com/learning/#introduction-to-langchain-beginner-guide-to-seven-essential-concepts
https://www.paepper.com/blog/posts/build-q-and-a-bot-of-your-website-using-langchain/
https://python.langchain.com/docs/get_started/introduction.html
https://www.gradio.app/guides/sharing-your-app
https://www.pinecone.io/learn/vector-database/