from diagrams import  Cluster, Diagram, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
import diagrams.programming.flowchart as FC
from diagrams.c4 import Person, Container, Database, System, SystemBoundary, Relationship


graph_attr = {
    "splines": "spline",
}

with Diagram("", show=False,outformat=["png"], graph_attr=graph_attr):
    FC.Action("NacosConfigBeanDefinitionRegistrar") >> Edge(color="red", style="dotted") >> [FC.Action("ImportBeanDefinitionRegistrar"),
                                                                                                               FC.Action("EnvironmentAware"),
                                                                                                               FC.Action("BeanFactoryAware")]