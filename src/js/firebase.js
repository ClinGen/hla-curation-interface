import { initializeApp } from "firebase/app";
import { OAuthProvider, getAuth, signInWithPopup } from "firebase/auth";

/*
========================================================================================
Configure Firebase
========================================================================================
*/

const firebaseConfig = {
  apiKey: "AIzaSyD_TLzPJT3IxX59b_7raOyLka11kLYGYg0",
  authDomain: "som-clingen-projects.firebaseapp.com",
  projectId: "som-clingen-projects",
  storageBucket: "som-clingen-projects.firebasestorage.app",
  messagingSenderId: "653902215137",
  appId: "1:653902215137:web:d054a272e88ab9ca2644a0",
};
const app = initializeApp(firebaseConfig);

/*
========================================================================================
Helper Functions
========================================================================================
*/

function getCsrfToken() {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];
}

async function getIdToken(providerString) {
  const auth = getAuth(app);
  const provider = new OAuthProvider(providerString);
  const result = await signInWithPopup(auth, provider);
  return result.user.getIdToken();
}

async function verifyIdToken(idToken) {
  const url = "/firebase/verify";
  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify({ idToken: idToken }),
  };
  const response = await fetch(url, options);
  return await response.json();
}

/*
========================================================================================
Log-In Functions
========================================================================================
*/

async function logInWithProvider(providerString) {
  try {
    const idToken = await getIdToken(providerString);
    const data = await verifyIdToken(idToken);
    if (data.valid) {
      window.location.href = "/";
    } else {
      window.alert(data.message);
    }
  } catch (error) {
    let errorMessage = `Something went wrong trying to log you in with ${providerString}.\n\n`;
    errorMessage += `Error Code:\n${error.code}\n\n`;
    errorMessage += `Error Message:\n${error.message}`;
    window.alert(errorMessage);
  }
}

async function logInWithGoogle() {
  await logInWithProvider("google.com");
}

async function logInWithMicrosoft() {
  await logInWithProvider("microsoft.com");
}

/*
========================================================================================
Event Listeners
========================================================================================
*/

const logInWithGoogleButton = document.getElementById(
  "log-in-with-google-button",
);
logInWithGoogleButton.addEventListener("click", logInWithGoogle);

const logInWithMicrosoftButton = document.getElementById(
  "log-in-with-microsoft-button",
);
logInWithMicrosoftButton.addEventListener("click", logInWithMicrosoft);
