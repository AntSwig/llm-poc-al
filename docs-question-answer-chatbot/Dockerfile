FROM python:slim-bookworm

RUN pip install --upgrade pip

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY faiss_store.pkl /
COPY qa-gradio.py /

WORKDIR /

ENTRYPOINT [ "python", "qa-gradio.py" ]

EXPOSE 7860