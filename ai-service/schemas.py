from pydantic import BaseModel, ConfigDict, Field, StrictBool


class Book(BaseModel):
    """图书响应模型。"""

    id: int
    title: str
    author: str
    available: bool


class BookCreate(BaseModel):
    """新增图书请求模型。"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    title: str = Field(
        min_length=1,
        max_length=100,
        description="图书名称",
    )
    author: str = Field(
        min_length=1,
        max_length=100,
        description="图书作者",
    )
    available: StrictBool = Field(
        default=True,
        description="图书当前是否可借",
    )


class BookAvailabilityUpdate(BaseModel):
    """修改图书可借状态的请求模型。"""

    model_config = ConfigDict(extra="forbid")

    available: StrictBool = Field(
        description="图书修改后的可借状态",
    )
