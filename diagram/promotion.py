from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
import diagrams.programming.flowchart as FC

with Diagram("promotion", show=False,outformat=["png"],direction="TB"):
    FC.Action("Action") >> [FC.Database("Database")]