/**
 * Creates and inserts an article HTML element styled the same way we style our backend
 * Django messages.
 * @param class_ The class of the message. See the Bulma docs for more info.
 * @param title The title of the message.
 * @param body The body of the message.
 * @param icon The icon to display next to the message's title.
 * @private
 */
function _displayMessage(class_, title, body, icon) {
  const container = document.getElementById("message-container");

  if (container) {
    const articleDiv = document.createElement("div");
    articleDiv.classList.add("block");
    articleDiv.classList.add("mt-4");

    const article = document.createElement("article");
    article.classList.add("message");
    article.classList.add(`is-${class_}`);

    const headerDiv = document.createElement("div");
    headerDiv.classList.add("message-header");

    const titleP = document.createElement("p");
    const iconSpan = document.createElement("span");
    iconSpan.classList.add("icon", "mr-1");
    const iconI = document.createElement("i");
    iconI.classList.add("bi", `bi-${icon}`);
    iconSpan.appendChild(iconI);
    titleP.appendChild(iconSpan);
    titleP.appendChild(document.createTextNode(title));

    const deleteButton = document.createElement("button");
    deleteButton.classList.add("delete");
    deleteButton.setAttribute("aria-label", "delete");
    deleteButton.addEventListener("click", () => {
      article.remove();
    });

    headerDiv.appendChild(titleP);
    headerDiv.appendChild(deleteButton);

    const bodyDiv = document.createElement("div");
    bodyDiv.classList.add("message-body");
    bodyDiv.innerHTML = body;

    article.appendChild(headerDiv);
    article.appendChild(bodyDiv);

    articleDiv.appendChild(article);

    container.appendChild(articleDiv);
  }
}

/**
 * Displays a message to the user. Uses the same styling as the backend messages.
 */
export const message = {
  debug: (messageBody) => {
    _displayMessage("debug", "Debug", messageBody, "bug");
  },
  info: (messageBody) => {
    _displayMessage("info", "Info", messageBody, "info-square");
  },
  success: (messageBody) => {
    _displayMessage("success", "Success", messageBody, "star");
  },
  warning: (messageBody) => {
    _displayMessage("warning", "Warning", messageBody, "exclamation-triangle");
  },
  error: (messageBody) => {
    _displayMessage("danger", "Error", messageBody, "exclamation-octagon");
  },
};
