const API_BASE = "http://127.0.0.1:5000";

        function showModal(id, title = "", desc = "") {
            document.getElementById('overlay').classList.add('active');
            document.getElementById(id).classList.add('active');
            if(title) document.getElementById('loadingTitle').innerText = title;
            if(desc) document.getElementById('loadingDesc').innerText = desc;
        }

        function hideModals() {
            document.getElementById('overlay').classList.remove('active');
            document.querySelectorAll('.modal').forEach(m => m.classList.remove('active'));
        }

        function showError(msg) {
            hideModals();
            document.getElementById('errorText').innerText = msg;
            showModal('errorModal');
        }

        function base64urlToBuffer(base64url) {
            const padding = '='.repeat((4 - (base64url.length % 4)) % 4);
            const base64 = (base64url + padding).replace(/-/g, '+').replace(/_/g, '/');
            const raw = window.atob(base64);
            const buffer = new Uint8Array(raw.length);
            for (let i = 0; i < raw.length; i++) buffer[i] = raw.charCodeAt(i);
            return buffer.buffer;
        }

        function bufferToBase64url(buffer) {
            const bytes = new Uint8Array(buffer);
            let binary = '';
            for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
            return window.btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
        }

        async function startBiometricLogin(method) {
            const username = document.getElementById("username").value.trim();
            if (!username) return showError("Please enter your username first.");

            showModal('loadingModal', 'Authenticating...', 'Please follow your device prompt.');

            try {
                // 1. Get login challenge based on username
                const startRes = await fetch(`${API_BASE}/webauthn/login/start`, {
                    method: 'POST', 
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ username: username })
                });
                const startData = await startRes.json();
                if (!startRes.ok) throw new Error(startData.message || "Failed to initiate login.");

                // 2. Prepare binary objects for navigator API
                const publicKey = startData.options.publicKey;
                publicKey.challenge = base64urlToBuffer(publicKey.challenge);
                if (publicKey.allowCredentials) {
                    for (let cred of publicKey.allowCredentials) {
                        cred.id = base64urlToBuffer(cred.id);
                    }
                }

                // 3. Trigger Hardware Scan
                const assertion = await navigator.credentials.get({ publicKey: publicKey });

                // 4. Format securely for Python WebAuthn library
                const formattedAssertion = {
                    id: assertion.id,
                    rawId: bufferToBase64url(assertion.rawId),
                    type: assertion.type,
                    response: {
                        authenticatorData: bufferToBase64url(assertion.response.authenticatorData),
                        clientDataJSON: bufferToBase64url(assertion.response.clientDataJSON),
                        signature: bufferToBase64url(assertion.response.signature),
                        userHandle: assertion.response.userHandle ? bufferToBase64url(assertion.response.userHandle) : null
                    }
                };

                // 5. Verify cryptographically with backend
                const finishRes = await fetch(`${API_BASE}/webauthn/login/finish`, {
                    method: 'POST', 
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ username: username, credential: formattedAssertion })
                });
                
                const finishData = await finishRes.json();
                if (!finishRes.ok) throw new Error(finishData.message);

                hideModals();
                showModal('successModal');
                
                // Redirect on success
                setTimeout(() => window.location.href = "index.html", 1500);

            } catch (err) {
                showError(err.message);
            }
        }

        function backToMethods() {
            document.getElementById('otpView').classList.add('hidden');
            document.getElementById('methodView').classList.remove('hidden');
            document.getElementById('otpCode').value = '';
        }

        async function requestOTP() {
            const username = document.getElementById("username").value.trim();
            if (!username) return showError("Please enter your username to receive an OTP.");

            showModal('loadingModal', 'Sending OTP...', 'Locating your email securely.');

            try {
                // Backend expects username, looks up email, and sends OTP
                const res = await fetch(`${API_BASE}/otp/send`, {
                    method: 'POST', 
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ username: username })
                });
                const data = await res.json();
                
                if (!res.ok) throw new Error(data.message || "Failed to send OTP.");

                hideModals();
                
                // Switch UI Views
                document.getElementById('methodView').classList.add('hidden');
                document.getElementById('otpView').classList.remove('hidden');
                
                // Display masked email to user
                if (data.email) {
                    document.getElementById('displayEmail').innerText = data.email;
                    document.getElementById('emailDisplayBox').classList.remove('hidden');
                }

                setTimeout(() => document.getElementById('otpCode').focus(), 100);

            } catch (err) {
                showError(err.message);
            }
        }

        async function verifyOTP() {
            const username = document.getElementById("username").value.trim();
            const otpCode = document.getElementById("otpCode").value.trim();

            if (otpCode.length !== 6) return showError("Please enter the full 6-digit OTP code.");

            showModal('loadingModal', 'Verifying...', 'Checking secure code.');

            try {
                // Verify OTP with Backend
                const res = await fetch(`${API_BASE}/otp/verify`, {
                    method: 'POST', 
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ username: username, otp: otpCode })
                });
                const data = await res.json();
                
                if (!res.ok) throw new Error(data.message || "Invalid or expired OTP code.");

                hideModals();
                showModal('successModal');
                
                // Redirect on success
                setTimeout(() => window.location.href = "index.html", 1500);

            } catch (err) {
                showError(err.message);
            }
        }
