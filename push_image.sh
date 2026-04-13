#!/bin/bash

ACCOUNT_ID="924665350698"
REGION="us-east-1"

REPOS=(
winvale-backend
)

echo "Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login \
--username AWS \
--password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

for repo in "${REPOS[@]}"
do
    echo "---------------------------------------"
    echo "Processing $repo"

    echo "Creating repo if not exists..."
    aws ecr describe-repositories --repository-names $repo --region $REGION >/dev/null 2>&1 || \
    aws ecr create-repository --repository-name $repo --region $REGION

    echo "Tagging image..."
    docker tag $repo:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$repo:latest

    echo "Pushing image..."
    docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$repo:latest

    echo "$repo pushed successfully"
done

echo "---------------------------------------"
echo "All images pushed to ECR"
 
