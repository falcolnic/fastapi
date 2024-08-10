# import base64
# import io
# import secrets
# from typing import Optional

# from src.database import Base, engine, SessionLocal
# import src.models as models
# import src.schemas as schemas
# from sqlalchemy.orm import Session

# import qrcode
# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.responses import StreamingResponse
# from pyotp import TOTP


# Base.metadata.create_all(engine)
# def get_session():
#     session = SessionLocal()
#     try:
#         yield session
#     finally:
#         session.close()
        
# router=APIRouter(
#     prefix='/two-auth',
#     tags=['two-factor-ai']
# )


# class TwoFactorAuth:
#     def __init__(self, id: str, secret_key: str):
#         self._user_id = id
#         self._secret_key = secret_key
#         self._totp = TOTP(self._secret_key)
#         self._qr_cache: Optional[bytes] = None

#     @property
#     def totp(self) -> TOTP:
#         return self._totp

#     @property
#     def secret_key(self) -> str:
#         return self._secret_key

#     @staticmethod
#     def _generate_secret_key() -> str:
#         secret_bytes = secrets.token_bytes(20)
#         secret_key = base64.b32encode(secret_bytes).decode('utf-8')
#         return secret_key

#     @staticmethod
#     def get_or_create_secret_key(user: schemas.User, session: Session = Depends(get_session)) -> str:
#         db_user = session.query(user).filter(user.id == id).first()
#         if db_user:
#             return db_user.secret_key
#         secret_key = TwoFactorAuth._generate_secret_key()
#         session.add(models.User(id=id, secret_key=secret_key))
#         session.commit()
#         return secret_key

#     def _create_qr_code(self) -> bytes:
#         uri = self.totp.provisioning_uri(
#             name=self._user_id,
#             issuer_name='2FA',
#         )
#         img = qrcode.make(uri)
#         img_byte_array = io.BytesIO()
#         img.save(img_byte_array, format='PNG')
#         img_byte_array.seek(0)
#         return img_byte_array.getvalue()

#     @property
#     def qr_code(self) -> bytes:
#         if self._qr_cache is None:
#             self._qr_cache = self._create_qr_code()
#         return self._qr_cache

#     def verify_totp_code(self, totp_code: str) -> bool:
#         return self.totp.verify(totp_code)





# def get_two_factor_auth(id: str, session: Session = Depends(get_session)) -> TwoFactorAuth:
#     secret_key = TwoFactorAuth.get_or_create_secret_key(session, id)
#     return TwoFactorAuth(id, secret_key)


# @router.post('/enable-2fa/{id}')
# def enable_2fa(two_factor_auth: TwoFactorAuth = Depends(get_two_factor_auth)):
#     return {'secret_key': two_factor_auth.secret_key}


# @router.get('/generate-qr/{id}')
# def generate_qr(two_factor_auth: TwoFactorAuth = Depends(get_two_factor_auth)):
#     qr_code = two_factor_auth.qr_code
#     if qr_code is None:
#         raise HTTPException(status_code=404, detail='User not found')
#     return StreamingResponse(io.BytesIO(qr_code), media_type='image/png')


# @router.post('/verify-totp/{id}')
# def verify_totp(
#     totp_code: str,
#     two_factor_auth: TwoFactorAuth = Depends(get_two_factor_auth),
# ):
#     is_valid = two_factor_auth.verify_totp_code(totp_code)
#     if not is_valid:
#         raise HTTPException(status_code=400, detail='Code invalid')
#     return {'valid': is_valid}