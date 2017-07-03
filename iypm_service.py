from troposphere import (GetAtt, Join, Sub, Output, FindInMap, Parameter, Ref,
                         Template, ImportValue)
from troposphere.cloudfront import (Distribution, DistributionConfig, Origin,
                                    DefaultCacheBehavior, ForwardedValues,
                                    ViewerCertificate, CustomOrigin, Logging,
                                    CustomErrorResponse, Cookies)
from troposphere.s3 import (Bucket, PublicRead, WebsiteConfiguration,
                            RedirectAllRequestsTo)
from troposphere.route53 import (RecordSetType, AliasTarget)

t = Template()

t.add_description(
    'Template for creating an AWS stack for serving the IYPM front-end.')

t.add_mapping('RegionMap', {
    'us-east-2': {
        'HostedZoneId': 'Z2O1EMRO9K5GLX',
        'WebsiteEndpoint': 's3-website.us-east-2.amazonaws.com'
    },
    'us-east-1': {
        'HostedZoneId': 'Z3AQBSTGFYJSTF',
        'WebsiteEndpoint': 's3-website-us-east-1.amazonaws.com'
    },
    'us-west-1': {
        'HostedZoneId': 'Z2F56UZL2M1ACD',
        'WebsiteEndpoint': 's3-website-us-west-1.amazonaws.com'
    },
    'us-west-2': {
        'HostedZoneId': 'Z3BJ6K6RIION7M',
        'WebsiteEndpoint': 's3-website-us-west-2.amazonaws.com'
    },
    'ca-central-1': {
        'HostedZoneId': 'Z1QDHH18159H29',
        'WebsiteEndpoint': 's3-website.ca-central-1.amazonaws.com'
    },
    'ap-south-1': {
        'HostedZoneId': 'Z11RGJOFQNVJUP',
        'WebsiteEndpoint': 's3-website.ap-south-1.amazonaws.com'
    },
    'ap-northeast-2': {
        'HostedZoneId': 'Z3W03O7B5YMIYP',
        'WebsiteEndpoint': 's3-website.ap-northeast-2.amazonaws.com'
    },
    'ap-southeast-1': {
        'HostedZoneId': 'Z3O0J2DXBE1FTB',
        'WebsiteEndpoint': 's3-website-ap-southeast-1.amazonaws.com'
    },
    'ap-southeast-2': {
        'HostedZoneId': 'Z1WCIGYICN2BYD',
        'WebsiteEndpoint': 's3-website-ap-southeast-2.amazonaws.com'
    },
    'ap-northeast-1': {
        'HostedZoneId': 'Z2M4EHUR26P7ZW',
        'WebsiteEndpoint': 's3-website-ap-northeast-1.amazonaws.com'
    },
    'eu-central-1': {
        'HostedZoneId': 'Z21DNDUVLTQW6Q',
        'WebsiteEndpoint': 's3-website.eu-central-1.amazonaws.com'
    },
    'eu-west-1': {
        'HostedZoneId': 'Z1BKCTXD74EZPE',
        'WebsiteEndpoint': 's3-website-eu-west-1.amazonaws.com'
    },
    'eu-west-2': {
        'HostedZoneId': 'Z3GKZC51ZF0DB4',
        'WebsiteEndpoint': 's3-website.eu-west-2.amazonaws.com'
    },
    'sa-east-1': {
        'HostedZoneId': 'Z7KQH4QJS55SO',
        'WebsiteEndpoint': 's3-website-sa-east-1.amazonaws.com'
    }
})

# Parameters
zone_name = t.add_parameter(
    Parameter(
        'ZoneName',
        Description='The name of the DNS Zone (example.com)',
        Type='String'))

domain_stack_name = t.add_parameter(
    Parameter(
        'DomainStackName',
        Description='Domain stack which exports a ZoneId',
        Type='String'))

acm_cert_arn = t.add_parameter(
    Parameter(
        'ACMCertARN',
        Description='ACM certificate ARN covering the desired DNS zone',
        Type='String'))

# S3 Buckets
root_bucket = t.add_resource(
    Bucket(
        'RootBucket',
        BucketName=Sub('${ZoneName}-root'),
        AccessControl=PublicRead,
        WebsiteConfiguration=WebsiteConfiguration(
            IndexDocument='index.html', ErrorDocument='index.html')))

redirect_bucket = t.add_resource(
    Bucket(
        'RedirectBucket',
        BucketName=Sub('${ZoneName}-redirect'),
        AccessControl=PublicRead,
        WebsiteConfiguration=WebsiteConfiguration(
            RedirectAllRequestsTo=RedirectAllRequestsTo(
                HostName=Ref(zone_name), Protocol='https'), )))

log_bucket = t.add_resource(
    Bucket('AccessLogBucket', BucketName=Sub('${ZoneName}-log')))

