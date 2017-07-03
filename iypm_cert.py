import sys

try:
    from troposphere import Sub, Output, Export
    from troposphere import Parameter, Ref, Template
    from troposphere.certificatemanager import Certificate
except ImportError:
    sys.exit('Unable to import troposphere. '
             'Try "pip install troposphere[policy]".')


t = Template()


t.add_description(
    'Template for creating SSL/TLS certificates using ACM. '
    'Note: Stack creation will block until domain ownership is verified.')


domain_name = t.add_parameter(Parameter(
    'DomainName',
    Description='The name of the domain to create certificates for (example.com).',
    Type='String'
))


acm_certificate = t.add_resource(Certificate(
    'Certificate',
    DomainName=Ref(domain_name),
    SubjectAlternativeNames=[Sub('*.${DomainName}')]
))


t.add_output([
    Output(
        'CertificateId',
        Description='ACM Certificate ARN',
        Value=Ref(acm_certificate),
        Export=Export(Sub('${AWS::StackName}-CertARN'))
    )
])

print(t.to_json())
