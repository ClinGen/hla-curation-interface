// Shows suggestions under text inputs marked with data-suggest, which
// common/form/input/text.html adds when given a suggest_url. HTMX fetches the
// suggestions as the curator types; this file sends the typed text as q, opens
// and closes the list, and fills the input from the mouse or keyboard.

function suggestionList(input) {
	return document.getElementById(input.getAttribute("aria-controls"));
}

function suggestionItems(input) {
	return [...suggestionList(input).querySelectorAll("[role='option']")];
}

function closeSuggestions(input) {
	htmx.trigger(input, "htmx:abort"); // A late response would reopen the list.
	input.closest(".suggest").classList.remove("is-active");
	input.setAttribute("aria-expanded", "false");
	input.removeAttribute("aria-activedescendant");
	suggestionList(input).replaceChildren();
}

function highlightSuggestion(input, index) {
	const items = suggestionItems(input);
	items.forEach((item, i) => {
		const selected = i === index;
		item.classList.toggle("is-active", selected);
		item.setAttribute("aria-selected", String(selected));
		if (selected) {
			input.setAttribute("aria-activedescendant", item.id);
			item.scrollIntoView({ block: "nearest" });
		}
	});
}

function chooseSuggestion(input, item) {
	input.value = item.dataset.value;
	closeSuggestions(input);
}

document.addEventListener("htmx:configRequest", (event) => {
	const input = event.detail.elt;
	if (!input.matches("[data-suggest]")) {
		return;
	}
	for (const key of Object.keys(event.detail.parameters)) {
		delete event.detail.parameters[key];
	}
	event.detail.parameters.q = input.value;
});

document.addEventListener("htmx:afterSwap", (event) => {
	const input = document.querySelector(
		`[aria-controls='${event.detail.target.id}'][data-suggest]`,
	);
	if (!input) {
		return;
	}
	const items = suggestionItems(input);
	items.forEach((item, i) => {
		item.id = `${event.detail.target.id}-${i}`;
	});
	const open = items.length > 0 && document.activeElement === input;
	input.closest(".suggest").classList.toggle("is-active", open);
	input.setAttribute("aria-expanded", String(open));
	input.removeAttribute("aria-activedescendant");
});

document.addEventListener("keydown", (event) => {
	const input = event.target;
	if (!input.matches?.("[data-suggest]")) {
		return;
	}
	const items = suggestionItems(input);
	if (input.getAttribute("aria-expanded") !== "true" || items.length === 0) {
		return;
	}
	const current = items.findIndex((item) => item.classList.contains("is-active"));
	if (event.key === "ArrowDown") {
		event.preventDefault();
		highlightSuggestion(input, (current + 1) % items.length);
	} else if (event.key === "ArrowUp") {
		event.preventDefault();
		highlightSuggestion(input, (current - 1 + items.length) % items.length);
	} else if (event.key === "Enter" && current >= 0) {
		event.preventDefault();
		chooseSuggestion(input, items[current]);
	} else if (event.key === "Escape") {
		event.preventDefault();
		closeSuggestions(input);
	}
});

// mousedown, not click, so the choice lands before the input's blur closes the list.
document.addEventListener("mousedown", (event) => {
	const item = event.target.closest?.(".suggest [role='option']");
	if (!item) {
		return;
	}
	event.preventDefault();
	const input = item.closest(".suggest").querySelector("[data-suggest]");
	chooseSuggestion(input, item);
});

document.addEventListener("focusout", (event) => {
	if (event.target.matches?.("[data-suggest]")) {
		closeSuggestions(event.target);
	}
});
