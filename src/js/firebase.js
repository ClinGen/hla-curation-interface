/**
 * Enables signup, login, logout via Google's Firebase service. Also handles email
 * verification, user profile management, and password resets.
 */

import { initializeApp } from "firebase/app";
import {
  OAuthProvider,
  createUserWithEmailAndPassword,
  getAuth,
  sendEmailVerification,
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  updateProfile,
} from "firebase/auth";
import { message } from "./message.js";

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
Common Functions
========================================================================================
*/

async function getIdTokenFromProvider(providerString) {
  const provider = new OAuthProvider(providerString);
  const auth = getAuth(app);
  const result = await signInWithPopup(auth, provider);
  return await result.user.getIdToken();
}

async function continueWithProvider(providerString) {
  try {
    const idToken = await getIdTokenFromProvider(providerString);
    const data = await verifyIdToken(idToken);
    if (data.valid) {
      window.location.href = "/";
    } else {
      message.error(data.message);
    }
  } catch (error) {
    let errorMessage = "Oops, something went wrong. ";
    errorMessage += "Please try again later.";
    message.error(errorMessage);
  }
}

function getCsrfToken() {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];
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
Signup
========================================================================================
*/

async function getIdTokenFromEmailSignUp() {
  const email = document.getElementById("email-input").value;
  const password = document.getElementById("password-input").value;
  const auth = getAuth(app);
  const userCredential = await createUserWithEmailAndPassword(
    auth,
    email,
    password,
  );
  return userCredential.user.getIdToken();
}

async function signUpWithEmail() {
  try {
    const idToken = await getIdTokenFromEmailSignUp();
    const auth = getAuth(app);
    const user = auth.currentUser;
    if (user) {
      await sendEmailVerification(user);
    }
    const data = await verifyIdToken(idToken);
    if (data.valid) {
      window.location.href = "/";
    } else {
      message.error(data.message);
    }
  } catch (error) {
    let errorMessage = "Oops, something went wrong trying to sign you up.";
    errorMessage += " Please try again later.";
    message.error(errorMessage);
  }
}

async function signUpWithGoogle() {
  await continueWithProvider("google.com");
}

async function signUpWithMicrosoft() {
  await continueWithProvider("microsoft.com");
}

function attachSignUpListener() {
  const signUpWithEmailButton = document.getElementById(
    "signup-with-email-button",
  );
  const signUpWithGoogleButton = document.getElementById(
    "signup-with-google-button",
  );
  const signUpWithMicrosoftButton = document.getElementById(
    "signup-with-microsoft-button",
  );
  if (signUpWithEmailButton) {
    signUpWithEmailButton.addEventListener("click", signUpWithEmail);
  }
  if (signUpWithGoogleButton) {
    signUpWithGoogleButton.addEventListener("click", signUpWithGoogle);
  }
  if (signUpWithMicrosoftButton) {
    signUpWithMicrosoftButton.addEventListener("click", signUpWithMicrosoft);
  }
}

document.addEventListener("DOMContentLoaded", attachSignUpListener);
document.addEventListener("htmx:load", attachSignUpListener);

/*
========================================================================================
Login
========================================================================================
*/

async function getIdTokenFromEmailLogIn() {
  const email = document.getElementById("email-input").value;
  const password = document.getElementById("password-input").value;
  const auth = getAuth(app);
  const userCredential = await signInWithEmailAndPassword(
    auth,
    email,
    password,
  );
  return userCredential.user.getIdToken();
}

async function logInWithEmail() {
  try {
    const idToken = await getIdTokenFromEmailLogIn();
    const data = await verifyIdToken(idToken);
    if (data.valid) {
      window.location.href = "/";
    } else {
      message.error(data.message);
    }
  } catch (error) {
    let errorMessage = "Oops, something went wrong trying to log you in.";
    errorMessage += " Please check your information and try again.";
    message.error(errorMessage);
  }
}

async function logInWithGoogle() {
  await continueWithProvider("google.com");
}

async function logInWithMicrosoft() {
  await continueWithProvider("microsoft.com");
}

function attachLogInListeners() {
  const logInWithEmailButton = document.getElementById(
    "login-with-email-button",
  );
  const logInWithGoogleButton = document.getElementById(
    "login-with-google-button",
  );
  const logInWithMicrosoftButton = document.getElementById(
    "login-with-microsoft-button",
  );
  if (logInWithEmailButton) {
    logInWithEmailButton.addEventListener("click", logInWithEmail);
  }
  if (logInWithGoogleButton) {
    logInWithGoogleButton.addEventListener("click", logInWithGoogle);
  }
  if (logInWithMicrosoftButton) {
    logInWithMicrosoftButton.addEventListener("click", logInWithMicrosoft);
  }
}

