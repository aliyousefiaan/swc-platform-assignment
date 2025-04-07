from swc_platform_assignment.lambda_values.lambda_values import lambda_handler

def test_dev_environment(mocker):
    # Mock the event and context
    event = {
        'RequestType': 'Create',
        'ResourceProperties': {
            'ParameterName': '/test/param'
        }
    }
    context = {}

    # Mock boto3 SSM client
    mock_ssm = mocker.Mock()
    mock_ssm.get_parameter.return_value = {
        'Parameter': {
            'Value': 'dev'
        }
    }
    mocker.patch('boto3.client', return_value=mock_ssm)

    # Mock cfnresponse.send
    mock_cfnresponse = mocker.patch('cfnresponse.send')

    # Call the handler
    lambda_handler(event, context)

    # Verify the response
    mock_cfnresponse.assert_called_once()
    call_args = mock_cfnresponse.call_args[0]
    assert call_args[2] == 'SUCCESS'
    response_data = call_args[3]
    assert response_data['ReplicaCount'] == '1'
    assert response_data['Environment'] == 'dev'

def test_staging_environment(mocker):
    event = {
        'RequestType': 'Create',
        'ResourceProperties': {
            'ParameterName': '/test/param'
        }
    }
    context = {}

    mock_ssm = mocker.Mock()
    mock_ssm.get_parameter.return_value = {
        'Parameter': {
            'Value': 'staging'
        }
    }
    mocker.patch('boto3.client', return_value=mock_ssm)
    mock_cfnresponse = mocker.patch('cfnresponse.send')

    lambda_handler(event, context)

    mock_cfnresponse.assert_called_once()
    call_args = mock_cfnresponse.call_args[0]
    assert call_args[2] == 'SUCCESS'
    response_data = call_args[3]
    assert response_data['ReplicaCount'] == '2'
    assert response_data['Environment'] == 'staging'

def test_prod_environment(mocker):
    event = {
        'RequestType': 'Create',
        'ResourceProperties': {
            'ParameterName': '/test/param'
        }
    }
    context = {}

    mock_ssm = mocker.Mock()
    mock_ssm.get_parameter.return_value = {
        'Parameter': {
            'Value': 'prod'
        }
    }
    mocker.patch('boto3.client', return_value=mock_ssm)
    mock_cfnresponse = mocker.patch('cfnresponse.send')

    lambda_handler(event, context)

    mock_cfnresponse.assert_called_once()
    call_args = mock_cfnresponse.call_args[0]
    assert call_args[2] == 'SUCCESS'
    response_data = call_args[3]
    assert response_data['ReplicaCount'] == '2'
    assert response_data['Environment'] == 'prod'

def test_delete_request(mocker):
    event = {
        'RequestType': 'Delete',
        'ResourceProperties': {
            'ParameterName': '/test/param'
        }
    }
    context = {}

    mock_cfnresponse = mocker.patch('cfnresponse.send')

    lambda_handler(event, context)

    mock_cfnresponse.assert_called_once()
    call_args = mock_cfnresponse.call_args[0]
    assert call_args[2] == 'SUCCESS'
    assert call_args[3] == {}

def test_invalid_environment(mocker):
    event = {
        'RequestType': 'Create',
        'ResourceProperties': {
            'ParameterName': '/test/param'
        }
    }
    context = {}

    mock_ssm = mocker.Mock()
    mock_ssm.get_parameter.return_value = {
        'Parameter': {
            'Value': 'invalid'
        }
    }
    mocker.patch('boto3.client', return_value=mock_ssm)
    mock_cfnresponse = mocker.patch('cfnresponse.send')

    lambda_handler(event, context)

    mock_cfnresponse.assert_called_once()
    call_args = mock_cfnresponse.call_args[0]
    assert call_args[2] == 'FAILED'
    assert 'Unknown environment' in call_args[3]['Message'] 
