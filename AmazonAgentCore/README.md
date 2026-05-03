

### Deploy a inference Model in Amazon Bedrock
![alt text](image.png)

### Run the application
![alt text](image-1.png)

![alt text](image-2.png)

![alt text](image-3.png)

Create Docker and Deploy
![alt text](image-4.png)

![alt text](image-5.png)

![alt text](image-6.png)

![alt text](image-7.png)

![alt text](image-8.png)


## Associate the inline Policy

```bash
aws iam put-role-policy \
  --role-name AmazonBedrockAgentCoreSDKRuntime-us-east-1-2292fc8165 \
  --policy-name BedrockInferenceProfileAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "bedrock:GetInferenceProfile",
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ],
        "Resource": [
          "arn:aws:bedrock:us-east-1:395109667422:application-inference-profile/ptbzu6tpt21o",
          "arn:aws:bedrock:us-east-1::foundation-model/*"
        ]
      }
    ]
  }'
```

![alt text](image-9.png)

![alt text](image-10.png)

![alt text](image-12.png)