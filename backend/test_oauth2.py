#!/usr/bin/env python3
"""
Simple test script to check what's causing the 422 error with OAuth2PasswordRequestForm
"""

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()

@app.post("/test-oauth2")
async def test_oauth2_form(form_data: OAuth2PasswordRequestForm = Depends()):
    """Test endpoint to see what OAuth2PasswordRequestForm receives"""
    return {
        "username": form_data.username,
        "password": "***" if form_data.password else None,
        "client_id": getattr(form_data, 'client_id', 'not_provided'),
        "client_secret": "***" if getattr(form_data, 'client_secret', None) else 'not_provided',
        "scopes": getattr(form_data, 'scopes', []),
        "grant_type": getattr(form_data, 'grant_type', 'not_provided')
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
