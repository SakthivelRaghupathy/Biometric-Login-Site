# Biometric Login Site

> A passwordless authentication system that uses **WebAuthn-based biometric authentication** with **email OTP fallback**.

BioSecure is a secure authentication web application designed to eliminate traditional password-based login. Users can register an account and authenticate using device-supported biometrics such as **fingerprint or facial recognition** through the WebAuthn standard.

If biometric authentication is unavailable or fails, users can use a **time-limited email OTP** as the fallback authentication method.

---

## ✨ Features

* 🔐 **Passwordless authentication**
* 👆 **Fingerprint authentication** through WebAuthn
* 🙂 **Face / device biometric authentication** through WebAuthn
* 📧 **Email OTP fallback**
* ⏱️ **Time-limited OTP verification**
* 🗄️ **MongoDB-based user and credential storage**
* 🛡️ **WebAuthn challenge-based authentication**
* 🔑 **Public-key credential storage**
* 🚫 **No traditional password storage**
* 🌐 REST API-based backend
* 🎨 Dedicated biometric registration UI
* 📱 Responsive authentication interface
* ⚡ Flask-based backend architecture

---

## 🧠 How BioSecure Works

BioSecure follows a passwordless authentication flow.

```text
                    ┌──────────────────────┐
                    │      User visits     │
                    │      BioSecure       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Enter Username     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  WebAuthn Biometric  │
                    │ Authentication       │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐        ┌─────────────────┐
        │ Fingerprint /   │        │ Authentication  │
        │ Face succeeds   │        │ unavailable     │
        └────────┬────────┘        └────────┬────────┘
                 │                          │
                 ▼                          ▼
        ┌─────────────────┐        ┌─────────────────┐
        │ Login successful│        │ Email OTP       │
        └─────────────────┘        │ verification    │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │ Login successful│
                                    └─────────────────┘
```

---

## 🔑 Authentication Architecture

### Primary Authentication — WebAuthn

BioSecure uses the WebAuthn/FIDO2 authentication model.

During registration:

1. User provides a username and email.
2. Backend creates a unique WebAuthn challenge.
3. Browser requests a credential from the user's authenticator.
4. The operating system/browser may request:

   * Fingerprint
   * Face recognition
   * Device PIN/passcode
   * Security key
5. The authenticator creates a public/private key pair.
6. The private key remains protected by the authenticator.
7. The public credential information is sent to the backend.
8. The backend stores the credential information in MongoDB.

During login:

1. User enters their username.
2. Backend generates a fresh authentication challenge.
3. Browser requests the user's registered WebAuthn credential.
4. User verifies themselves using their device authenticator.
5. The authenticator signs the challenge.
6. Backend verifies the authentication response.
7. Authentication succeeds only if the credential and cryptographic response are valid.

---

## 📧 OTP Fallback

BioSecure provides email OTP as a fallback when biometric authentication cannot be completed.

The OTP system:

* Generates a 6-digit OTP.
* Stores the OTP temporarily.
* Associates the OTP with the user's email.
* Sends the OTP through email.
* Uses an expiration period.
* Deletes the OTP after successful verification.
* Rejects invalid or expired OTPs.

Example flow:

```text
Username
   │
   ▼
Find user
   │
   ▼
Generate OTP
   │
   ▼
Store OTP temporarily
   │
   ▼
Send OTP through email
   │
   ▼
User enters OTP
   │
   ▼
Verify OTP + expiration
   │
   ├── Valid ──────► Authentication successful
   │
   └── Invalid ────► Authentication rejected
```

---

# ⚙️ Technology Stack

### Frontend

| Technology             | Purpose                                 |
| ---------------------- | --------------------------------------- |
| HTML5                  | Application structure                   |
| CSS3                   | UI and responsive design                |
| JavaScript             | Authentication and WebAuthn interaction |
| Web Authentication API | Browser biometric authentication        |

### Backend

| Technology | Purpose                     |
| ---------- | --------------------------- |
| Python     | Backend programming         |
| Flask      | REST API server             |
| Pydantic   | Request validation          |
| WebAuthn   | Passwordless authentication |
| PyMongo    | MongoDB communication       |
| SMTP       | OTP email delivery          |

### Database

**MongoDB**

MongoDB stores:

* User accounts
* Email addresses
* WebAuthn credential information
* Public keys
* Credential IDs
* Authentication challenges
* Temporary OTP records
---

# 🔒 Security Design

BioSecure is designed around the principle of **passwordless authentication**.

