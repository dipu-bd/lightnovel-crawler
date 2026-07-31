from pydantic import BaseModel, Field


class LoginData(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password or token")


class ProxyItem(BaseModel):
    """One configured proxy, and what it is doing right now.

    Configuration and health together because they answer one question — an operator
    looking at a proxy wants to know whether it is working, and a proxy that has been
    retired is the reason a scrape slowed down.

    Secrets never come back out: `token` is replaced by `has_token`, and the URL's
    password by `***`. Send an entry back with either still elided to keep what is
    stored; anything actually typed replaces it.
    """

    id: str = Field(..., description="Stable row identity; send it back when editing")
    url: str = Field(..., description="Proxy URL with its password masked")
    kind: str = Field(..., description="datacenter, isp, residential, mobile, tor or torpool")
    label: str = Field(default="", description="Name shown in logs and here")
    enabled: bool = Field(default=True, description="False keeps the entry without using it")
    api_url: str = Field(default="", description="tor-pool API URL; tor-pool entries only")
    has_token: bool = Field(default=False, description="True if a tor-pool token is stored")

    clears_reputation: bool = Field(
        default=False,
        description="True if this kind of address can get past a reputation block",
    )
    retired: bool = Field(default=False, description="True if it is being rested after a failure")
    returns_in: float = Field(
        default=0.0, description="Seconds until a retired exit is usable again; 0 if available"
    )
    origins: int = Field(default=0, description="How many sites currently hold a lease on it")
