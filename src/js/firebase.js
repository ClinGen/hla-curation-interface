/**
 * Configures Firebase and Firebase UI.
 */

import { initializeApp } from "https://www.gstatic.com/firebasejs/11.8.1/firebase-app.js";
import {
  GoogleAuthProvider,
  getAuth,
} from "https://www.gstatic.com/firebasejs/11.8.1/firebase-auth.js";

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
const auth = getAuth(app);

/*
========================================================================================
Configure Firebase UI
========================================================================================
*/

const ui = new firebaseui.auth.AuthUI(auth);
const uiConfig = {
  signInSuccessUrl: "/home",
  signInOptions: [GoogleAuthProvider.PROVIDER_ID],
};
ui.start("#firebaseui-auth-container", uiConfig);

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

async function handleLogin(authResult) {
  try {
    const idToken = await authResult.user.getIdToken();
    const url = "/firebase/login";
    const options = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({ idToken: idToken }),
    };
    const response = await fetch(url, options);
    const data = await response.json();
    if (data.success) {
      window.location.href = "/home";
    } else {
      window.alert("Unable to log you in with Google.");
    }
  } catch (error) {
    let errorMessage =
      "Something went wrong trying to log you in with Google.\n\n";
    errorMessage += `Error Code:\n${error.code}\n\n`;
    errorMessage += `Error Message:\n${error.message}`;
    window.alert(errorMessage);
  }
}
