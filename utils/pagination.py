from fastapi import Query
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')

class Page(BaseModel, Generic[T]):
    """
    페이지네이션 결과를 나타내는 Pydantic 모델
    """
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

def paginate(items: List[T], page: int = 1, size: int = 10) -> Page[T]:
    """
    주어진 항목 리스트를 페이지네이션
    :param items: 페이지네이션할 항목 리스트
    :param page: 현재 페이지 번호
    :param size: 페이지당 항목 수
    :return: 페이지네이션된 결과
    """
    total = len(items)
    pages = (total + size - 1) // size
    start = (page - 1) * size
    end = start + size
    
    return Page(
        items=items[start:end],
        total=total,
        page=page,
        size=size,
        pages=pages
    )

class PaginationParams:
    """
    페이지네이션 파라미터를 위한 의존성 클래스
    """
    def __init__(
        self,
        page: int = Query(1, ge=1, description="페이지 번호"),
        size: Optional[int] = Query(10, ge=1, le=100, description="페이지당 항목 수")
    ):
        self.page = page
        self.size = size