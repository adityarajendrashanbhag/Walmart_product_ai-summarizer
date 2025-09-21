import boto3, json

# Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# Correct chat-completion style body
body = {
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Summarize: The phone is great but the battery is weak"}
            ]
        }
    ],
    "max_tokens": 200,
    "temperature": 0.3,
    "top_p": 0.9
}

response = bedrock.invoke_model(
    modelId="qwen.qwen3-32b-v1:0",
    contentType="application/json",
    accept="application/json",
    body=json.dumps(body)
)

# Parse Bedrock's response
result = json.loads(response["body"].read())
print(json.dumps(result, indent=2))

# Extract text output if available
if "output" in result:
    print("\nModel Output:\n", result["output"][0]["content"][0]["text"])
