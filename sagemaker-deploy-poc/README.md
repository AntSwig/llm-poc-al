### LLM-POC

Manual steps for testing in the aws playground account (658786808637)

We are following this guide here:

https://huggingface.co/blog/sagemaker-huggingface-llm#1-setup-development-environment

1 - In IAM create a role called "sagemaker_execution_role"

https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html


2 - In service quotas > Amazon SageMaker increase "ml.g5.12xlarge for endpoint usage" to 1


3 - You can run this model with different instances but they do need to be able to support the workload, e.g. have 4 CPUs like "ml.c6i.xlarge". There is an inference recommender job in the aws sagemaker console that will recommend instance types that are suitable. Go check in service quotas if the are available for endpoint usage.

https://repost.aws/knowledge-center/sagemaker-endpoint-creation-fail

For debugging set loglevel like so:
`export SAGEMAKER_CONTAINER_LOG_LEVEL=DEBUG`

Run the model:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python startmodel.py
```