"""
Pydantic schemas for IBKR Scanner endpoints.
These models validate responses from /iserver/scanner/params and /iserver/scanner/run.
"""
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

# --- Parameters Schemas ---

class ScannerParamItem(BaseModel):
    """Basic item in a scanner parameter list."""
    display_name: str = Field(alias="display_name")
    code: str = Field(alias="code")

class ScannerLocation(BaseModel):
    """Location item in the location tree."""
    display_name: str = Field(alias="display_name")
    type: str = Field(alias="type")
    locations: Optional[List['ScannerLocation']] = None

class ScannerParams(BaseModel):
    """Full response from /iserver/scanner/params."""
    scan_type_list: List[ScannerParamItem] = Field(alias="scan_type_list", default_factory=list)
    instrument_list: List[ScannerParamItem] = Field(alias="instrument_list", default_factory=list)
    filter_list: List[ScannerParamItem] = Field(alias="filter_list", default_factory=list)
    location_tree: List[ScannerLocation] = Field(alias="location_tree", default_factory=list)

# --- Execution Schemas ---

class ScannerFilter(BaseModel):
    """Definition for an individual filter in a scan request."""
    code: str
    value: Union[int, float, str, bool]

class ScannerRequest(BaseModel):
    """Request body for executing a scan via /iserver/scanner/run."""
    instrument: str
    type: str
    location: str
    filter: List[ScannerFilter] = Field(default_factory=list)

class ScannerResultItem(BaseModel):
    """A single result item from a scanner execution."""
    conid: int
    symbol: str
    company_name: Optional[str] = Field(None, alias="company_name")
    last: Optional[float] = None
    change: Optional[float] = None
    change_pct: Optional[float] = Field(None, alias="change_pct")
    volume: Optional[int] = None
    # Scanners often return additional fields depending on the scan type
    extra_data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "allow"
        populate_by_name = True

class ScannerResponse(BaseModel):
    """Full response containing scanner results."""
    total: int
    offset: int
    limit: int
    results: List[ScannerResultItem] = Field(default_factory=list)
