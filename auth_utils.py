import os
import jwt
from fastapi import Request, HTTPException
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------
# 1. Load and Format the Public Key
# ---------------------------------------------------------
RAW_PUBLIC_KEY = os.getenv("CLERK_PEM_PUBLIC_KEY")

# IMPORTANT: Convert the literal "\n" strings back to actual newlines
if RAW_PUBLIC_KEY:
    PUBLIC_KEY = RAW_PUBLIC_KEY.replace("\\n", "\n")
else:
    print("⚠️ WARNING: CLERK_PEM_PUBLIC_KEY is missing in .env")
    PUBLIC_KEY = None

# ---------------------------------------------------------
# 2. The Main Auth Function
# ---------------------------------------------------------
async def get_current_user_optional(request: Request):
    """
    Checks the 'Authorization' header. 
    - If valid token: Returns user dict (with '_id' and 'email').
    - If no token or invalid: Returns None (does not block the user).
    """
    
    # 1. Get the header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None  # Guest user

    try:
        # 2. Extract token (Format: "Bearer <token>")
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            return None
        
        # 3. Verify Token using the Public Key
        # We allow a small 'leeway' for clock differences between servers
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"], leeway=10)

        # 4. Return User Info
        # We map Clerk's 'sub' (Subject ID) to our database '_id' concept
        return {
            "_id": payload.get("sub"),
            "email": payload.get("email", "")
        }

    except (jwt.ExpiredSignatureError, jwt.DecodeError, Exception) as e:
        # If token is invalid, just treat them as a guest (don't crash)
        print(f"Auth Error: {str(e)}")
        return None