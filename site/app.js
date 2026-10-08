// Street Kit docs: renders manifest.json and the top of CHANGELOG.md. No build step.
(() => {
  "use strict";

  const GAMES = { "tip-the-can": "Tip the Can", "kerby": "Kerby" };
  const KINDS = [
    ["elevation", "Front elevations", "Straight-on, cut out on transparent. Stack them, tile them, put them on the map."],
    ["decal", "Decals", "Seen from directly above. Lay them on pavements and roads."],
    ["texture", "Tiling textures", "Seamless, seen from directly above."],
    ["fx", "Effects", "Particle and glow textures."],
    ["font", "Fonts", "Shared typefaces, with their licences."],
  ];

  // Chalk sketches for paintings that don't exist yet (viewBox 0 0 120 90).
  const SKETCH = {
    house: "M15 80V42H105V80M10 44L35 18H85L110 44M60 42V80M26 50h18v12H26zM76 50h18v12H76zM48 62h8v18h-8zM64 62h8v18h-8zM40 18V10h7v8M74 18V10h7v8",
    terrace: "M5 80V40H115V80M2 42L14 24H106L118 42M42 40V80M78 40V80M12 48h16v10H12zM50 48h16v10H50zM86 48h16v10H86zM30 62h7v18h-7zM66 62h7v18h-7zM102 62h7v18h-7zM40 24V16h6v8M76 24V16h6v8",
    bungalow: "M18 80V50H102V80M12 52L36 30H84L108 52M28 58h24v13H28zM70 58h11v22H70z",
    roofline: "M0 72L12 52H32L44 72L56 52H76L88 72L100 52H120M20 52V40h7v12M62 52V40h7v12M104 52V40h7v12M0 80H120",
    wall: "M18 80V58H112V80M18 69H112M34 58V69M52 58V69M70 58V69M88 58V69M106 58V69M26 69V80M44 69V80M62 69V80M80 69V80M98 69V80M6 80V50h12v30H6zM4 50h16",
    hedge: "M6 80V58Q12 44 22 54Q30 40 40 52Q50 40 60 52Q70 40 80 52Q90 40 100 52Q110 44 114 58V80ZM20 62q4-4 8 0M52 60q4-4 8 0M86 62q4-4 8 0",
    fence: "M8 80V36M24 80V34M40 80V36M56 80V34M72 80V36M88 80V34M104 80V36M4 46H110M4 68H110",
    gate: "M20 80V32M100 80V32M17 32h6M97 32h6M28 76V44H92V76ZM28 44L92 76M44 44V76M60 44V76M76 44V76",
    lamp: "M70 86V20M70 22Q70 10 54 10M44 8h20l-4 6H48zM48 20l-8 22M58 20l6 22M64 86H76",
    garage: "M4 80V34H116V80M9 40h31v40M45 40h31v40M81 40h31v40M9 50h31M9 60h31M45 50h31M45 60h31M81 50h31M81 60h31",
    tree: "M60 84V52M60 62L48 52M60 58L72 48M30 38a30 24 0 1 0 60 0a30 24 0 1 0 -60 0M52 84h16",
    van: "M8 72V40H72L88 54H110V72ZM72 40V54H88M18 46h44v14H18zM24 72a8 8 0 1 0 16 0a8 8 0 1 0 -16 0M86 72a8 8 0 1 0 16 0a8 8 0 1 0 -16 0M36 40l6-14l6 14",
    shop: "M10 80V28H110V80M10 40H110M14 30h92v8H14zM18 48h40v22H18zM66 48h18v32H66zM92 48h14v22H92z",
    decals: "M10 82V64h18v18zM10 64V46h18v18M28 46h18v18H28zM46 64h18v18H46zM74 70a16 10 0 1 0 32 0a16 10 0 1 0 -32 0M78 16h28v20H78zM85 16v20M92 16v20M99 16v20",
  };

  const $ = (s, el = document) => el.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const state = { status: "all", assets: [] };

  // ---- light toggle (also drives the street at the top) ----
  const setLight = (light) => {
    document.body.dataset.light = light;
    document.querySelectorAll("[data-light]").forEach((b) => {
      if (b.tagName === "BUTTON") b.setAttribute("aria-pressed", String(b.dataset.light === light));
    });
    try { localStorage.setItem("sk-light", light); } catch (_) { /* storage blocked */ }
  };
  document.querySelectorAll("button[data-light]").forEach((b) => b.addEventListener("click", () => setLight(b.dataset.light)));
  try { const saved = localStorage.getItem("sk-light"); if (saved === "dusk" || saved === "golden") setLight(saved); } catch (_) { /* ignore */ }

  // ---- status filter ----
  document.querySelectorAll("button[data-status]").forEach((b) => b.addEventListener("click", () => {
    state.status = b.dataset.status;
    document.querySelectorAll("button[data-status]").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    renderGroups();
  }));

  const sketchSvg = (key) => `<svg viewBox="0 0 120 90" aria-hidden="true"><path d="${SKETCH[key] || SKETCH.house}"/></svg>`;
  const gameTags = (a) => (a.used_by || []).map((g) => `<span class="game ${esc(g)}">${esc(GAMES[g] || g)}</span>`).join("");
  const isImg = (o) => o.size && /\.(png|webp|jpe?g|svg)$/i.test(o.path || "");
  const firstImage = (a) => (a.outputs || []).find(isImg);

  const preview = (a, big = false) => {
    const img = firstImage(a);
    if (a.kind === "font" && a.status === "shipped") {
      return `<div class="preview specimen"><span class="sp-chalk">All free!</span><span class="sp-body">Fredoka for buttons and body</span></div>`;
    }
    if (a.status === "shipped" && img) {
      return `<div class="preview painted"><img src="${esc(img.path)}" alt="${big ? esc(a.name) : ""}" loading="lazy"></div>`;
    }
    return `<div class="preview sketch">${sketchSvg(a.sketch)}<span class="tag">not painted yet</span></div>`;
  };

  const meta = (a) => {
    const bits = [];
    const imgOuts = (a.outputs || []).filter((o) => /\.(png|webp|jpe?g|svg)$/i.test(o.path || ""));
    const painted = imgOuts.filter((o) => o.size).length;
    if (a.status === "shipped") {
      bits.push(a.since ? `Since v${esc(a.since)}` : "Painted");
      if (painted < imgOuts.length) bits.push(`${painted} of ${imgOuts.length} painted`);
    } else bits.push("Planned");
    const v = (a.variants || []).filter((x) => x !== "tileable");
    if (v.length) bits.push(v.map(esc).join(", "));
    if ((a.variants || []).includes("tileable")) bits.push("tiles");
    return bits.join("; ");
  };

  function renderGroups() {
    const host = $("#groups");
    const list = state.assets.filter((a) => state.status === "all" || a.status === state.status);
    if (!list.length) {
      host.innerHTML = `<p class="empty">${state.status === "shipped"
        ? "Nothing painted yet. The first batch is the semi, the terrace, the bungalow and the roofline."
        : "Nothing here. Add assets to manifest.json to plan them."}</p>`;
      return;
    }
    host.innerHTML = KINDS.map(([kind, title, blurb]) => {
      const items = list.filter((a) => a.kind === kind);
      if (!items.length) return "";
      return `<div class="group"><h3>${title}</h3><p>${blurb}</p><ul class="grid">${items.map((a) => {
        const i = state.assets.indexOf(a);
        const tilt = ((i * 37) % 7 - 3) * 0.45;
        return `<li><button type="button" class="polaroid" style="--tilt:${tilt.toFixed(2)}deg" data-id="${esc(a.id)}" aria-haspopup="dialog">
          ${preview(a)}
          <span class="caption"><span class="name">${esc(a.name)}</span><span class="meta">${meta(a)}</span>
          <span class="games">${gameTags(a)}</span></span></button></li>`;
      }).join("")}</ul></div>`;
    }).join("");
    host.querySelectorAll(".polaroid").forEach((b) => b.addEventListener("click", () => openDetail(b.dataset.id)));
  }

  function copyButton(text, label) {
    return `<button type="button" class="copy" data-copy="${esc(text)}">${label}</button>`;
  }
  function wireCopies(root) {
    root.querySelectorAll("[data-copy]").forEach((b) => b.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(b.dataset.copy); b.dataset.done = "true"; b.textContent = "Copied"; }
      catch (_) { b.textContent = "Select and copy"; }
    }));
  }

  function openDetail(id) {
    const a = state.assets.find((x) => x.id === id);
    if (!a) return;
    const outs = a.outputs || [];
    const imgs = outs.filter(isImg);
    const previews = a.status === "shipped" && imgs.length
      ? `<div class="d-previews">${imgs.map((o) => `<figure><div class="preview painted"><img src="${esc(o.path)}" alt="${esc(o.variant || a.name)}"></div><figcaption>${esc(o.variant || o.path.split("/").pop())}</figcaption></figure>`).join("")}</div>`
      : `<div class="d-previews"><figure>${preview(a, true)}</figure></div>`;
    const uses = (a.used_by || []).map((g) => `<div><span class="game ${esc(g)}">${esc(GAMES[g] || g)}</span><div>${esc((a.uses || {})[g] || "")}</div></div>`).join("");
    const files = outs.length ? `<table class="d-files"><thead><tr><th>${a.status === "shipped" ? "File" : "Will be saved as"}</th><th>${a.status === "shipped" ? "Size" : "Width"}</th><th>Anchor</th></tr></thead><tbody>${outs.map((o) => {
      const res = `res://addons/street_kit/${o.path}`;
      return `<tr><td><code>${esc(o.path)}</code>${copyButton(res, "Copy res:// path")}</td><td>${o.size ? esc(o.size.join(" × ")) + " px" : o.width ? esc(o.width) + " px" : ""}</td><td>${esc(o.anchor || "")}</td></tr>`;
    }).join("")}</tbody></table>` : `<p class="d-note">No files yet. Variants planned: ${esc((a.variants || []).join(", ") || "one")}.</p>`;
    const sc = a.spritecook || {};
    const scBlock = sc.asset_id || sc.prompt ? `<details><summary>SpriteCook source</summary>
      ${sc.asset_id ? `<p>Asset <code>${esc(sc.asset_id)}</code>${copyButton(sc.asset_id, "Copy id")}</p>` : ""}
      ${sc.prompt ? `<pre>${esc(sc.prompt)}</pre>` : ""}</details>` : "";
    $("#d-body").innerHTML = `<h2 id="d-title">${esc(a.name)}</h2>
      <p class="d-status">${meta(a)}</p>${previews}<div class="d-uses">${uses}</div>${files}${scBlock}
      ${a.notes ? `<p class="d-note">${esc(a.notes)}</p>` : ""}`;
    wireCopies($("#d-body"));
    $("#detail").showModal();
  }
  $("#detail").addEventListener("click", (e) => { if (e.target.id === "detail") e.target.close(); });

  function renderPalette(pal) {
    $("#swatches").innerHTML = (pal || []).map((p) => `<li><button type="button" class="swatch" data-copy="${esc(p.hex)}" style="--c:${esc(p.hex)}">
      <span class="chipcolour"></span><span class="n">${esc(p.name)}</span><span class="h">${esc(p.hex)}</span><span class="u">${esc(p.use)}</span></button></li>`).join("");
    $("#swatches").querySelectorAll(".swatch").forEach((b) => b.addEventListener("click", async () => {
      const h = b.querySelector(".h");
      try { await navigator.clipboard.writeText(b.dataset.copy); h.textContent = `${b.dataset.copy} copied`; setTimeout(() => (h.textContent = b.dataset.copy), 1400); }
      catch (_) { /* clipboard blocked */ }
    }));
  }

  async function loadRelease() {
    const el = $("#release");
    try {
      const txt = await (await fetch("CHANGELOG.md", { cache: "no-cache" })).text();
      const m = txt.match(/^## \[(\d+\.\d+\.\d+)\]/m);
      el.innerHTML = m
        ? `Latest release <a href="https://github.com/danbhala/street-kit/releases/tag/v${m[1]}">v${m[1]}</a>. <a href="https://github.com/danbhala/street-kit/releases/latest/download/street-kit.zip">Download the zip</a>`
        : `<a href="https://github.com/danbhala/street-kit">See the repo</a>`;
    } catch (_) { el.innerHTML = `<a href="https://github.com/danbhala/street-kit/releases">See releases</a>`; }
  }

  async function load() {
    try {
      const m = await (await fetch("manifest.json", { cache: "no-cache" })).json();
      state.assets = m.assets || [];
      const shipped = state.assets.filter((a) => a.status === "shipped").length;
      const planned = state.assets.length - shipped;
      $("#count").textContent = `${shipped} painted, ${planned} planned`;
      renderGroups();
      renderPalette(m.palette);
    } catch (e) {
      $("#groups").innerHTML = `<p class="empty">Couldn't load manifest.json. Check it's valid JSON and published with the site.</p>`;
    }
  }

  loadRelease();
  load();
})();
