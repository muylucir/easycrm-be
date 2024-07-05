from fastapi import HTTPException, status

class CRMException(HTTPException):
    """
    CRM 애플리케이션의 기본 예외 클래스
    """
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class NotFoundException(CRMException):
    """
    리소스를 찾을 수 없을 때 발생하는 예외
    """
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class UnauthorizedException(CRMException):
    """
    인증되지 않은 요청에 대한 예외
    """
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
        self.headers = {"WWW-Authenticate": "Bearer"}

class ForbiddenException(CRMException):
    """
    권한이 없는 요청에 대한 예외
    """
    def __init__(self, detail: str = "Not enough privileges"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class BadRequestException(CRMException):
    """
    잘못된 요청에 대한 예외
    """
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)