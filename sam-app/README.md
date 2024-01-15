# sam-app

This folder contains the AWS [SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) application templates and source code. It is recommended to get yourself familiar with SAM before you start.

## Deployment

### Prerequisites

- Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
- [Configure AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html#cli-configure-files-methods) with your AWS account credentials.
- Install [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html).
- Have docker installed and running. We will use docker to build the Lambda functions.

### Bedrock / LangChainBedrock

Make sure you have the access to the Amazon Bedrock foundation models. You can request the access in the AWS console. Documentation can be found [here](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html).

By default these 2 Lambda functions will use Anthropic Claude v2.1 model (`anthropic.claude-v2:1`).

### LangChainSageMaker

This application **_doesn't_** include the deployment of the SageMaker endpoint. You have to have an existing SageMaker endpoint deployed in your AWS account.

Once the SageMaker endpoint is ready, you can set the `EndpointName` environment variable for the Lambda function to use it.

> [!WARNING]
> Not every model on SageMaker support response streaming. If a model doesn't support response streaming, the Lambda function may stuck. You can test the [SageMaker endpoint with LangChain](https://python.langchain.com/docs/integrations/llms/sagemaker) locally to see if it works before you deploy it.

### LangChainOpenAI

Make sure you have an OpenAI API key, or an OpenAI compatible HTTP endpoint.

Once you are ready, modify the [langchain/openai](./langchain/openai/app.py) Lambda function to apply it.

### Deploy

```bash
# Build the Lambda functions, layers, etc.
sam build

# Deploy the whole application
sam deploy --guided
```
