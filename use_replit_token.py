import requests
import sys
from typing import Optional

def test_replit_auth(token: str) -> Optional[dict]:
    """Test Replit authentication using the provided token."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "X-Requested-With": "replit"
    }
    
    # Test authentication by getting user info
    try:
        response = requests.get(
            "https://replit.com/graphql",
            headers=headers,
            json={
                "query": """
                    query CurrentUser {
                        currentUser {
                            username
                            displayName
                        }
                    }
                """
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Authentication failed (Status code: {response.status_code})")
            print(f"Response: {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"Error making request: {e}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python use_replit_token.py <token>")
        print("You can generate a token using the web interface")
        sys.exit(1)
    
    token = sys.argv[1]
    print("Testing Replit authentication...")
    result = test_replit_auth(token)
    
    if result:
        try:
            user_data = result["data"]["currentUser"]
            print("\nAuthentication successful! ✨")
            print(f"Logged in as: {user_data['displayName']} (@{user_data['username']})")
        except KeyError:
            print("Error: Unexpected response format")
            print(f"Response: {result}")

if __name__ == "__main__":
    main()
