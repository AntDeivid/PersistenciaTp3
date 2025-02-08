from pydantic import BaseModel


class PaginationResult(BaseModel):
    page: int
    limit: int
    total_items: int
    number_of_pages: int
    data: list