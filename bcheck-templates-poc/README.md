## BCheckTemplateGPT - Supercharge your bchecks.

I used this blog post as inspiration:

https://mp-weixin-qq-com.translate.goog/s/j7EHftzPdTf84lBzxpLb_Q?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp

### Prerequisites
- Go to "https://openai.com" , login and generate a API key.
- Set the API key as an environmental variable: `export OPENAI_API_KEY="xxxx-xxxx-xxxx-xxxx"`
- To enable prompt analytics set the promptlayer API key as an environment variable: `export PROMPTLAYER_API_KEY="pl_xx-xxxx-xxxx-xxxx"`
- Minimum version requirement Python 3.8.3.

### Local development

This script is still [WIP] it will load data from a GitHub Repo that you can then query locally. 
It also uses MultiQueryRetriever to generate example prompt questions from the base question you ask it. 

First load data:
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bcheck.py
```

Then query the data:
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python qa-bcheck.py
```

Expect output like:

```python
❯ python bcheck.py
INFO:langchain.retrievers.multi_query:Generated queries: ['1. Can you provide information about the concept of bcheck?', '2. Could you explain what bcheck means?', "3. I'm curious to know the definition of bcheck. Can you help me understand it better?"]
metadata:
    language: v1-beta
    name: "Request-level collaborator based"
    description: "Blind SSRF with out-of-band detection"
    author: "Carlos Montoya"

given request then
    send request:
        headers:
            "Referer": {generate_collaborator_address()}

    if http interactions then
        report issue:
            severity: high
            confidence: firm
            detail: "This site fetches arbitrary URLs specified in the Referer header."
            remediation: "Ensure that the site does not directly request URLs from the Referer header."
    end if```