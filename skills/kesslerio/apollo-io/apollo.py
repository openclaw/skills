#!/usr/bin/env python3
"""
Apollo.io API client wrapper.
"""

import os
import sys
import requests
from typing import Optional, Dict, Any, List

BASE_URL = "https://api.apollo.io/v1"


class ApolloClient:
    """Simple Apollo.io API client."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("APOLLO_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Apollo API key required. Set APOLLO_API_KEY environment variable."
            )
        self.session = requests.Session()
        self.session.headers.update({
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        })
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make GET request to Apollo API."""
        url = f"{BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params or {})
        response.raise_for_status()
        return response.json()
    
    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make POST request to Apollo API."""
        url = f"{BASE_URL}/{endpoint}"
        response = self.session.post(url, json=data or {})
        response.raise_for_status()
        return response.json()
    
    def search_people(
        self,
        q_keywords: Optional[str] = None,
        person_titles: Optional[List[str]] = None,
        organization_ids: Optional[List[str]] = None,
        organization_names: Optional[List[str]] = None,
        per_page: int = 25,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        Search for people in Apollo's database.
        
        Args:
            q_keywords: General search keywords
            person_titles: List of job titles to match
            organization_ids: Apollo organization IDs
            organization_names: Company names to match
            per_page: Results per page (max 100)
            page: Page number
        """
        data = {"per_page": per_page, "page": page}
        
        if q_keywords:
            data["q_keywords"] = q_keywords
        if person_titles:
            data["person_titles"] = person_titles
        if organization_ids:
            data["organization_ids"] = organization_ids
        if organization_names:
            data["organization_names"] = organization_names
            
        return self._post("mixed_people/search", data)
    
    def enrich_person(
        self,
        email: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        organization_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Enrich person data from email or LinkedIn URL.
        
        Provide either email OR linkedin_url for best results.
        """
        data = {}
        if email:
            data["email"] = email
        if linkedin_url:
            data["linkedin_url"] = linkedin_url
        if first_name:
            data["first_name"] = first_name
        if last_name:
            data["last_name"] = last_name
        if organization_name:
            data["organization_name"] = organization_name
            
        if not data:
            raise ValueError("Must provide email, linkedin_url, or name + company")
            
        return self._post("people/match", data)
    
    def search_companies(
        self,
        q_keywords: Optional[str] = None,
        organization_industry_tag_ids: Optional[List[str]] = None,
        organization_num_employees_range: Optional[str] = None,
        organization_locations: Optional[List[str]] = None,
        per_page: int = 25,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        Search for companies in Apollo's database.
        
        Args:
            q_keywords: General search keywords
            organization_industry_tag_ids: Industry tag IDs
            organization_num_employees_range: e.g. "1-10", "11-50", "51-200", etc.
            organization_locations: City/country locations
            per_page: Results per page (max 100)
            page: Page number
        """
        data = {"per_page": per_page, "page": page}
        
        if q_keywords:
            data["q_keywords"] = q_keywords
        if organization_industry_tag_ids:
            data["organization_industry_tag_ids"] = organization_industry_tag_ids
        if organization_num_employees_range:
            data["organization_num_employees_range"] = organization_num_employees_range
        if organization_locations:
            data["organization_locations"] = organization_locations
            
        return self._post("mixed_companies/search", data)
    
    def enrich_company(
        self,
        domain: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Enrich company data from domain or name.
        
        Provide either domain OR name for best results.
        """
        data = {}
        if domain:
            data["domain"] = domain
        if name:
            data["name"] = name
            
        if not data:
            raise ValueError("Must provide domain or name")
            
        return self._post("organizations/enrich", data)


if __name__ == "__main__":
    # Simple test
    client = ApolloClient()
    print("Apollo client initialized successfully")
