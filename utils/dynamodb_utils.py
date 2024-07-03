import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

def get_dynamodb_resource():
    """
    DynamoDB 리소스 객체 생성
    :return: boto3 DynamoDB 리소스 객체
    """
    return boto3.resource(
        'dynamodb',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

def create_table_if_not_exists(table_name: str, key_schema: list, attribute_definitions: list, provisioned_throughput: dict):
    """
    DynamoDB 테이블이 존재하지 않으면 생성
    :param table_name: 테이블 이름
    :param key_schema: 키 스키마
    :param attribute_definitions: 속성 정의
    :param provisioned_throughput: 프로비저닝된 처리량 설정
    :return: 생성된 또는 이미 존재하는 테이블 객체
    """
    dynamodb = get_dynamodb_resource()
    
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Table {table_name} created successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {table_name} already exists.")
            table = dynamodb.Table(table_name)
        else:
            print(f"Unexpected error: {e}")
            raise
    
    return table

def get_table(table_name: str):
    """
    DynamoDB 테이블 객체 가져오기
    :param table_name: 테이블 이름
    :return: DynamoDB 테이블 객체
    """
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(table_name)

def batch_write_items(table_name: str, items: list):
    """
    DynamoDB 테이블에 여러 항목을 일괄 작성
    :param table_name: 테이블 이름
    :param items: 작성할 항목 리스트
    """
    table = get_table(table_name)
    
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

def query_items(table_name: str, key_condition_expression, expression_attribute_values):
    """
    DynamoDB 테이블 쿼리
    :param table_name: 테이블 이름
    :param key_condition_expression: 키 조건 표현식
    :param expression_attribute_values: 표현식 속성 값
    :return: 쿼리 결과
    """
    table = get_table(table_name)
    
    response = table.query(
        KeyConditionExpression=key_condition_expression,
        ExpressionAttributeValues=expression_attribute_values
    )
    
    return response['Items']