import { signOut } from "firebase/auth";
import { getAuth } from "firebase/auth";
import { message } from "../common/message.js";
import { getCsrfToken } from "./common.js";
import { app } from "./config.js";

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

document.addEventListener("DOMContentLoaded", () => {
  const logOutButton = document.getElementById("log-out-button");
  logOutButton.addEventListener("click", logOut);
});
