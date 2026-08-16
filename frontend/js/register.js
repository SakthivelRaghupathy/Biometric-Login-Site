const usernameInput = document.getElementById("username");
const loadingModal = document.getElementById("loadingModal");
const successModal = document.getElementById("successModal");
const errorModal = document.getElementById("errorModal");
const errorText = document.getElementById("errorText");

function show(el) { if (el) el.classList.remove("hidden"); }
function hide(el) { if (el) el.classList.add("hidden"); }

function base64urlToBuffer(base64url) {
    const padding = '='.repeat((4 - (base64url.length % 4)) % 4);
    const base64 = (base64url + padding).replace(/-/g, '+').replace(/_/g, '/');
    const raw = window.atob(base64);
    const buffer = new Uint8Array(raw.length);
    for (let i = 0; i < raw.length; i++) {
        buffer[i] = raw.charCodeAt(i);
    }
    return buffer.buffer;
}

function bufferToBase64url(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    const base64 = window.btoa(binary);
    return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

async function startBiometricRegistration(selectedMethod) {
    try {
        const username = usernameInput ? usernameInput.value.trim() : "";

        // Prevent Bad Request Errors (Must be at least 3 chars)
        if (username.length < 3) {
            throw new Error("Your username must be at least 3 characters long to register.");
        }

        if (loadingModal) show(loadingModal);

        // STEP 1: Request the challenge from the Python backend
        const startResponse = await fetch('http://localhost:5000/webauthn/register/start', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: username })
        });

        const startData = await startResponse.json();

        if (!startResponse.ok) {
            throw new Error(startData.message || "Failed to initiate registration challenge.");
        }

        // STEP 1.5: Unpack the nested publicKey object correctly
        const publicKey = startData.options.publicKey;

        if (!publicKey) {
             throw new Error("Backend did not return a valid publicKey object.");
        }

        // Prepare raw binary values required by the navigator API
        publicKey.challenge = base64urlToBuffer(publicKey.challenge);
        publicKey.user.id = base64urlToBuffer(publicKey.user.id);

        if (publicKey.excludeCredentials && publicKey.excludeCredentials.length > 0) {
            for (let cred of publicKey.excludeCredentials) {
                cred.id = base64urlToBuffer(cred.id);
            }
        } else {
            delete publicKey.excludeCredentials;
        }

        // STEP 2: Trigger Windows Hello / Touch ID / Face ID
        let credential;
        try {
            credential = await navigator.credentials.create({ publicKey: publicKey });
        } catch (deviceErr) {
            throw new Error(`Device biometrics aborted: ${deviceErr.message}`);
        }

        // STEP 3: Format payload perfectly for the Duo Labs webauthn library
        const formattedCredential = {
            id: credential.id,
            rawId: bufferToBase64url(credential.rawId),
            type: credential.type,
            response: {
                clientDataJSON: bufferToBase64url(credential.response.clientDataJSON),
                attestationObject: bufferToBase64url(credential.response.attestationObject),
                transports: credential.response.getTransports ? credential.response.getTransports() : []
            }
        };

        // STEP 4: Submit local cryptographic payload to backend for verification
        const finishResponse = await fetch('http://localhost:5000/webauthn/register/finish', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: username,
                method: selectedMethod, 
                credential: formattedCredential
            })
        });

        const finishData = await finishResponse.json();
        
        if (loadingModal) hide(loadingModal);

        if (!finishResponse.ok) {
            throw new Error(finishData.message || "Cryptographic signature validation failed.");
        }

        // SUCCESS! Show modal if exists, else alert
        if (successModal) {
            show(successModal);
            
            // Auto-hide the success popup and overlay after 2 seconds
            setTimeout(() => {
                hide(successModal);
                const overlay = document.getElementById("overlay");
                if (overlay) hide(overlay);
            }, 2000);
            
        } else {
            alert("Success! Biometrics registered and saved to database.");
        }

        // 1. Mark the clicked card with a Green Tick
        const targetCard = document.getElementById(selectedMethod + "Card");
        if (targetCard) {
            const pTag = targetCard.querySelector("p");
            if (pTag) {
                pTag.innerHTML = "✅ Registered";
                pTag.style.color = "#10b981"; // Emerald green color
                pTag.style.fontWeight = "bold";
            }
            targetCard.style.borderColor = "#10b981";
            targetCard.style.backgroundColor = "rgba(16, 185, 129, 0.05)";
            targetCard.style.pointerEvents = "none"; // Prevent double clicking
        }

        // Update the Status Box text
        const statusDiv = document.querySelector(".auth-grid").nextElementSibling;
        if (statusDiv && statusDiv.innerText.includes("Waiting")) {
            statusDiv.innerHTML = "<span style='color:#10b981; font-weight:bold;'>✅ Biometric verification complete! Proceed to create account.</span>";
        }

        // 2. Safely find and enable the "Create Account" button
        const allElements = document.querySelectorAll("button, div");
        let createAccountBtn = null;
        allElements.forEach(el => {
            if (el.textContent && el.textContent.trim() === "Create Account") {
                createAccountBtn = el;
            }
        });

        if (createAccountBtn) {
            // Forcefully remove disabled styles and attributes
            createAccountBtn.removeAttribute("disabled");
            createAccountBtn.style.opacity = "1";
            createAccountBtn.style.cursor = "pointer";
            createAccountBtn.style.pointerEvents = "auto";
            
            // 3. Attach the final click event to send BOTH Username and Email
            createAccountBtn.onclick = async (e) => {
                e.preventDefault();
                
                const emailInput = document.getElementById("email");
                const email = emailInput ? emailInput.value.trim() : "";

                if (!username || !email) {
                    alert("Please fill in both Username and Email to complete registration.");
                    return;
                }

                try {
                    // Final API call to save the full user profile to MongoDB!
                    const res = await fetch('http://127.0.0.1:5000/auth/register', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ username: username, email: email })
                    });
                    
                    const data = await res.json();
                    if(!res.ok) throw new Error(data.message || "Failed to create account.");
                    
                    alert("Account fully created! Redirecting to login...");
                    window.location.href = "login.html"; 
                    
                } catch(err) {
                    alert("Error creating account: " + err.message);
                }
            };
        }

    } catch (err) {
        if (loadingModal) hide(loadingModal);
        
        // Show error using your custom UI modal
        if (errorText && errorModal) {
            errorText.textContent = err.message;
            show(errorModal);
        } else {
            alert("Error: " + err.message);
        }
    }
}

