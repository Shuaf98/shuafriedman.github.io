#!/usr/bin/env python3
import aws_cdk as cdk

from stack.networking_stack import NetworkingStack
from stack.demo_stack import DemoStack
from stack.sagemaker_stack import GenerativeAiTxt2imgSagemakerStack
import os
import boto3
from config import *

import sagemaker
import boto3
from sagemaker import script_uris
from sagemaker import image_uris 
from sagemaker import model_uris
from sagemaker.jumpstart.notebook_utils import list_jumpstart_models

session = sagemaker.Session()

def get_sagemaker_uris(model_id,model_task_type,instance_type,region_name):
    inference_image_uri = image_uris.retrieve(region=region_name, 
                                          framework=None,
                                          model_id=model_id, 
                                          model_version="*" , 
                                          image_scope="inference", 
                                          instance_type=instance_type)
    
    inference_model_uri = model_uris.retrieve(model_id=model_id, 
                                          model_version="*" , 
                                          model_scope="inference")
    
    inference_source_uri = script_uris.retrieve(model_id=model_id, 
                                            model_version="*" , 
                                            script_scope="inference")

    model_bucket_name = inference_model_uri.split("/")[2]
    model_bucket_key = "/".join(inference_model_uri.split("/")[3:])
    model_docker_image = inference_image_uri

    return {"model_bucket_name":model_bucket_name, "model_bucket_key": model_bucket_key, \
            "model_docker_image":model_docker_image, "instance_type":instance_type, \
                "inference_source_uri":inference_source_uri, "region_name":region_name}


# region_name = boto3.Session().region_name
env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
region_name = os.getenv('CDK_DEFAULT_REGION')
MODEL_INFO = get_sagemaker_uris(model_id=MODEL_ID,
                                        model_task_type=TASK_TYPE, 
                                        instance_type=INFERENCE_INSTANCE_TYPE,
                                        region_name=region_name)


app = cdk.App()

network_stack = NetworkingStack(app, "VpcNetworkStack", env=env)
DemoStack(app, "DemoWebStack", vpc=network_stack.vpc, env=env)
GenerativeAiTxt2imgSagemakerStack(app, "Txt2imgSagemakerStack", env=env, model_info=MODEL_INFO)

app.synth()
