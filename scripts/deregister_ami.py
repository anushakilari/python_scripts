#!/usr/bin/env python
#################################################################################################################
#python script to deregister amis in datelimit
#################################################################################################################
import json
import boto3
import datetime

def print_json(j):
    print(json.dumps(j, indent=2, sort_keys=True))

def deregister_ami(client,image_id):
    print "deregistering "+image_id+" ami"
    response = client.deregister_image(ImageId=image_id,DryRun=False )
    print "deregistered ami id response " + response

def delete_snapshot(client,snapshot_id):
    print "deleting snapshot "+snapshot_id
    response = client.delete_snapshot(SnapshotId=snapshot_id,DryRun=False)
    print "deleted snapshot id response "+response

def ami_list(client):
    timeLimit = datetime.timedelta(days=3) - datetime.timedelta(days=30)
    filters = [
        {
            'Name': 'state',
            'Values': ['available']
        },
        {
            'Name': 'root-device-type',
            'Values': ['ebs']
        },
        {
            'Name': 'virtualization-type',
            'Values': ['hvm']
        },
        {
            'Name': 'hypervisor',
            'Values': ['xen']
        } # filters to filter ami 
    ]
    image = client.describe_images(Filters=filters)
    #print_json(image)
    timeLimit = datetime.datetime.now() - datetime.timedelta(days=3)
    timeLimit = timeLimit.strftime('%Y-%m-%d')
    #print(timeLimit)
    if len(image["Images"]) != 0:
        for image_ids in image["Images"]:
            image_date = image_ids["CreationDate"]
            print(image_date)
            if image_date <= timeLimit:
                image_name = image_ids["Name"]
                print "======================================================================================="
                print(image_name)
                image_id = image_ids["ImageId"]
                print "deregistering image: " + image_id
                deregister_ami(client,image_id)
                for device in image_ids["BlockDeviceMappings"]:
                    if 'SnapshotId' in device['Ebs']:
                        snapshot_id = device['Ebs']['SnapshotId']
                        print "snapshot ids " + snapshot_id
                        delete_snapshot(client,snapshot_id)
                print "======================================================================================="

def main():
    regions=['us-west-2','us-east-1','ap-south-1']
    for region in regions:
        print "region is "+region
        client = boto3.client('ec2', region)
        ami_list(client)
        
if __name__ == "__main__":
    main()
