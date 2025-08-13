Backend API overview

Routes
- GET /health
- POST /auth/login/request-otp
- POST /auth/login/verify-otp
- POST /chat/
- POST /documents/upload
- POST /certificates/bonafide

Notes
- Provide `Authorization: Bearer <token>` for protected routes after OTP verification.
- Summarizer uses Hugging Face `t5-small` pipeline. For very long docs, consider upgrading to `google/pegasus-xsum` or longformer-based models and chunking.

