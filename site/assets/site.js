(() => {
  // Menu mobile
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open);
    });
  }

  // Vidéos YouTube : chargées seulement au clic (page plus rapide, pas de cookies avant lecture)
  document.querySelectorAll(".yt").forEach((btn) => {
    btn.addEventListener("click", () => {
      const f = document.createElement("iframe");
      f.className = "yt-frame";
      f.src = `https://www.youtube-nocookie.com/embed/${btn.dataset.id}?autoplay=1&rel=0`;
      f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      f.allowFullscreen = true;
      f.title = btn.getAttribute("aria-label") || "Video";
      btn.replaceWith(f);
    });
  });

  // Visionneuse d'images
  const links = [...document.querySelectorAll("a.lb")];
  if (!links.length) return;
  const svg = (d) => `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${d}" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  const box = document.createElement("div");
  box.className = "lightbox";
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-modal", "true");
  box.innerHTML = `<img alt=""><p class="lb-cap"></p>
    <button class="lb-close" aria-label="Close">${svg("M6 6l12 12M18 6 6 18")}</button>
    <button class="lb-prev" aria-label="Previous">${svg("M15 6l-6 6 6 6")}</button>
    <button class="lb-next" aria-label="Next">${svg("M9 6l6 6-6 6")}</button>`;
  document.body.appendChild(box);
  const img = box.querySelector("img"), cap = box.querySelector(".lb-cap");
  let i = 0, last = null;
  const show = (n) => {
    i = (n + links.length) % links.length;
    img.src = links[i].href;
    img.alt = links[i].dataset.caption || "";
    cap.textContent = links[i].dataset.caption || "";
    new Image().src = links[(i + 1) % links.length].href;
  };
  const open = (n) => { last = document.activeElement; show(n); box.classList.add("open"); document.body.style.overflow = "hidden"; box.querySelector(".lb-close").focus(); };
  const close = () => { box.classList.remove("open"); document.body.style.overflow = ""; img.src = ""; last && last.focus(); };
  links.forEach((a, n) => a.addEventListener("click", (e) => { e.preventDefault(); open(n); }));
  box.querySelector(".lb-close").onclick = close;
  box.querySelector(".lb-prev").onclick = () => show(i - 1);
  box.querySelector(".lb-next").onclick = () => show(i + 1);
  box.addEventListener("click", (e) => { if (e.target === box) close(); });
  document.addEventListener("keydown", (e) => {
    if (!box.classList.contains("open")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") show(i - 1);
    if (e.key === "ArrowRight") show(i + 1);
  });
  let x0 = null;
  box.addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; }, { passive: true });
  box.addEventListener("touchend", (e) => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 50) show(i + (dx < 0 ? 1 : -1));
    x0 = null;
  });
})();
