from diagrams import  Cluster, Diagram, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
import diagrams.programming.flowchart as FC

with Diagram("费曼学习五部曲", show=False,outformat=["png"]):
    FC.Action("第一步:目标")  >> FC.Action("确立学习对象")  >> FC.Action("产生专注力")
    FC.Action("第二步:理解")  >> FC.Action("确立学习对象")  >> FC.Action("产生专注力")
    
    