const fingerprintCard = document.getElementById("fingerprintCard");
const faceCard = document.getElementById("faceCard");
const bothCard = document.getElementById("bothCard");

if (fingerprintCard) {
    fingerprintCard.onclick = () => startBiometricRegistration('fingerprint');
    fingerprintCard.style.cursor = 'pointer'; 
}

if (faceCard) {
    faceCard.onclick = () => startBiometricRegistration('face');
    faceCard.style.cursor = 'pointer';
}

if (bothCard) {
    bothCard.onclick = () => startBiometricRegistration('both');
    bothCard.style.cursor = 'pointer';
}

const closeErrorBtn = document.getElementById("closeError");
if (closeErrorBtn) {
    closeErrorBtn.onclick = () => {
        hide(errorModal);
        const overlay = document.getElementById("overlay");
        if (overlay) hide(overlay);
    };
}

// --- NEW FIX: Make the "Create Account" button work! ---
// Finds the submit button at the bottom of the form
const createAccountBtn = document.querySelector("button"); 
if (createAccountBtn) {
    createAccountBtn.onclick = async (e) => {
        e.preventDefault(); // Stop page from refreshing
        
        const username = document.getElementById("username").value.trim();
        const emailInput = document.getElementById("email");
        const email = emailInput ? emailInput.value.trim() : "user@domain.com";

        if (!username || !email) {
            alert("Please fill in both Username and Email to complete registration.");
            return;
        }

        try {
            // Send the final request to save the user profile
            const res = await fetch('http://127.0.0.1:5000/auth/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ username, email })
            });
            
            const data = await res.json();
            
            if(!res.ok) throw new Error(data.message);
            
            alert("Account fully created! Redirecting to login...");
            
            // Send the user to the login page to test their new passkey!
            window.location.href = "login.html"; 
            
        } catch(err) {
            alert("Error creating account: " + err.message);
        }
    };
}