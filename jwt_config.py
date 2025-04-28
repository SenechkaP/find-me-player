from datetime import datetime, timedelta
from jose import JWTError, jwt
from env_values import secret_key, algorithm, exp_minutes

SECRET_KEY = secret_key
ALGORITHM = algorithm


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(exp_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
