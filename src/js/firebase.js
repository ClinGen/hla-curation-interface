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

/**
 * Extracts the value of a specified query parameter from a given URL.
 * @param {string} paramName The name of the query parameter to extract.
 * @param {string} urlString The URL string to parse. Defaults to current window's URL.
 * @returns {string | null} The extracted parameter value, or null if not found.
 */
function extractQueryParameterPath(
  paramName,
  urlString = window.location.href,
) {
  try {
    const url = new URL(urlString);
    const params = new URLSearchParams(url.search);
    if (params.has(paramName)) {
      return params.get(paramName);
    }
    return null;
  } catch (error) {
    message.error("Oops, something went wrong trying to parse the URL.");
    return null;
  }
}

/**
 * Redirects the user to the next page or the home page.
 */
function redirect() {
  const next = extractQueryParameterPath("next");
  if (next) {
    window.location.replace(next);
  } else {
    window.location.replace("/");
  }
}

/**
 * Gets the user's ID token from the OAuth provider.
 * @param providerString {string} The provider: google.com or microsoft.com.
 * @returns {Promise<string>} The user's ID token.
 */
async function getIdTokenFromProvider(providerString) {
  const provider = new OAuthProvider(providerString);
  const auth = getAuth(app);
  const result = await signInWithPopup(auth, provider);
  return await result.user.getIdToken();
}

/**
 * Allows a user to sign in or log in using an OAuth provider.
 * @param providerString {string} The provider: google.com or microsoft.com.
 * @returns {Promise<void>}
 */
async function continueWithProvider(providerString) {
  try {
    const idToken = await getIdTokenFromProvider(providerString);
    const data = await verifyIdToken(idToken);
    if (data.valid) {
      redirect();
    } else {
      message.error(data.message);
    }
  } catch (error) {
    let errorMessage = "Oops, something went wrong. ";
    errorMessage += "Please try again later.";
    message.error(errorMessage);
  }
}

/**
 * Gets the Django cross-site request forgery (CSRF) token to send to the backend.
 * @returns {string}
 */
function getCsrfToken() {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];
}

/**
 * Verifies the user's ID on the backend.
 * @param idToken {string}
 * @returns {Promise<any>}
 */
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

/**
 * Gets the user's ID token from Firebase when they sign up with email and password.
 * @returns {Promise<string>}
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
  return await userCredential.user.getIdToken();
}

/**
 * Signs the user up using email and password.
 * @returns {Promise<void>}
 */
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
      redirect();
    } else {
      message.error(data.message);
    }
  } catch (error) {
    let errorMessage = "Oops, something went wrong trying to sign you up.";
    errorMessage += " Please try again later.";
    message.error(errorMessage);
  }
}

/**
 * Signs the user up using Google as an OAuth provider.
 * @returns {Promise<void>}
 */
async function signUpWithGoogle() {
  await continueWithProvider("google.com");
}

/**
 * Signs the user up using Microsoft as an OAuth provider.
 * @returns {Promise<void>}
 */
async function signUpWithMicrosoft() {
  await continueWithProvider("microsoft.com");
}

/**
 * Attaches event listeners for the signup buttons.
 */
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

/**
 * Gets the user's ID token from Firebase when they log in with email and password.
 * @returns {Promise<string>}
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
  return await userCredential.user.getIdToken();
}

/**
 * Logs the user in with email and password.
 * @returns {Promise<void>}
 */
async function logInWithEmail() {
  try {
    const idToken = await getIdTokenFromEmailLogIn();
    const data = await verifyIdToken(idToken);
    if (data.valid) {
      redirect();
    } else {
      message.error(data.message);
    }
  } catch (error) {
    let errorMessage = "Oops, something went wrong trying to log you in.";
    errorMessage += " Please check your information and try again.";
    message.error(errorMessage);
  }
}

/**
 * Signs the user up using Google as an OAuth provider.
 * @returns {Promise<void>}
 */
async function logInWithGoogle() {
  await continueWithProvider("google.com");
}

/**
 * Signs the user up using Google as an OAuth provider.
 * @returns {Promise<void>}
 */
async function logInWithMicrosoft() {
  await continueWithProvider("microsoft.com");
}

/**
 * Attaches event listeners for the login buttons.
 */
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

/**
 * Logs the user out using Firebase on the frontend, and sends a request to log the user
 * out on the backend.
 * @returns {Promise<void>}
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

/**
 * Attaches an event listener for the logout button.
 */
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

/**
 * Resends the verification email. The verification email should be sent when the user
 * first signs up with email and password, but it can get lost/buried in the user's
 * inbox if they don't verify right away.
 * @returns {Promise<void>}
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

/**
 * Attaches an event listener for the verification email button.
 */
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

/**
 * Allows the user to edit their profile.
 * @returns {Promise<void>}
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

/**
 * Attaches an event listener for the edit profile save button.
 */
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

/**
 * Sends an email that allows the user to reset their password.
 * @returns {Promise<void>}
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

/**
 * Attaches an event listener for the reset password button.
 */
function attachResetListeners() {
  const resetPasswordAnchor = document.getElementById("reset-password-anchor");
  if (resetPasswordAnchor) {
    resetPasswordAnchor.addEventListener("click", sendResetEmail);
  }
  const resetPasswordButton = document.getElementById("reset-password-button");
  if (resetPasswordButton) {
    resetPasswordButton.addEventListener("click", sendResetEmail);
  }
}

document.addEventListener("DOMContentLoaded", attachResetListeners);
document.addEventListener("htmx:load", attachResetListeners);
