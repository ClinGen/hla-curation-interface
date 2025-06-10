import { createUserWithEmailAndPassword } from "firebase/auth";
import { message } from "../common/message.js";
import { continueWithProvider, verifyIdToken } from "./common.js";
import { auth } from "./config.js";

async function getIdTokenFromEmailSignUp() {
  const email = document.getElementById("email-input").value;
  const password = document.getElementById("password-input").value;
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

document.addEventListener("DOMContentLoaded", () => {
  const signUpWithEmailButton = document.getElementById(
    "continue-with-email-button",
  );
  const signUpWithGoogleButton = document.getElementById(
    "continue-with-google-button",
  );
  const signUpWithMicrosoftButton = document.getElementById(
    "continue-with-microsoft-button",
  );
  signUpWithEmailButton.addEventListener("click", signUpWithEmail);
  signUpWithGoogleButton.addEventListener("click", signUpWithGoogle);
  signUpWithMicrosoftButton.addEventListener("click", signUpWithMicrosoft);
});
