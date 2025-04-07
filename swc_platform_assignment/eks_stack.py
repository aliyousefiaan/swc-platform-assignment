from aws_cdk import (
    Stack,
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_iam as iam,
    CustomResource
)
from constructs import Construct
import json
from swc_platform_assignment.helpers.tags import common_tags
from aws_cdk.lambda_layer_kubectl_v32 import KubectlV32Layer

class EksStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, values: CustomResource, config: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        eks_config = config.get("eks_main_configurations", {})
        node_group_config = config.get("eks_main_managed_node_group_general_settings", {})

        # Create EKS cluster
        self.cluster = eks.Cluster(
            self,
            construct_id,
            cluster_name=f"main-{config['environment']}",
            version=getattr(eks.KubernetesVersion, eks_config.get("cluster_version")),
            vpc=vpc,
            vpc_subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)],
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,
            default_capacity=0,
            kubectl_layer=KubectlV32Layer(self, "kubectl"),
            alb_controller={
                "version": getattr(eks.AlbControllerVersion, eks_config.get("alb_controller_version"))
            },
        )
        common_tags(self.cluster, config)

        # Add managed node group
        node_group = self.cluster.add_nodegroup_capacity(
            "GeneralWorkers",
            ami_type=eks.NodegroupAmiType.BOTTLEROCKET_X86_64,
            desired_size=node_group_config.get("desired_size"),
            min_size=node_group_config.get("min_size"),
            max_size=node_group_config.get("max_size"),
            instance_types=[ec2.InstanceType(instance_type) for instance_type in node_group_config.get("instance_types", [])],
            capacity_type=getattr(eks.CapacityType, node_group_config.get("capacity_type")),
            labels={"nodegroup": "general-workers"}
        )
        common_tags(node_group, config)

        # Add EBS CSI Driver policy to node group role
        node_group.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEBSCSIDriverPolicy")
        )

        # Add IAM user mapping to allow access to the cluster
        self.cluster.aws_auth.add_user_mapping(
            user=iam.User.from_user_arn(
                self,
                "EKSAdminRole",
                user_arn=iam.AccountRootPrincipal().arn
            ),
            groups=["system:masters"]
        )

        # Add EKS addons
        eks.CfnAddon(
            self,
            "CoreDnsAddon",
            addon_name="coredns",
            cluster_name=self.cluster.cluster_name,
        )
        eks.CfnAddon(
            self,
            "KubeProxyAddon",
            addon_name="kube-proxy",
            cluster_name=self.cluster.cluster_name,
        )
        eks.CfnAddon(
            self,
            "VpcCniAddon",
            addon_name="vpc-cni",
            cluster_name=self.cluster.cluster_name,
            configuration_values=json.dumps({
                "enableNetworkPolicy": "true",
                "env": {
                    "NETWORK_POLICY_ENFORCING_MODE": "standard"
                }
            })
        )
        eks.CfnAddon(
            self,
            "EbsCsiDriverAddon",
            addon_name="aws-ebs-csi-driver",
            cluster_name=self.cluster.cluster_name,
        )

        replica_count = values.get_att_string("ReplicaCount")
        # Install ingress-nginx Helm chart
        self.cluster.add_helm_chart(
            "IngressNginx",
            release="ingress-nginx",
            chart="ingress-nginx",
            repository="https://kubernetes.github.io/ingress-nginx",
            namespace="ingress-nginx",
            create_namespace=True,
            version="4.12.1",
            values={
                "controller": {
                    "replicaCount": replica_count
                }
            }
        )
