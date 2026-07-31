from pydantic import BaseModel, Field


class LoginData(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password or token")


class ExitStatusItem(BaseModel):
    """What one configured exit is doing right now.

    Named rather than addressed on purpose: a proxy URL carries its credential, and this
    is written for a status page. Set a label on the `proxy_urls` entry to tell several
    apart.
    """

    name: str = Field(..., description="The exit's label, or its host")
    kind: str = Field(..., description="datacenter, isp, residential, mobile, tor or direct")
    clears_reputation: bool = Field(
        default=False,
        description="True if this kind of address can get past a reputation block",
    )
    retired: bool = Field(default=False, description="True if it is being rested after a failure")
    returns_in: float = Field(
        default=0.0, description="Seconds until a retired exit is usable again; 0 if available"
    )
    origins: int = Field(default=0, description="How many origins currently hold a lease on it")