### WebAuthn Security

WebAuthn uses asymmetric cryptography:

```text
Authenticator
      │
      ├── Private Key
      │      └── Remains protected on device
      │
      └── Public Key
             │
             ▼
          Backend
```

The backend does **not** need to store the user's biometric information itself.

The biometric verification is performed by the user's device/authenticator, while the server verifies the resulting cryptographic authentication response.

### OTP Security

OTP records are:

* Randomly generated
* Time-limited
* Associated with the user's account/email
* Deleted after successful verification
* Replaced when a new OTP is generated

---

# 🌐 Browser Requirements

WebAuthn requires a browser that supports the Web Authentication API.

Modern versions of browsers such as:

* Google Chrome
* Microsoft Edge
* Mozilla Firefox
* Safari

support WebAuthn.

Biometric availability depends on the user's operating system, hardware, browser, and configured authenticator.

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd BioSecure
```

---

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file inside the backend directory.

Example:

```env
MONGO_URI=your_mongodb_connection_string
DATABASE_NAME=biometric_login

SECRET_KEY=your_secret_key

SENDER_EMAIL=your_email@example.com
SENDER_PASSWORD=your_email_app_password

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587

OTP_EXPIRY_SECONDS=300
```

> Never commit `.env` or email credentials to GitHub.

Add this to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
```

---

# ▶️ Run the Backend

From the backend directory:

```bash
python main.py
```

The Flask server will start locally.

Example:

```text
http://127.0.0.1:5000
```

---

# 🖥️ Run the Frontend

Open the frontend using a local development server.

For example, with VS Code Live Server:

```text
frontend/index.html
```

or:

```text
frontend/register.html
```

For WebAuthn development, use a proper secure context such as **HTTPS or localhost** rather than relying on arbitrary `file://` URLs.

---

# 🧪 Testing

The backend APIs can be tested using:

* Postman
* Thunder Client
* Browser frontend

Recommended testing sequence:

```text
1. Register user
       ↓
2. Start WebAuthn registration
       ↓
3. Complete biometric registration
       ↓
4. Verify credential was stored
       ↓
5. Start WebAuthn login
       ↓
6. Complete biometric authentication
       ↓
7. Verify successful login
```

OTP fallback:

```text
1. Send OTP
       ↓
2. Receive email
       ↓
3. Enter OTP
       ↓
4. Verify OTP
       ↓
5. Authentication successful
```

# 🛡️ Important Security Considerations

For production deployment, the following should be configured properly:

* HTTPS
* Secure cookies
* Appropriate WebAuthn RP ID
* Correct WebAuthn origin
* Secure challenge storage
* Challenge expiration
* Credential counter verification where applicable
* Rate limiting
* OTP attempt limits
* OTP resend limits
* Input validation
* Secure email credentials
* Environment-based secrets
* MongoDB access restrictions
* CORS restrictions
* Authentication session/token management
* Logging without exposing sensitive authentication data

---

# 🎯 Project Goals

BioSecure was designed with three main goals:

### 1. Passwordless Authentication

Replace traditional password authentication with modern WebAuthn-based authentication.

### 2. User-Friendly Biometrics

Provide a simple interface where users can authenticate using device-supported biometric methods.

### 3. Reliable Fallback

Provide email OTP authentication when biometric authentication cannot be completed.

---

# 🔮 Future Improvements

Potential future improvements include:

* JWT/session-based authenticated dashboard
* Multiple WebAuthn credentials per user
* Credential management and revocation
* Passkey support
* Device management
* Login activity history
* Rate limiting
* Account recovery workflow
* Security event logging
* Redis-based challenge/session storage
* Docker deployment
* HTTPS production deployment
* Automated testing
* CI/CD pipeline
* Production monitoring

---

# 🤝 Contributing

Contributions are welcome.

```text
Fork
  ↓
Create feature branch
  ↓
Make changes
  ↓
Test
  ↓
Commit
  ↓
Push
  ↓
Create Pull Request
```

Please ensure that authentication and security-related changes are thoroughly tested before submitting a pull request.

---

# 📄 License

This project can be distributed under the license specified by the repository owner.

---

# 👨‍💻 Project

**BioSecure — Passwordless Biometric Authentication System**

Built with:

**Python • Flask • MongoDB • WebAuthn • JavaScript • HTML • CSS**

> **BioSecure — Authenticate without passwords.**
'''
---
# 👤 Author
*SAKTHIVEL R*

>view on GitHub:SakthivelRaghupathy

