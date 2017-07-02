import sys

try:
    from troposphere import Join, Sub, Output, Export
    from troposphere import Parameter, Ref, Template
    from troposphere.route53 import HostedZone
    from troposphere.certificatemanager import Certificate
except ImportError:
    sys.exit('Unable to import troposphere. '
             'Try "pip install troposphere[policy]".')


t = Template()


t.add_description(
    'Template for creating a DNS Zone and SSL Certificate. '
    'Note: Stack creation will block until domain ownership is verified.')


zone_name = t.add_parameter(Parameter(
    'ZoneName',
    Description='The name of the DNS Zone to create (example.com).',
    Type='String'
))


hosted_zone = t.add_resource(HostedZone('DNSZone', Name=Ref(zone_name)))


acm_certificate = t.add_resource(Certificate(
    'Certificate',
    DomainName=Ref(zone_name),
    SubjectAlternativeNames=[Sub('*.${ZoneName}')]
))


t.add_output([
    Output(
        'ZoneId',
        Description='Route53 Zone ID',
        Value=Ref(hosted_zone),
        Export=Export(Sub('${AWS::StackName}-R53Zone'))
    ),
    Output(
        'CertificateId',
        Description='ACM Certificate ARN',
        Value=Ref(acm_certificate),
        Export=Export(Sub('${AWS::StackName}-CertARN'))
    )
])


print(t.to_json())
