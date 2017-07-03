from troposphere import (Sub, Output, Export, Parameter, Ref, Template)
from troposphere.route53 import HostedZone

t = Template()

t.add_description('Template for creating the IYPM DNS Zone on Route53.')

zone_name = t.add_parameter(
    Parameter(
        'ZoneName',
        Description='The name of the DNS Zone to create (example.com).',
        Type='String'))

hosted_zone = t.add_resource(HostedZone('DNSZone', Name=Ref(zone_name)))

t.add_output([
    Output(
        'ZoneId',
        Description='Route53 Zone ID',
        Value=Ref(hosted_zone),
        Export=Export(Sub('${AWS::StackName}-R53Zone'))),
])

print(t.to_json())
