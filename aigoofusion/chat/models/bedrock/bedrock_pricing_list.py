# Price per 1K tokens for different models (USD)
# https://aws.amazon.com/bedrock/pricing/
# https://aws.amazon.com/bedrock/pricing/
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html
BEDROCK_PRICING = {
    "anthropic.claude-3-5-sonnet-20240620-v1:0": {
        "us-east-1": {
            "region": "US East (N. Virginia)",
            "input": 0.003,
            "output": 0.015,
        },
        "us-west-2": {
            "region": "US West (Oregon)",
            "input": 0.003,
            "output": 0.015,
        },
    },
    "anthropic.claude-3-5-sonnet-20241022-v2:0": {
        "us-east-1": {
            "region": "US East (N. Virginia)",
            "input": 0.003,
            "output": 0.015,
        },
        "us-west-2": {
            "region": "US West (Oregon)",
            "input": 0.003,
            "output": 0.015,
        },
    },
    "anthropic.claude-3-5-haiku-20241022-v1:0": {
        "us-east-1": {
            "region": "US East (N. Virginia)",
            "input": 0.0008,
            "output": 0.004,
        },
        "us-west-2": {
            "region": "US West (Oregon)",
            "input": 0.0008,
            "output": 0.004,
        },
    },
    "anthropic.claude-3-sonnet-20240229-v1:0": {
        "us-east-1": {
            "region": "US East (N. Virginia)",
            "input": 0.003,
            "output": 0.015,
        },
        "us-west-2": {
            "region": "US West (Oregon)",
            "input": 0.003,
            "output": 0.015,
        },
    },
    "anthropic.claude-3-haiku-20240307-v1:0": {
        "us-east-1": {
            "region": "US East (N. Virginia)",
            "input": 0.00025,
            "output": 0.00125,
        },
        "us-west-2": {
            "region": "US West (Oregon)",
            "input": 0.00025,
            "output": 0.00125,
        },
    },
    "amazon.nova-pro-v1:0": {
        "us-east-1": {
            "region": "US East (N. Virginia)",
            "input": 0.0008,
            "output": 0.0032,
        },
        "us-west-2": {
            "region": "US West (Oregon)",
            "input": 0.0008,
            "output": 0.0032,
        },
    },
    "amazon.nova-lite-v1:0": {
        "us-east-1": {
            "region": "US East (N. Virginia)",
            "input": 0.00006,
            "output": 0.00024,
        },
        "us-west-2": {
            "region": "US West (Oregon)",
            "input": 0.00006,
            "output": 0.00024,
        },
    },
}
