from aws_cdk import Tags

def common_tags(stack, config: dict) -> None:
    common_tags = {
        "Environment": config['environment'],
        "Project": config['project']
    }
    
    for key, value in common_tags.items():
        Tags.of(stack).add(key, value) 
