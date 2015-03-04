#!/bin/sh

for region in ap-northeast-1 ap-southeast-1 ap-southeast-2 eu-west-1 sa-east-1 us-east-1 us-west-1 us-west-2
do
  for instance in c1.medium c1.xlarge c3.2xlarge c3.large c3.xlarge hi1.4xlarge m1.large m1.medium m1.small m1.xlarge m2.2xlarge m2.4xlarge m2.xlarge m3.large m3.medium m3.xlarge
  do
    echo "Region: $region InstanceType: $instance"
    aws ec2 describe-reserved-instances-offerings --region $region --instance-type $instance > json/$region-$instance.json
  done
done

echo "Done"
