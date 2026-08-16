const API_BASE_URL = "http://127.0.0.1:5000";

const API = {

    register: `${API_BASE_URL}/auth/register`,

    registerStart: `${API_BASE_URL}/webauthn/register/start`,

    registerFinish: `${API_BASE_URL}/webauthn/register/finish`,

    loginStart: `${API_BASE_URL}/webauthn/login/start`,

    loginFinish: `${API_BASE_URL}/webauthn/login/finish`,

    sendOTP: `${API_BASE_URL}/otp/send`,

    verifyOTP: `${API_BASE_URL}/otp/verify`
};