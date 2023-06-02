

 In this post, we show how to deploy image and text generative AI models from JumpStart using the [AWS Cloud Development Kit](https://aws.amazon.com/cdk/) (AWS CDK). The AWS CDK is an open-source software development framework to define your cloud application resources using familiar programming languages like Python.

 

We use the Stable Diffusion model for image generation and the FLAN-T5-XL model for [natural language understanding (NLU)](https://en.wikipedia.org/wiki/Natural-language_understanding) and text generation from [Hugging Face](https://huggingface.co/) in JumpStart.



## Solution overview

The web application is built on [Streamlit](https://streamlit.io/), an open-source Python library that makes it easy to create and share beautiful, custom web apps for ML and data science. We host the web application using [Amazon Elastic Container Service](https://aws.amazon.com/ecs) (Amazon ECS) with [AWS Fargate](https://docs.aws.amazon.com/AmazonECS/latest/userguide/what-is-fargate.html) and it is accessed via an Application Load Balancer. Fargate is a technology that you can use with Amazon ECS to run [containers](https://aws.amazon.com/what-are-containers) without having to manage servers or clusters or virtual machines. The generative AI model endpoints are launched from JumpStart images in [Amazon Elastic Container Registry](https://aws.amazon.com/ecr/) (Amazon ECR). Model data is stored on [Amazon Simple Storage Service](https://aws.amazon.com/s3/) (Amazon S3) in the JumpStart account. The web application interacts with the models via [Amazon API Gateway](https://aws.amazon.com/api-gateway) and [AWS Lambda](http://aws.amazon.com/lambda) functions as shown in the following diagram.

![architecture](./images/architecture.png)

API Gateway provides the web application and other clients a standard RESTful interface, while shielding the Lambda functions that interface with the model. This simplifies the client application code that consumes the models. The API Gateway endpoints are publicly accessible in this example, allowing for the possibility to extend this architecture to implement different [API access controls](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-control-access-to-api.html) and integrate with other applications.


## Prerequisites

You must have the following prerequisites:

- An [AWS account](https://signin.aws.amazon.com/signin)
- The [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- Python 3.6 or later
- node.js 14.x or later
- The [AWS CDK v2](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)
- Docker v20.10 or later

 You can deploy the infrastructure in this tutorial from your local computer or you can use [AWS Cloud9](https://aws.amazon.com/cloud9/) as your deployment workstation. AWS Cloud9 comes pre-loaded with AWS CLI, AWS CDK and Docker. If you opt for AWS Cloud9, [create the environment](https://docs.aws.amazon.com/cloud9/latest/user-guide/tutorial-create-environment.html) from the [AWS console](https://console.aws.amazon.com/cloud9).

The estimated cost to complete this post is $50, assuming you leave the resources running for 8 hours. Make sure you delete the resources you create in this post to avoid ongoing charges.



## Install the AWS CLI and AWS CDK on your local machine

If you don’t already have the AWS CLI on your local machine, refer to [Installing or updating the latest version of the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and [Configuring the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

Install the AWS CDK Toolkit globally using the following node package manager command:

```
npm install -g aws-cdk-lib@latest
```

Run the following command to verify the correct installation and print the version number of the AWS CDK:

```
cdk --version
```

Make sure you have Docker installed on your local machine. Issue the following command to verify the version:

```
docker --version
```



## Clone and set up the AWS CDK application

On your local machine, clone the AWS CDK application with the following command:

```
git clone https://github.com/aws-samples/generative-ai-sagemaker-cdk-demo.git
```

Navigate to the project folder:

```
cd generative-ai-sagemaker-cdk-demo
```


The `stacks` folder contains the code for each stack in the AWS CDK application. The `demo` folder contains the code for the Amazon Lambda functions. The repository also contains the web application located  under the folder `web-app`. 

The `cdk.json` file tells the AWS CDK Toolkit how to run your application.

This application was tested in the `us-east-1` Region but it should work in any Region that has the required services and inference instance type `ml.g4dn.4xlarge` specified in [app.py](app.py). 



#### Setup a virtual environment

This project is set up like a standard Python project. Create a Python virtual environment using the following code:

```
python3 -m venv .venv
```

Use the following command to activate the virtual environment:

```
source .venv/bin/activate
```

If you’re on a Windows platform, activate the virtual environment as follows:

```
.venv\Scripts\activate.bat
```

After the virtual environment is activated, upgrade pip to the latest version:

```
python3 -m pip install --upgrade pip
```

Install the required dependencies:

```
pip install -r requirements.txt
```

Before you deploy any AWS CDK application, you need to bootstrap a space in your account and the Region you’re deploying into. To bootstrap in your default Region, issue the following command:

```
cdk bootstrap
```

If you want to deploy into a specific account and Region, issue the following command:

```
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
```

For more information about this setup, visit  [Getting started with the AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html).


## Deploy the AWS CDK application

The AWS CDK application will be deployed to the default Region based on your workstation configuration. If you want to force the deployment in a specific Region, set your `AWS_DEFAULT_REGION` environment variable accordingly.



At this point, you can deploy the AWS CDK application. First you launch the VPC network stack:

```
cdk deploy GenerativeAiVpcNetworkStack
```

If you are prompted, enter `y` to proceed with the deployment. You should see a list of AWS resources that are being provisioned in the stack. This step takes around 3 minutes to complete.


Then you  launch the web application stack:

```
cdk deploy GenerativeAiDemoWebStack
```

After analyzing the stack, the AWS CDK will display the resource list in the stack. Enter y to proceed with the deployment. This step takes around 5 minutes.

![04](./images/cdk-deploy.png)

Note down the `WebApplicationServiceURL` from the output as you will use it later. You can also retrieve it later in the CloudFormation console, under the `GenerativeAiDemoWebStack` stack outputs.



Now, launch the image generation AI model endpoint stack:

```
cdk deploy GenerativeAiTxt2imgSagemakerStack
```

This step takes around 8 minutes. The image generation model endpoint is deployed, we can now use it.



## Use the image generation AI model

The first example demonstrates how to utilize Stable Diffusion, a powerful generative modeling technique that enables the creation of high-quality images from text prompts.

1. Access the web application using the `WebApplicationServiceURL` from the output of the `GenerativeAiDemoWebStack` in your browser.

![streamlit-01](./images/streamlit-landing-page.png)

2. In the navigation pane, choose **Image Generation**.

3. The **SageMaker Endpoint Name** and **API GW Url** fields will be pre-populated, but you can change the prompt for the image description if you’d like. 
4. Choose **Generate image**.

![streamlit-03](./images/streamlit-image-gen-01.png)

The application will make a call to the SageMaker endpoint. It takes a few seconds. A picture with the charasteristics in your image description will be displayed.

![streamlit-04](./images/streamlit-image-gen-02.png)


## View the deployed resources on the console

On the AWS CloudFormation console, choose **Stacks** in the navigation pane to view the stacks deployed.

![console-cloudformation](./images/console-cloudformation.png)



On the Amazon ECS console, you can see the clusters on the **Clusters** page.

![console-ec2](./images/console-ecs.png)



On the AWS Lambda console, you can see the functions on the **Functions** page.

![console-lambda](./images/console-lambda.png)



On the API Gateway console, you can see the API Gateway endpoints on the **APIs** page.

![console-apigw](./images/console-apigw.png)



On the SageMaker console, you can see the deployed model endpoints on the **Endpoints** page.

![console-sagemaker](./images/console-sagemaker.png)



When the stacks are launched, some parameters are generated. These are stored in the [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html). To view them, choose **Parameter Store** in the navigation pane on the [AWS Systems Manager](https://aws.amazon.com/systems-manager/) console.

![console-ssm-parameter-store](./images/console-ssm-parameter-store.png)



## Clean up

To avoid unnecessary cost, clean up all the infrastructure created with the following command on your workstation:

```
cdk destroy --all
```