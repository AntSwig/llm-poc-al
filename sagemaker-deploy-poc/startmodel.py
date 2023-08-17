#!/usr/bin/env python3
import json
import os

import boto3
import gradio as gr
import sagemaker
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri

os.environ["SAGEMAKER_CONTAINER_LOG_LEVEL"] = "DEBUG"

sess = sagemaker.Session()
# sagemaker session bucket -> used for uploading data, models and logs
# sagemaker will automatically create this bucket if it not exists
sagemaker_session_bucket = None
if sagemaker_session_bucket is None and sess is not None:
    # set to default bucket if a bucket name is not given
    sagemaker_session_bucket = sess.default_bucket()

try:
    role = sagemaker.get_execution_role()
except ValueError:
    iam = boto3.client("iam")
    role = iam.get_role(RoleName="sagemaker_execution_role")["Role"]["Arn"]

sess = sagemaker.Session(default_bucket=sagemaker_session_bucket)

print(f"sagemaker role arn: {role}")
print(f"sagemaker session region: {sess.boto_region_name}")

# retrieve the llm image uri
llm_image = get_huggingface_llm_image_uri("huggingface", version="0.8.2")

# print ecr image uri
print(f"llm image uri: {llm_image}")

# sagemaker config
instance_type = "ml.g5.12xlarge"
number_of_gpu = 4
health_check_timeout = 600

# Define Model and Endpoint configuration parameter
config = {
    "HF_MODEL_ID": "OpenAssistant/pythia-12b-sft-v8-7k-steps",  # model_id from hf.co/models
    "SM_NUM_GPUS": json.dumps(number_of_gpu),  # Number of GPU used per replica
    "MAX_INPUT_LENGTH": json.dumps(1024),  # Max length of input text
    "MAX_TOTAL_TOKENS": json.dumps(
        2048
    ),  # Max length of the generation (including input text)
    # "HF_MODEL_QUANTIZE": "bitsandbytes",  # comment in to quantize
}

# create HuggingFaceModel with the image uri
llm_model = HuggingFaceModel(role=role, image_uri=llm_image, env=config)

# Deploy model to an endpoint
# https://sagemaker.readthedocs.io/en/stable/api/inference/model.html#sagemaker.model.Model.deploy
llm = llm_model.deploy(
    initial_instance_count=1,
    instance_type=instance_type,
    # volume_size=400,  # If using an instance with local SSD storage, volume_size must be None, e.g. p4 but not p3
    container_startup_health_check_timeout=health_check_timeout,  # 10 minutes to be able to load the model
)

# Create the UI

# hyperparameters for llm
parameters = {
    "do_sample": True,
    "top_p": 0.7,
    "temperature": 0.7,
    "top_k": 50,
    "max_new_tokens": 256,
    "repetition_penalty": 1.03,
    "stop": ["<|endoftext|>"],
}

with gr.Blocks() as demo:
    gr.Markdown("## Chat with Amazon SageMaker")
    with gr.Column():
        chatbot = gr.Chatbot()
        with gr.Row():
            with gr.Column():
                message = gr.Textbox(
                    label="Chat Message Box",
                    placeholder="Chat Message Box",
                    show_label=False,
                )
            with gr.Column():
                with gr.Row():
                    submit = gr.Button("Submit")
                    clear = gr.Button("Clear")

    def respond(message, chat_history):
        # convert chat history to prompt
        converted_chat_history = ""
        if len(chat_history) > 0:
            for c in chat_history:
                converted_chat_history += (
                    f"<|prompter|>{c[0]}<|endoftext|><|assistant|>{c[1]}<|endoftext|>"
                )
        prompt = (
            f"{converted_chat_history}<|prompter|>{message}<|endoftext|><|assistant|>"
        )

        # send request to endpoint
        llm_response = llm.predict({"inputs": prompt, "parameters": parameters})

        # remove prompt from response
        parsed_response = llm_response[0]["generated_text"][len(prompt) :]
        chat_history.append((message, parsed_response))
        return "", chat_history

    submit.click(respond, [message, chatbot], [message, chatbot], queue=False)
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch(share=True)

llm.delete_model()
llm.delete_endpoint()
