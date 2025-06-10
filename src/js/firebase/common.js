import { OAuthProvider, signInWithPopup } from "firebase/auth";
import { message } from "../common/message.js";
import { auth } from "./config.js";

async function getIdTokenFromProvider(providerString) {
  const provider = new OAuthProvider(providerString);
  const result = await signInWithPopup(auth, provider);
  return result.user.getIdToken();
}

export async function continueWithProvider(providerString) {
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

export function getCsrfToken() {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];
}

export async function verifyIdToken(idToken) {
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
