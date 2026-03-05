from fastapi import APIRouter, HTTPException, Depends
from supabase import create_client, Client
from supabase.lib.client_options import SyncClientOptions
from supabase_auth.errors import AuthApiError
import httpx
from core.config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_VERIFY_SSL
from domain.auth.schemas import SendOTPRequest, SendOTPResponse, VerifyOTPRequest, AuthResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_supabase_client() -> Client:
    """Get Supabase client instance with SSL configuration"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(
            status_code=500,
            detail="Supabase configuration is missing"
        )
    
    # Configure SSL verification for development
    # For development, set SUPABASE_VERIFY_SSL=false in .env to disable SSL verification
    if not SUPABASE_VERIFY_SSL:
        # Disable SSL verification warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Create httpx client with SSL configuration
    # This will be used by all Supabase clients (auth, postgrest, storage, etc.)
    httpx_client = httpx.Client(
        verify=SUPABASE_VERIFY_SSL,
        timeout=30.0
    )
    
    # Create SyncClientOptions with custom httpx client
    options = SyncClientOptions(
        httpx_client=httpx_client
    )
    
    # Create Supabase client with custom options
    return create_client(SUPABASE_URL, SUPABASE_KEY, options=options)

@router.post("/phone/send-otp", response_model=SendOTPResponse)
async def send_otp(
    request: SendOTPRequest,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Send OTP to phone number for authentication.
    
    Phone number should be in E.164 format (e.g., +1234567890)
    """
    try:
        # Send OTP via Supabase Auth
        response = supabase.auth.sign_in_with_otp({
            "phone": request.phone
        })
        
        return SendOTPResponse(
            message="OTP sent successfully",
            phone=request.phone
        )
    except AuthApiError as e:
        # Handle Supabase Auth API errors
        error_message = str(e)
        if "Twilio" in error_message or "Invalid From Number" in error_message:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "SMS provider configuration error",
                    "message": "Twilio is not properly configured in Supabase. Please check your Supabase Dashboard → Authentication → Providers → Phone settings.",
                    "details": "New Error: " + error_message,
                    "help": "Ensure you have: 1) Enabled Phone provider, 2) Configured Twilio Account SID, Auth Token, and Verify Service SID correctly, 3) Verified your Twilio phone number"
                }
            )
        raise HTTPException(
            status_code=400,
            detail=f"Failed to send OTP: {error_message}"
        )
    except Exception as e:
        error_message = str(e)
        if "Twilio" in error_message or "Invalid From Number" in error_message:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "SMS provider configuration error",
                    "message": "Twilio is not properly configured in Supabase. Please check your Supabase Dashboard → Authentication → Providers → Phone settings.",
                    "details": error_message
                }
            )
        raise HTTPException(
            status_code=400,
            detail=f"Failed to send OTP: {error_message}"
        )

@router.post("/phone/verify-otp", response_model=AuthResponse)
async def verify_otp(
    request: VerifyOTPRequest,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Verify OTP and authenticate user.
    
    Returns access token, refresh token, and user information.
    """
    try:
        # Verify OTP and get session
        response = supabase.auth.verify_otp({
            "phone": request.phone,
            "token": request.token,
            "type": "sms"
        })
        
        if not response.user or not response.session:
            raise HTTPException(
                status_code=401,
                detail="Invalid OTP or verification failed"
            )
        
        return AuthResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user={
                "id": response.user.id,
                "phone": response.user.phone,
                "email": response.user.email,
                "created_at": response.user.created_at,
            },
            expires_in=response.session.expires_in,
            token_type="bearer"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"OTP verification failed: {str(e)}"
        )

@router.post("/phone/resend-otp", response_model=SendOTPResponse)
async def resend_otp(
    request: SendOTPRequest,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Resend OTP to phone number.
    """
    try:
        # Resend OTP via Supabase Auth
        response = supabase.auth.sign_in_with_otp({
            "phone": request.phone
        })
        
        return SendOTPResponse(
            message="OTP resent successfully",
            phone=request.phone
        )
    except AuthApiError as e:
        # Handle Supabase Auth API errors
        error_message = str(e)
        if "Twilio" in error_message or "Invalid From Number" in error_message:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "SMS provider configuration error",
                    "message": "Twilio is not properly configured in Supabase. Please check your Supabase Dashboard → Authentication → Providers → Phone settings.",
                    "details": error_message,
                    "help": "Ensure you have: 1) Enabled Phone provider, 2) Configured Twilio Account SID, Auth Token, and Verify Service SID correctly, 3) Verified your Twilio phone number"
                }
            )
        raise HTTPException(
            status_code=400,
            detail=f"Failed to resend OTP: {error_message}"
        )
    except Exception as e:
        error_message = str(e)
        if "Twilio" in error_message or "Invalid From Number" in error_message:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "SMS provider configuration error",
                    "message": "Twilio is not properly configured in Supabase. Please check your Supabase Dashboard → Authentication → Providers → Phone settings.",
                    "details": error_message
                }
            )
        raise HTTPException(
            status_code=400,
            detail=f"Failed to resend OTP: {error_message}"
        )

