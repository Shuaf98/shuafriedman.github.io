
# AWS CDK Stack: RdsEc2BastionStack

This code provides an AWS CDK Stack (RdsEc2BastionStack) that deploys a set of AWS resources, including VPC, EC2 instance, RDS database, Secrets Manager parameter, Lambda function, and an API Gateway, among others. 

## AWS Resources

### Virtual Private Cloud (VPC)

This stack deploys a VPC named 'MyVpc'. The VPC is configured with three subnet types: 

- Private with Egress: These subnets can communicate with the internet through a NAT gateway.
- Public: These subnets can directly communicate with the internet.
- Private Isolated: These subnets can only communicate with other resources within the VPC. 

### EC2 Instance (Bastion Host)

The stack deploys an EC2 instance (bastion host) within the Public subnet of the VPC. This instance uses a `t2.micro` instance type and runs on Amazon Linux 2. 

The security group (`ec2-sg`) for the EC2 instance allows ingress (incoming) connections for TCP traffic on port 22 (SSH) from any IPv4 address.

### RDS Database Cluster

This stack deploys an RDS database cluster (Aurora MySQL) within the Private Isolated subnet. It creates a default database 'db' and uses a generated secret for the 'clusteradmin' credentials. The secret's name is stored as a parameter ('db-secret-name') in AWS Systems Manager's Parameter Store.

The security group (`rds-sg`) for the RDS cluster allows inbound traffic from the EC2 instance on port 3306.

### AWS Lambda Function

A Lambda function is deployed to connect to the RDS cluster. The function uses Python 3.8 runtime and is granted read access to the RDS secret in Secrets Manager for database credentials.

The function is associated with a security group (`lambda-sg`) that allows it to connect to the RDS cluster.

A Lambda layer (`lambda-layer`) with pymysql installed is created and associated with the function. This layer allows the function to use the pymysql package to interact with MySQL databases.

The Lambda function is deployed within the Private Isolated subnet of the VPC and has an interface VPC endpoint to the Secrets Manager service. This allows the function to access the Secrets Manager service within the AWS network, improving security.

### API Gateway

Finally, the stack creates an API Gateway that acts as an interface for the Lambda function. The API Gateway uses a `REGIONAL` endpoint type and is configured to allow CORS (Cross-Origin Resource Sharing) for all origins, methods, and headers.

### Connecting to the RDS Database Cluster
Deployment app currently uses a bastion host proxy to connect to the database in a private server. In order to connect a local machine to the database to access from MYSQL workbench, or any other GUI, take the following steps:

1) Generate a public and private key pair (generate a .pem key pair, and then create the public key from the .pem file

2) Upload the public key to the ec2 instance:

aws ec2-instance-connect send-ssh-public-key --instance-id xxxxxxxxxxxxx --instance-os-user xxxxx --ssh-public-key file://~/.ssh/xxxxxx.pub

NOTE: The key only exists for 60 seconds in the proxy, for security. Need to re-upload each session.

3) Connect over SSH in the GUI (MySQL Workbench for this stack), and enter the writer endpoint details of the RDS database (can be found in Secrets Manager).

## CDK Usage

To use this code, you would need the AWS CDK installed and configured with appropriate AWS credentials. The assets for the Lambda function and layer should be present in the 'lambda' and 'lambda/layer' directories respectively.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
