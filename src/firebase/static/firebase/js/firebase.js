import {initializeApp} from "https://www.gstatic.com/firebasejs/11.8.1/firebase-app.js";
import {
    getAuth,
    GoogleAuthProvider,
    signInWithPopup,
} from "https://www.gstatic.com/firebasejs/11.8.1/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyD_TLzPJT3IxX59b_7raOyLka11kLYGYg0",
    authDomain: "som-clingen-projects.firebaseapp.com",
    projectId: "som-clingen-projects",
    storageBucket: "som-clingen-projects.firebasestorage.app",
    messagingSenderId: "653902215137",
    appId: "1:653902215137:web:d054a272e88ab9ca2644a0",
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

function getCsrfToken() {
    return document.cookie
        .split("; ")
        .find((row) => row.startsWith("csrftoken="))
        ?.split("=")[1];
}

async function loginWithGoogle() {
    const provider = new GoogleAuthProvider();
    try {
        const result = await signInWithPopup(auth, provider);
        const idToken = await result.user.getIdToken();
        const response = await fetch("/firebase/auth", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify({
                id_token: idToken,
            }),
        });
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                window.alert("Login with Google successful.");
            }
        }
    } catch (error) {
        let errorMessage =
            "Something went wrong trying to log you in with Google.\n\n";
        errorMessage += `Error Code:\n${error.code}\n\n`;
        errorMessage += `Error Message:\n${error.message}`;
        window.alert(errorMessage);
    }
}

const loginWithGoogleButton = document.getElementById(
    "login-with-google-button",
);
loginWithGoogleButton.addEventListener("click", loginWithGoogle);