# Cloudfront Distributions
root_distribution = t.add_resource(
    Distribution(
        'RootDistribution',
        DistributionConfig=DistributionConfig(
            Comment='Cloudfront distribution for zone root',
            Aliases=[Ref(zone_name)],
            Origins=[
                Origin(
                    Id='RootEndpoint',
                    DomainName=Join('.', [
                        Ref(root_bucket),
                        FindInMap('RegionMap',
                                  Ref('AWS::Region'), 'WebsiteEndpoint')
                    ]),
                    CustomOriginConfig=CustomOrigin(
                        OriginProtocolPolicy='http-only'))
            ],
            DefaultCacheBehavior=DefaultCacheBehavior(
                Compress=True,
                CachedMethods=['GET', 'HEAD'],
                TargetOriginId='RootEndpoint',
                ForwardedValues=ForwardedValues(
                    QueryString=False, Cookies=Cookies(Forward='none')),
                ViewerProtocolPolicy='redirect-to-https'),
            CustomErrorResponses=[
                CustomErrorResponse(
                    ErrorCode=404, ResponseCode=200, ResponsePagePath='/')
            ],
            DefaultRootObject='index.html',
            Enabled=True,
            Logging=Logging(
                Bucket=GetAtt(log_bucket, 'DomainName'), IncludeCookies=True),
            PriceClass='PriceClass_All',
            HttpVersion='http2',
            ViewerCertificate=ViewerCertificate(
                AcmCertificateArn=Ref(acm_cert_arn),
                SslSupportMethod='sni-only'))))

redirect_distribution = t.add_resource(
    Distribution(
        'RedirectDistribution',
        DistributionConfig=DistributionConfig(
            Comment='Cloudfront distribution for wildcard redirection',
            Aliases=[Sub('*.${ZoneName}')],
            Origins=[
                Origin(
                    Id=Sub('RedirectEndpoint'),
                    DomainName=Join('.', [
                        Ref(redirect_bucket),
                        FindInMap('RegionMap',
                                  Ref('AWS::Region'), 'WebsiteEndpoint')
                    ]),
                    CustomOriginConfig=CustomOrigin(
                        OriginProtocolPolicy='http-only'))
            ],
            DefaultCacheBehavior=DefaultCacheBehavior(
                Compress=True,
                CachedMethods=['GET', 'HEAD'],
                TargetOriginId='RedirectEndpoint',
                ForwardedValues=ForwardedValues(
                    QueryString=False, Cookies=Cookies(Forward='none')),
                ViewerProtocolPolicy='allow-all'),
            Enabled=True,
            PriceClass='PriceClass_All',
            HttpVersion='http2',
            ViewerCertificate=ViewerCertificate(
                AcmCertificateArn=Ref(acm_cert_arn),
                SslSupportMethod='sni-only'))))

# Route53 Records
root_alias_record = t.add_resource(
    RecordSetType(
        'RootDistributionAliasRecord',
        HostedZoneId=ImportValue(Sub('${DomainStackName}-R53Zone')),
        Comment='Apex alias record for root distribution',
        Name=Sub('${ZoneName}.'),
        Type='A',
        AliasTarget=AliasTarget(
            DNSName=GetAtt(root_distribution, 'DomainName'),
            HostedZoneId='Z2FDTNDATAQYW2')))

wildcard_alias_record = t.add_resource(
    RecordSetType(
        'RedirectDistributionAliasRecord',
        HostedZoneId=ImportValue(Sub('${DomainStackName}-R53Zone')),
        Comment='Wildcard alias record for redirect distribution',
        Name=Sub('*.${ZoneName}.'),
        Type='A',
        AliasTarget=AliasTarget(
            DNSName=GetAtt(redirect_distribution, 'DomainName'),
            HostedZoneId='Z2FDTNDATAQYW2')))

t.add_output([
    Output(
        'RootDistributionId',
        Description='Cloudfront distribution ID for root zone',
        Value=Ref(root_distribution)),
    Output(
        'RootDistributionEndpoint',
        Description='Cloudfront endpoint for root zone',
        Value=Join('', ['http://',
                        GetAtt(root_distribution, 'DomainName')])),
    Output(
        'RedirectDistributionId',
        Description='Cloudfront distribution ID for subdomain wildcard redirect',
        Value=Ref(redirect_distribution)),
    Output(
        'RedirectDistributionEndpoint',
        Description='Cloudfront endpoint for subdomain wildcard redirect',
        Value=Join('',
                   ['http://',
                    GetAtt(redirect_distribution, 'DomainName')])),
    Output(
        'AccessLogBucket',
        Description='Cloudfront access log S3 bucket ID',
        Value=Ref(log_bucket))
])

print(t.to_json())
