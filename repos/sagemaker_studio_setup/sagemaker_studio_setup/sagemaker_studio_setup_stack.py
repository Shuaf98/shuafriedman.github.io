from aws_cdk import (
	aws_iam as iam,
	aws_ec2 as ec2,
	aws_sagemaker as _sagemaker,
	core
)
from constructs import Construct
import sagemaker_constructs

class SagemakerStudioSetupStack(Stack):

	def __init__(self, scope: core.Construct, construct_id: str,
	             **kwargs) -> None:
		super().__init__(scope, construct_id, **kwargs)
		role_sagemaker_studio_domain = iam.Role(self, 'RoleForSagemakerStudioUsers',
		                                        assumed_by=iam.ServicePrincipal('sagemaker.amazonaws.com'),
		                                        role_name="RoleSagemakerStudioUsers",
		                                        managed_policies=[
			                                        iam.ManagedPolicy.from_managed_policy_arn(self,
			                                                                                  id="SagemakerReadAccess",
			                                                                                  managed_policy_arn="arn:aws:iam::aws:policy/AmazonSageMakerFullAccess")
		                                        ])
		self.role_sagemaker_studio_domain = role_sagemaker_studio_domain
		self.sagemaker_domain_name = "StudioDomain"

		default_vpc_id = ec2.Vpc.from_lookup(self, "VPC",
		                                     vpc_id=self.node.try_get_context('existing_vpc_id')
		                                     )

		self.vpc_id = default_vpc_id.vpc_id
		self.public_subnet_ids = [public_subnet.subnet_id for public_subnet in default_vpc_id.public_subnets]

		my_sagemaker_domain = sagemaker_constructs.SagemakerStudioDomainConstruct(self, "mySagemakerStudioDomain",
		                                                                               sagemaker_domain_name=self.sagemaker_domain_name,
		                                                                               vpc_id=self.vpc_id,
		                                                                               subnet_ids=self.public_subnet_ids,
		                                                                               role_sagemaker_studio_users=self.role_sagemaker_studio_domain)

		team_to_add_in_sagemaker_studio = ["datascientist-team-1", "datascientist-team-2",
		                                   "datascientist-team-3"]
		for _team in team_to_add_in_sagemaker_studio:
			my_default_datascience_user = sagemaker_constructs.SagemakerStudioUserConstruct(self,
			                                                                                     _team,
			                                                                                     sagemaker_domain_id=my_sagemaker_domain.sagemaker_domain_id,
			                                                                                     user_profile_name=_team)
			core.CfnOutput(self, f"cfnoutput{_team}",
			               value=my_default_datascience_user.user_profile_arn,
			               description="The User Arn TeamA domain ID",
			               export_name=F"UserArn{_team}"
			               )
    
		core.CfnOutput(self, "DomainIdSagemaker",
		               value=my_sagemaker_domain.sagemaker_domain_id,
		               description="The sagemaker domain ID",
		               export_name="DomainIdSagemaker"
		               )
