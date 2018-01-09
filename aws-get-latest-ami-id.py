#===============================================================================
# Function: get-latest-ami-id
#
# Purpose:  Retrieves the latest Amazon Linux AMI ID for each region.
#===============================================================================
import boto3
import json
from operator import itemgetter

#=================================================
# default handler
#=================================================
def lambda_handler(event, context):
    
    image_list = {}
    
    # Loop through each region and get the most recent Amazon AMI for the given 
    # image name.
    for region in boto3.client('ec2').describe_regions()['Regions']:
        
        region_name = region['RegionName']
        
        # Get a list of all Amazon-owned HVM images.
        images = boto3.client('ec2', region_name=region_name).describe_images(
            Filters = [
                {"Name": "name", "Values": ["amzn-ami-hvm-2017*-x86_64-gp2"]}
                ],
            Owners = ["amazon"])['Images']
        
        # Sort the images with the most recent first.
        images = sorted(images, key=itemgetter('Name'), reverse=True)

        # Get the most recent non-beta and non-RC image.
        for image in images:
            if not ('rc' in image['Name'].lower() or 'beta' in image['Name'].lower()):
                image_list[region_name] = {"AMZNLINUXHVM": image['ImageId']}
                break

    # Output the results to CloudWatch Logs.
    print(json.dumps(image_list))

    # Return the JSON list of AMIs per region.
    return image_list