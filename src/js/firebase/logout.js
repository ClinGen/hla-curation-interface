import { signOut } from "firebase/auth";
import { getCsrfToken } from "./common.js";
import { auth } from "./config.js";

async function logOut() {
  try {
    console.log("Logging out...");
    await signOut(auth);
    const url = "/firebase/logout";
    const options = {
      headers: {
        "X-CSRFToken": getCsrfToken(),
      },
    };
    await fetch(url, options);
  } catch (error) {
    let errorMessage = "Something went wrong trying to log you out.\n\n";
    errorMessage += `Error Code:\n${error.code}\n\n`;
    errorMessage += `Error Message:\n${error.message}`;
    window.alert(errorMessage);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const logOutButton = document.getElementById("log-out-button");
  logOutButton.addEventListener("click", logOut);
});
