/**
 * Opens the evidence modal on the HLArepo detail page. Each evidence ID link
 * loads its evidence page into the modal's body with HTMX, and this opens the
 * modal once the content is in. Esc, the background, or the close button closes
 * it, and focus goes back to the link. The modal lives in
 * repo/partials/evidence_modal.html.
 */
(() => {
  let opener = null;

  const modal = () => document.getElementById("evidence-modal");

  const close = () => {
    const element = modal();
    if (!element?.classList.contains("is-active")) return;
    element.classList.remove("is-active");
    document.documentElement.classList.remove("is-clipped");
    opener?.focus();
    opener = null;
  };

  document.addEventListener("htmx:afterSwap", (event) => {
    const body = event.detail.target;
    if (body?.id !== "evidence-modal-body") return;
    opener = event.detail.requestConfig?.elt ?? null;
    document.getElementById("evidence-modal-title").textContent =
      opener?.dataset.evidenceModalTitle ?? "";
    modal().classList.add("is-active");
    document.documentElement.classList.add("is-clipped");
    body.scrollTop = 0;
    body.focus();
  });

  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    if (event.target.closest("[data-evidence-modal-close]")) close();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") close();
  });
})();
