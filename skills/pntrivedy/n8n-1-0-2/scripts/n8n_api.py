#!/usr/bin/env python3
"""
n8n API client for Clawdbot
Manages workflows, executions, and credentials via n8n REST API
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List


class N8nClient:
    """n8n API client"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv('N8N_BASE_URL')
        self.api_key = api_key or os.getenv('N8N_API_KEY')
        
        if not self.api_key:
            raise ValueError("N8N_API_KEY not found in environment")
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-N8N-API-KEY': self.api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}/api/v1/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, **kwargs)
        
        try:
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            raise Exception(error_msg) from e
    
    # Workflows
    def list_workflows(self, active: bool = None) -> List[Dict]:
        """List all workflows"""
        params = {}
        if active is not None:
            params['active'] = str(active).lower()
        return self._request('GET', 'workflows', params=params)
    
    def get_workflow(self, workflow_id: str) -> Dict:
        """Get workflow details"""
        return self._request('GET', f'workflows/{workflow_id}')
    
    def create_workflow(self, workflow_data: Dict) -> Dict:
        """Create new workflow"""
        return self._request('POST', 'workflows', json=workflow_data)
    
    def update_workflow(self, workflow_id: str, workflow_data: Dict) -> Dict:
        """Update existing workflow"""
        return self._request('PATCH', f'workflows/{workflow_id}', json=workflow_data)
    
    def delete_workflow(self, workflow_id: str) -> Dict:
        """Delete workflow"""
        return self._request('DELETE', f'workflows/{workflow_id}')
    
    def activate_workflow(self, workflow_id: str) -> Dict:
        """Activate workflow"""
        return self._request('PATCH', f'workflows/{workflow_id}', json={'active': True})
    
    def deactivate_workflow(self, workflow_id: str) -> Dict:
        """Deactivate workflow"""
        return self._request('PATCH', f'workflows/{workflow_id}', json={'active': False})
    
    # Executions
    def list_executions(self, workflow_id: str = None, limit: int = 20) -> List[Dict]:
        """List workflow executions"""
        params = {'limit': limit}
        if workflow_id:
            params['workflowId'] = workflow_id
        return self._request('GET', 'executions', params=params)
    
    def get_execution(self, execution_id: str) -> Dict:
        """Get execution details"""
        return self._request('GET', f'executions/{execution_id}')
    
    def delete_execution(self, execution_id: str) -> Dict:
        """Delete execution"""
        return self._request('DELETE', f'executions/{execution_id}')
    
    # Manual execution
    def execute_workflow(self, workflow_id: str, data: Dict = None) -> Dict:
        """Manually trigger workflow execution"""
        payload = {'workflowId': workflow_id}
        if data:
            payload['data'] = data
        return self._request('POST', f'workflows/{workflow_id}/execute', json=payload)


def main():
    parser = argparse.ArgumentParser(description='n8n API Client')
    parser.add_argument('action', choices=[
        'list-workflows', 'get-workflow', 'activate', 'deactivate',
        'list-executions', 'get-execution', 'execute'
    ])
    parser.add_argument('--id', help='Workflow or execution ID')
    parser.add_argument('--active', type=lambda x: x.lower() == 'true', help='Filter by active status')
    parser.add_argument('--limit', type=int, default=20, help='Limit results')
    parser.add_argument('--data', help='JSON data for execution')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    try:
        client = N8nClient()
        result = None
        
        if args.action == 'list-workflows':
            result = client.list_workflows(active=args.active)
        elif args.action == 'get-workflow':
            if not args.id:
                raise ValueError("--id required for get-workflow")
            result = client.get_workflow(args.id)
        elif args.action == 'activate':
            if not args.id:
                raise ValueError("--id required for activate")
            result = client.activate_workflow(args.id)
        elif args.action == 'deactivate':
            if not args.id:
                raise ValueError("--id required for deactivate")
            result = client.deactivate_workflow(args.id)
        elif args.action == 'list-executions':
            result = client.list_executions(workflow_id=args.id, limit=args.limit)
        elif args.action == 'get-execution':
            if not args.id:
                raise ValueError("--id required for get-execution")
            result = client.get_execution(args.id)
        elif args.action == 'execute':
            if not args.id:
                raise ValueError("--id required for execute")
            data = json.loads(args.data) if args.data else None
            result = client.execute_workflow(args.id, data=data)
        
        # Output
        if args.pretty:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
