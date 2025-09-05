from fastapi import Header
import base64
from auth_functions import *


def get_auth_user(authorization: str = Header(None)) -> User:
    """
    Extract and authenticate Bearer or Basic credentials from the Authorization header.
    """
    logger = logging.getLogger(__name__)
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if authorization.startswith("Bearer "):
        token = authorization[7:]

        logger.info(f"[AUTH] Bearer token received.")

        return get_authenticated_user(token=token)
    
    elif authorization.startswith("Basic "):
        try:
            b64 = authorization[6:]
            decoded = base64.b64decode(b64).decode()
            if ':' not in decoded:
                raise ValueError("Malformed Basic Auth")
            
            username, password = decoded.split(':', 1)
            
            logger.info(f"[AUTH] Basic credentials received. user: {username}")
            
            creds = HTTPBasicCredentials(username=username, password=password)
            return get_authenticated_user(credentials=creds)
        
        except Exception as e:
            logger.warning(f"[AUTH] Basic Auth decode error: {e}")
            raise HTTPException(status_code=401, detail="Invalid Basic Auth header")
    else:
        raise HTTPException(status_code=401, detail="Unsupported Authorization type")