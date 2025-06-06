import { createUserWithEmailAndPassword } from "firebase/auth";
import { continueWithProvider, verifyIdToken } from "./common.js";
import { auth } from "./config.js";

//======================================================================================
// Sign-Up Functions
//======================================================================================

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
      window.alert(data.message);
    }
  } catch (error) {
    let errorMessage = "Something went wrong trying to log you in.\n\n";
    errorMessage += `Error Code:\n${error.code}\n\n`;
    errorMessage += `Error Message:\n${error.message}`;
    window.alert(errorMessage);
  }
}

async function signUpWithGoogle() {
  await continueWithProvider("google.com");
}

async function signUpWithMicrosoft() {
  await continueWithProvider("microsoft.com");
}

//======================================================================================
// Elements
//======================================================================================

const signUpWithEmailButton = document.getElementById(
  "continue-with-email-button",
);
const signUpWithGoogleButton = document.getElementById(
  "continue-with-google-button",
);
const signUpWithMicrosoftButton = document.getElementById(
  "continue-with-microsoft-button",
);

//======================================================================================
// Event Listeners
//======================================================================================

signUpWithEmailButton.addEventListener("click", signUpWithEmail);
signUpWithGoogleButton.addEventListener("click", signUpWithGoogle);
signUpWithMicrosoftButton.addEventListener("click", signUpWithMicrosoft);