document.addEventListener("DOMContentLoaded", attachLogInListeners);
document.addEventListener("htmx:load", attachLogInListeners);

/*
========================================================================================
Logout
========================================================================================
*/

async function logOut() {
  try {
    const auth = getAuth(app);
    await signOut(auth);
    const url = "/firebase/logout";
    const options = {
      headers: {
        "X-CSRFToken": getCsrfToken(),
      },
    };
    await fetch(url, options);
  } catch (error) {
    let errorMessage = "Oops, something went wrong trying to log you out.";
    errorMessage += " Please try again later.";
    message.error(errorMessage);
  }
}

function attachLogOutListener() {
  const logOutButton = document.getElementById("log-out-button");
  if (logOutButton) {
    logOutButton.addEventListener("click", logOut);
  }
}

document.addEventListener("DOMContentLoaded", attachLogOutListener);
document.addEventListener("htmx:load", attachLogOutListener);

/*
========================================================================================
Email Verification
========================================================================================
*/

async function resendVerificationEmail() {
  const auth = getAuth(app);
  await auth.authStateReady();
  const user = auth.currentUser;
  if (user && !user.emailVerified) {
    try {
      await sendEmailVerification(user);
      const successMessage =
        "Verification email sent. Please check your inbox." +
        " Click the link in the verification email, then log out." +
        " The next time you log in, you should see that your email is verified.";
      message.success(successMessage);
    } catch (error) {
      let errorMessage =
        "Oops, something went wrong trying to send the verification email.";
      errorMessage += " Please try again later.";
      message.error(errorMessage);
    }
  } else {
    let errorMessage =
      "Oops, something went wrong trying to send the verification email.";
    errorMessage += " Please log out, log back in, and try again.";
    message.error(errorMessage);
  }
}

function attachVerificationListener() {
  const resendVerificationEmailButton = document.getElementById(
    "resend-verification-email-button",
  );
  if (resendVerificationEmailButton) {
    resendVerificationEmailButton.addEventListener(
      "click",
      resendVerificationEmail,
    );
  }
}

document.addEventListener("DOMContentLoaded", attachVerificationListener);
document.addEventListener("htmx:load", attachVerificationListener);

/*
========================================================================================
User Profile Management
========================================================================================
*/

async function editUserProfile() {
  try {
    const displayNameInput = document.getElementById("display-name-input");
    const newDisplayName = displayNameInput.value.trim();
    const photoUrlInput = document.getElementById("photo-url-input");
    const newPhotoUrl = photoUrlInput.value.trim();
    const auth = getAuth(app);
    await auth.authStateReady();
    const user = auth.currentUser;
    const displayNameChanged = user.displayName !== newDisplayName;
    const photoUrlChanged = user.photoURL !== newPhotoUrl;
    if (displayNameChanged || photoUrlChanged) {
      await updateProfile(user, {
        displayName: displayNameChanged ? newDisplayName : user.displayName,
        photoURL: photoUrlChanged ? newPhotoUrl : user.photoURL,
      });
      message.success(
        "Profile updated successfully!" +
          " Please log out and log back in to see your changes.",
      );
    } else {
      message.warning(
        "The profile info you entered is the same as what we have on file.",
      );
    }
  } catch (error) {
    message.error(
      "Oops, something went wrong trying to update your display name." +
        " Please try again later.",
    );
  }
}

function attachSaveProfileListener() {
  const saveProfileButton = document.getElementById("save-profile-button");
  if (saveProfileButton) {
    saveProfileButton.addEventListener("click", editUserProfile);
  }
}

document.addEventListener("DOMContentLoaded", attachSaveProfileListener);
document.addEventListener("htmx:load", attachSaveProfileListener);

/*
========================================================================================
Password Reset
========================================================================================
*/

async function sendResetEmail() {
  try {
    const auth = getAuth(app);
    await auth.authStateReady();
    const user = auth.currentUser;
    await sendPasswordResetEmail(auth, user.email);
    message.success("Password reset email sent. Please check your inbox.");
  } catch (error) {
    message.error(
      "Oops, something went wrong trying to send a password reset email." +
        " Please try again later",
    );
  }
}

function attachResetListener() {
  const resetPasswordButton = document.getElementById("reset-password-button");
  if (resetPasswordButton) {
    resetPasswordButton.addEventListener("click", sendResetEmail);
  }
}

document.addEventListener("DOMContentLoaded", attachResetListener);
document.addEventListener("htmx:load", attachResetListener);
