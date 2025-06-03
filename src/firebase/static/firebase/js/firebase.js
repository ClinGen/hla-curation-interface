/**
 * Configures Firebase and Firebase UI.
 */

import { initializeApp } from "https://www.gstatic.com/firebasejs/11.8.1/firebase-app.js";

const firebaseConfig = {
    apiKey: "AIzaSyD_TLzPJT3IxX59b_7raOyLka11kLYGYg0",
    authDomain: "som-clingen-projects.firebaseapp.com",
    projectId: "som-clingen-projects",
    storageBucket: "som-clingen-projects.firebasestorage.app",
    messagingSenderId: "653902215137",
    appId: "1:653902215137:web:d054a272e88ab9ca2644a0",
};
initializeApp(firebaseConfig);

const ui = new firebaseui.auth.AuthUI(firebase.auth());
const uiConfig = {
    signInSuccessUrl: "/home",
    signInOptions: [firebase.auth.GoogleAuthProvider.PROVIDER_ID],
};
ui.start("#firebaseui-auth-container", uiConfig);
