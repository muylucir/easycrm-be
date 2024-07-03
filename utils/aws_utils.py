import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

def get_aws_session():
    """
    AWS 세션 생성
    :return: boto3 Session 객체
    """
    return boto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

def get_ssm_parameter(param_name: str, with_decryption: bool = True):
    """
    AWS Systems Manager Parameter Store에서 파라미터 값을 가져옴
    :param param_name: 파라미터 이름
    :param with_decryption: 암호화된 파라미터 복호화 여부
    :return: 파라미터 값
    """
    session = get_aws_session()
    ssm_client = session.client('ssm')
    
    try:
        response = ssm_client.get_parameter(
            Name=param_name,
            WithDecryption=with_decryption
        )
        return response['Parameter']['Value']
    except ClientError as e:
        print(f"Error getting parameter {param_name}: {e}")
        return None

def create_cognito_user(username: str, password: str, user_attributes: list):
    """
    Cognito 사용자 생성
    :param username: 사용자 이름
    :param password: 비밀번호
    :param user_attributes: 사용자 속성 리스트
    :return: 생성된 사용자 정보
    """
    session = get_aws_session()
    cognito_client = session.client('cognito-idp')
    
    try:
        response = cognito_client.sign_up(
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=user_attributes
        )
        return response
    except ClientError as e:
        print(f"Error creating Cognito user: {e}")
        raise

def confirm_cognito_signup(username: str):
    """
    Cognito 사용자 가입 확인
    :param username: 사용자 이름
    """
    session = get_aws_session()
    cognito_client = session.client('cognito-idp')
    
    try:
        cognito_client.admin_confirm_sign_up(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            Username=username
        )
    except ClientError as e:
        print(f"Error confirming Cognito signup: {e}")
        raise

def delete_cognito_user(username: str):
    """
    Cognito 사용자 삭제
    :param username: 사용자 이름
    """
    session = get_aws_session()
    cognito_client = session.client('cognito-idp')
    
    try:
        cognito_client.admin_delete_user(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            Username=username
        )
    except ClientError as e:
        print(f"Error deleting Cognito user: {e}")
        raise