import { signInWithEmailAndPassword } from "firebase/auth";
import { continueWithProvider, verifyIdToken } from "./common.js";
import { auth } from "./config.js";

async function getIdTokenFromEmailLogIn() {
  const email = document.getElementById("email-input").value;
  const password = document.getElementById("password-input").value;
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
      window.alert(data.message);
    }
  } catch (error) {
    let errorMessage = "Something went wrong trying to log you in.\n\n";
    errorMessage += `Error Code:\n${error.code}\n\n`;
    errorMessage += `Error Message:\n${error.message}`;
    window.alert(errorMessage);
  }
}

async function logInWithGoogle() {
  await continueWithProvider("google.com");
}

async function logInWithMicrosoft() {
  await continueWithProvider("microsoft.com");
}

document.addEventListener("DOMContentLoaded", () => {
  const logInWithEmailButton = document.getElementById(
    "continue-with-email-button",
  );
  const logInWithGoogleButton = document.getElementById(
    "continue-with-google-button",
  );
  const logInWithMicrosoftButton = document.getElementById(
    "continue-with-microsoft-button",
  );
  logInWithEmailButton.addEventListener("click", logInWithEmail);
  logInWithGoogleButton.addEventListener("click", logInWithGoogle);
  logInWithMicrosoftButton.addEventListener("click", logInWithMicrosoft);
});
