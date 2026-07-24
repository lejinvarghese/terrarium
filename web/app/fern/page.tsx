"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import * as THREE from "three";

/* ════════════════════════════════════════════
   FERN — FERN — fractal towns for the northern shield
   Pages: SYSTEM · SITES · ENERGY · ROBOTS
   ════════════════════════════════════════════ */

const REDUCE =
  typeof window !== "undefined" &&
  window.matchMedia &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const GLOBAL_CSS = `
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300..800&family=IBM+Plex+Mono:wght@400;500&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:#07161C}
.pf{font-family:'Bricolage Grotesque',sans-serif;color:#E8F1F2;background:#07161C;overflow-x:hidden;min-height:100vh}
.mono{font-family:'IBM Plex Mono',monospace;letter-spacing:.12em;text-transform:uppercase}
.flowHot{stroke:#F08A2C;stroke-width:4;fill:none;stroke-dasharray:10 9;animation:flow 1.5s linear infinite}
.flowCold{stroke:#6FB9C9;stroke-width:4;fill:none;stroke-dasharray:10 9;animation:flow 2.3s linear infinite}
.flowPow{stroke:#9ED9A8;stroke-width:3;fill:none;stroke-dasharray:4 7;animation:flow 1s linear infinite}
@keyframes flow{to{stroke-dashoffset:-19}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes glowP{0%,100%{opacity:.45}50%{opacity:1}}
@keyframes blink{0%,100%{opacity:.15}50%{opacity:1}}
@keyframes pulseR{0%{r:7;opacity:.8}100%{r:22;opacity:0}}
@keyframes chev{0%{transform:translateX(0);opacity:0}25%{opacity:1}100%{transform:translateX(30px);opacity:0}}
@keyframes swimS{0%{transform:translateX(0)}50%{transform:translateX(40px)}100%{transform:translateX(0)}}
@keyframes gantry{0%{transform:translateX(0)}50%{transform:translateX(56px)}100%{transform:translateX(0)}}
@keyframes haulBot{0%{transform:translateX(0)}100%{transform:translateX(150px)}}
@keyframes heroHaul{0%{transform:translateX(0)}100%{transform:translateX(300px)}}
@keyframes auroraShift{0%{transform:translateX(-4%) skewX(-3deg)}100%{transform:translateX(4%) skewX(3deg)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(26px)}to{opacity:1;transform:none}}
@keyframes growBar{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes fall{to{transform:translateY(108vh) translateX(5vw)}}
.flake{position:absolute;top:-2vh;border-radius:50%;background:rgba(235,245,248,.85);animation-name:fall;animation-timing-function:linear;animation-iteration-count:infinite}
.reveal{opacity:0;transform:translateY(26px);transition:opacity .7s ease,transform .7s ease}
.reveal.in{opacity:1;transform:none}
input[type=range]{accent-color:#F08A2C}
@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{animation:none!important;transition:none!important}
  .reveal{opacity:1!important;transform:none!important}
}`;

const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

/* logo: original FERN mark — one frond, flat silhouette, organically varied leaflets */
const FERN_D = "M137,477 L142,457 L149,437 L156,417 L164,398 L172,378 L182,360 L192,341 L202,323 L213,306 L224,289 L236,273 L248,258 L260,244 L273,231 L285,219 L298,208 L311,198 L323,190 L335,183 L348,177 L360,173 L371,170 L382,169 L393,170 L404,172 L414,177 L414,175 L404,170 L394,167 L382,166 L371,167 L359,169 L346,173 L333,179 L321,186 L308,194 L294,204 L281,215 L268,227 L256,240 L243,254 L230,269 L218,285 L206,301 L195,319 L184,337 L174,355 L164,374 L155,394 L147,414 L139,434 L133,454 L127,475 Z M140,447 L152,456 L160,455 L168,452 L175,448 L181,443 L187,437 L193,431 L198,423 L202,416 L202,416 L193,417 L185,418 L178,419 L170,420 L163,422 L156,425 L149,428 L143,433 L140,447 Z M140,447 L142,437 L139,432 L136,427 L132,423 L127,419 L122,416 L117,412 L112,408 L106,405 L106,405 L108,412 L109,418 L112,424 L114,430 L117,435 L121,440 L125,445 L130,448 L140,447 Z M147,426 L157,436 L165,436 L173,435 L180,433 L188,430 L195,426 L203,422 L209,417 L216,411 L216,411 L207,410 L199,409 L191,409 L183,409 L176,409 L168,410 L161,412 L154,415 L147,426 Z M147,426 L153,409 L150,400 L145,392 L139,385 L133,378 L126,372 L118,365 L110,359 L101,352 L101,352 L101,363 L101,374 L103,385 L106,395 L109,405 L114,414 L121,422 L129,428 L147,426 Z M156,404 L167,417 L177,417 L186,415 L195,412 L203,408 L211,402 L219,396 L226,389 L232,381 L232,381 L222,380 L213,380 L204,379 L195,380 L186,380 L178,382 L170,384 L162,389 L156,404 Z M156,404 L161,392 L159,385 L156,378 L152,372 L148,365 L143,359 L138,353 L133,347 L127,341 L127,341 L126,349 L126,358 L127,366 L129,374 L131,382 L134,389 L137,397 L143,403 L156,404 Z M165,383 L176,392 L185,391 L193,389 L201,386 L209,382 L216,376 L223,371 L230,364 L236,357 L236,357 L227,358 L218,358 L210,359 L201,360 L193,361 L186,363 L178,365 L171,369 L165,383 Z M165,383 L172,368 L170,360 L167,353 L162,346 L157,340 L152,334 L146,327 L139,321 L132,315 L132,315 L131,325 L130,334 L131,343 L132,352 L135,361 L138,369 L143,376 L149,383 L165,383 Z M176,361 L184,372 L191,373 L198,373 L206,372 L213,369 L220,366 L227,362 L233,358 L240,353 L240,353 L232,351 L224,349 L217,347 L210,346 L203,346 L196,346 L189,347 L183,349 L176,361 Z M176,361 L181,348 L178,341 L174,334 L170,328 L165,321 L160,315 L154,309 L148,303 L142,297 L142,297 L142,306 L142,315 L144,323 L146,332 L148,340 L152,347 L157,354 L163,360 L176,361 Z M188,340 L196,351 L205,352 L213,352 L222,350 L230,348 L238,344 L246,340 L254,335 L261,329 L261,329 L252,328 L243,326 L235,325 L227,325 L219,324 L211,325 L203,326 L196,328 L188,340 Z M188,340 L195,329 L194,322 L192,316 L189,311 L186,305 L182,299 L178,294 L173,288 L168,283 L168,283 L166,290 L165,298 L165,305 L165,312 L166,319 L168,326 L171,332 L175,338 L188,340 Z M200,319 L207,328 L213,329 L220,328 L226,326 L232,324 L237,321 L243,318 L248,314 L253,309 L253,309 L247,307 L240,306 L234,305 L228,305 L222,305 L216,305 L210,306 L205,309 L200,319 Z M200,319 L207,308 L206,300 L204,293 L201,286 L198,279 L194,272 L190,265 L186,258 L182,251 L182,251 L180,260 L178,268 L177,276 L177,285 L178,293 L180,301 L183,309 L187,316 L200,319 Z M213,299 L220,309 L227,311 L235,311 L243,310 L250,308 L257,305 L264,301 L271,297 L277,292 L277,292 L270,291 L262,289 L255,288 L248,287 L241,287 L234,287 L227,287 L220,289 L213,299 Z M213,299 L218,289 L217,284 L215,279 L212,274 L209,269 L205,265 L201,261 L197,256 L192,252 L192,252 L191,259 L191,265 L191,271 L192,277 L193,283 L195,289 L198,294 L202,298 L213,299 Z M227,280 L231,290 L237,292 L243,293 L249,293 L255,292 L261,291 L267,289 L273,286 L278,283 L278,283 L273,280 L267,278 L261,275 L256,274 L251,272 L245,271 L240,271 L234,272 L227,280 Z M227,280 L233,271 L233,264 L232,258 L230,252 L227,246 L225,240 L222,234 L219,227 L215,221 L215,221 L213,228 L211,235 L210,242 L209,249 L210,256 L211,263 L213,270 L216,276 L227,280 Z M241,262 L246,270 L252,271 L258,271 L264,271 L269,269 L275,267 L281,265 L286,262 L291,259 L291,259 L285,257 L280,256 L274,254 L268,253 L263,253 L258,252 L252,253 L247,254 L241,262 Z M241,262 L248,254 L249,249 L248,244 L247,239 L245,234 L243,229 L240,223 L238,218 L234,213 L234,213 L232,219 L230,224 L228,230 L227,236 L227,242 L227,247 L228,253 L231,258 L241,262 Z M256,245 L260,254 L266,256 L272,257 L278,256 L284,255 L290,253 L295,251 L301,248 L306,244 L306,244 L300,242 L295,240 L289,239 L284,237 L278,236 L273,235 L268,235 L262,236 L256,245 Z M256,245 L260,238 L260,232 L259,228 L257,223 L255,219 L253,214 L250,209 L248,205 L245,200 L245,200 L243,205 L242,211 L242,216 L242,222 L242,227 L243,232 L245,237 L248,242 L256,245 Z M271,229 L273,236 L277,238 L281,240 L285,240 L290,241 L294,240 L299,240 L303,239 L308,238 L308,238 L304,235 L300,233 L296,231 L292,229 L289,227 L285,226 L281,225 L276,225 L271,229 Z M271,229 L278,222 L278,217 L278,212 L277,207 L275,202 L273,198 L271,193 L269,188 L266,182 L266,182 L263,188 L261,193 L259,199 L258,204 L257,210 L258,215 L259,221 L261,226 L271,229 Z M286,215 L289,223 L294,226 L299,227 L304,227 L309,227 L314,226 L320,224 L325,222 L330,220 L330,220 L325,217 L320,215 L315,213 L311,211 L306,210 L302,209 L297,208 L292,208 L286,215 Z M286,215 L291,211 L292,207 L292,203 L291,199 L291,196 L290,192 L289,188 L288,184 L287,180 L287,180 L285,184 L283,188 L281,192 L280,195 L280,199 L279,203 L279,207 L281,211 L286,215 Z M301,202 L303,208 L307,210 L310,210 L314,211 L317,211 L321,211 L325,210 L328,209 L332,208 L332,208 L329,206 L325,204 L322,202 L319,201 L316,200 L313,199 L309,198 L306,198 L301,202 Z M301,202 L308,197 L309,193 L309,189 L308,184 L308,180 L307,176 L305,172 L304,167 L302,162 L302,162 L299,167 L297,171 L294,175 L293,180 L292,185 L292,189 L292,194 L294,198 L301,202 Z M316,191 L317,198 L320,201 L324,202 L327,204 L331,204 L335,205 L339,205 L343,204 L347,203 L347,203 L344,201 L341,198 L338,196 L335,194 L332,192 L329,190 L326,189 L322,188 L316,191 Z M316,191 L320,188 L321,185 L321,182 L321,179 L320,176 L320,173 L319,170 L318,166 L317,163 L317,163 L315,166 L314,169 L313,173 L312,176 L311,179 L311,182 L311,185 L312,188 L316,191 Z M332,182 L332,188 L334,190 L337,191 L340,192 L343,193 L346,194 L350,194 L353,194 L356,194 L356,194 L354,191 L352,189 L349,187 L347,185 L344,184 L342,182 L339,181 L336,180 L332,182 Z M332,182 L337,180 L339,177 L340,175 L340,172 L340,168 L340,165 L340,162 L340,159 L340,155 L340,155 L337,157 L335,160 L332,163 L330,165 L329,168 L328,172 L327,175 L327,178 L332,182 Z M347,175 L347,180 L349,181 L351,183 L353,184 L356,184 L358,185 L361,185 L363,185 L366,184 L366,184 L364,182 L362,181 L361,179 L359,177 L357,176 L355,175 L353,174 L351,173 L347,175 Z M347,175 L351,174 L352,171 L353,169 L353,167 L353,164 L354,161 L354,159 L354,156 L354,153 L354,153 L352,155 L350,157 L348,159 L347,162 L346,164 L345,167 L344,169 L344,172 L347,175 Z M361,171 L361,175 L362,177 L364,178 L366,180 L368,181 L370,182 L373,182 L375,183 L378,183 L378,183 L376,181 L375,179 L374,177 L372,175 L371,174 L369,172 L367,171 L365,170 L361,171 Z M361,171 L365,169 L366,168 L366,166 L367,164 L367,162 L367,160 L367,158 L367,156 L367,154 L367,154 L365,156 L364,157 L362,159 L361,160 L360,162 L359,164 L359,166 L359,168 L361,171 Z M376,168 L375,170 L375,172 L376,173 L377,174 L378,175 L379,176 L380,177 L382,177 L383,178 L383,178 L383,176 L382,175 L382,174 L381,172 L381,171 L380,170 L379,169 L378,168 L376,168 Z M376,168 L379,168 L380,167 L381,165 L382,164 L383,162 L383,161 L384,159 L385,157 L385,156 L385,156 L384,156 L382,157 L380,158 L379,159 L377,161 L376,162 L375,164 L374,165 L376,168 Z M389,168 L388,170 L389,171 L390,172 L390,173 L391,174 L393,175 L394,176 L395,176 L396,177 L396,177 L396,175 L395,174 L395,173 L394,172 L394,171 L393,170 L392,169 L391,168 L389,168 Z M389,168 L391,169 L392,168 L393,167 L393,167 L394,166 L394,165 L395,164 L395,163 L395,162 L395,162 L394,163 L393,163 L392,163 L391,164 L391,164 L390,165 L389,166 L389,166 L389,168 Z M402,171 L401,172 L401,172 L401,173 L401,173 L402,174 L402,174 L403,175 L403,175 L404,175 L404,175 L404,175 L404,174 L404,173 L404,173 L404,172 L404,172 L404,171 L404,171 L402,171 Z M402,171 L404,171 L404,171 L405,171 L405,170 L405,170 L406,169 L406,169 L406,168 L407,167 L407,167 L406,167 L405,167 L404,168 L404,168 L403,168 L403,168 L402,169 L402,169 L402,171 Z M411,175 L412,179 L413,180 L415,181 L417,183 L418,183 L420,184 L422,185 L425,186 L427,187 L427,187 L426,185 L425,182 L424,180 L423,178 L421,176 L419,175 L417,174 L415,173 L411,175 Z";

function FernFlake({ size = 120, opacity = 1, color = "#9ED9A8" }) {
  return (
    <svg viewBox="0 0 512 512" width={size} height={size} style={{ opacity, display: "block" }}>
      <path d={FERN_D} fill={color} />
    </svg>
  );
}

function Reveal({ children, style }) {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (es) => es.forEach((e) => e.isIntersecting && (e.target.classList.add("in"), io.unobserve(e.target))),
      { threshold: 0.12 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return <div ref={ref} className="reveal" style={style}>{children}</div>;
}

const Ref = ({ ids }) => (
  <sup className="mono" style={{ fontSize: 8, color: "#F08A2C", marginLeft: 4, letterSpacing: ".06em" }}>[{ids}]</sup>
);
function JumpChips({ items }) {
  return (
    <div style={{ maxWidth: 1150, margin: "0 auto", display: "flex", gap: 8, flexWrap: "wrap", padding: "1.4rem 5vw 0" }}>
      {items.map(([l, id]) => (
        <button key={id} className="mono"
          onClick={() => { const el = document.getElementById(id); if (el) el.scrollIntoView({ behavior: REDUCE ? "auto" : "smooth" }); }}
          style={{ fontSize: 9.5, padding: ".45rem .9rem", borderRadius: 99, cursor: "pointer", border: "1px solid #1E4751", background: "transparent", color: "#7FA8A6" }}>
          ↓ {l}
        </button>
      ))}
    </div>
  );
}
const Tag = ({ n, label }) => (
  <div className="mono" style={{ fontSize: 11, color: "#F08A2C", marginBottom: 14 }}>{n} · {label}</div>
);
const H2 = ({ children }) => (
  <h2 style={{ fontSize: "clamp(1.6rem,3.4vw,2.6rem)", fontWeight: 700 }}>{children}</h2>
);
const Sub = ({ children }) => (
  <div style={{ marginTop: 10, fontSize: ".98rem", color: "#A9C8C8", maxWidth: 640, fontWeight: 300 }}>{children}</div>
);

/* ───────────────────────── NAV ───────────────────────── */
const PAGES = ["SYSTEM", "THE BIOME", "PLACE", "CHARTER"];
function Nav({ page, setPage }) {
  return (
    <nav style={{
      position: "sticky", top: 0, zIndex: 50, display: "flex", alignItems: "center", gap: 6,
      padding: ".7rem 5vw", background: "rgba(7,22,28,.92)", backdropFilter: "blur(8px)",
      borderBottom: "1px solid #14323B", flexWrap: "wrap",
    }}>
      <div style={{ fontWeight: 750, fontSize: "1.05rem", marginRight: 14, color: "#9ED9A8" }}>FERN</div>
      {PAGES.map((p) => (
        <button key={p} onClick={() => setPage(p)} className="mono"
          style={{
            fontSize: 10, padding: ".45rem .85rem", borderRadius: 99, cursor: "pointer", border: "none",
            background: page === p ? "#F08A2C" : "transparent",
            color: page === p ? "#0B1D24" : "#7FA8A6", transition: "all .25s",
          }}>{p}</button>
      ))}
    </nav>
  );
}

/* ───────────────────────── THE BIOME SCENE (hero panorama) ───────────────────────── */
function BiomeScene() {
  const A = (a) => (REDUCE ? "none" : a);
  return (
    <svg viewBox="0 0 1200 270" preserveAspectRatio="xMidYMax meet"
      style={{ position: "absolute", bottom: 0, left: 0, width: "100%", zIndex: 2, pointerEvents: "none" }}>
      {/* snowfield */}
      <path d="M0,218 Q150,210 300,218 T600,216 T900,220 T1200,216 L1200,270 L0,270 Z" fill="#0A222B" />
      <path d="M0,218 Q150,210 300,218 T600,216 T900,220 T1200,216" stroke="#DCE9EC" strokeWidth="1.6" fill="none" opacity=".4" />

      {/* the agent mesh — the quiet layer coordinating every denizen */}
      <g opacity=".5">
        <path d="M300,72 C480,18 700,12 825,32 C950,52 1080,52 1150,82" stroke="#A78BDB" strokeWidth="1.4" fill="none" strokeDasharray="2 7" style={{ animation: REDUCE ? "none" : "flow 3.5s linear infinite" }} />
        <path d="M300,72 C400,98 510,108 620,44" stroke="#A78BDB" strokeWidth="1.2" fill="none" strokeDasharray="2 7" style={{ animation: REDUCE ? "none" : "flow 4.2s linear infinite" }} />
        <path d="M825,32 C900,20 1000,28 1030,44" stroke="#A78BDB" strokeWidth="1.2" fill="none" strokeDasharray="2 7" style={{ animation: REDUCE ? "none" : "flow 4.8s linear infinite" }} />
        {[[300, 72], [620, 44], [825, 32], [1030, 44], [1148, 80]].map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r="3.2" fill="#A78BDB" style={{ animation: REDUCE ? "none" : `glowP ${2.4 + i * 0.5}s ease-in-out infinite` }} />
        ))}
        <text x="640" y="20" className="mono" fontSize="8.5" fill="#A78BDB" textAnchor="middle">AGENTS — THE QUIET LAYER, COORDINATING EVERYTHING</text>
      </g>

      {/* wind */}
      {[[70, 158, 0], [128, 138, 1]].map(([x, y, i]) => (
        <g key={i}>
          <line x1={x} y1="218" x2={x} y2={y} stroke="#9ED9A8" strokeWidth="3" strokeLinecap="round" />
          <g style={{ transformOrigin: `${x}px ${y}px`, animation: A(`spin ${4.5 + i}s linear infinite`) }} stroke="#9ED9A8" strokeWidth="3" strokeLinecap="round" fill="none">
            <line x1={x} y1={y} x2={x} y2={y - 24} /><line x1={x} y1={y} x2={x + 20} y2={y + 12} /><line x1={x} y1={y} x2={x - 20} y2={y + 12} />
          </g>
        </g>
      ))}

      {/* data hall: servers heating the loop */}
      <rect x="230" y="150" width="140" height="68" rx="5" fill="#0C2730" stroke="#2C5763" strokeWidth="1.8" />
      {[0, 1, 2].map((r) => [0, 1, 2, 3].map((c) => (
        <rect key={r + "-" + c} x={244 + c * 30} y={160 + r * 17} width="18" height="10" rx="2" fill="#7FD8E8"
          style={{ animation: A(`glowP ${1.8 + ((r + c) % 4) * 0.5}s infinite`) }} />
      )))}
      {/* heat into the glass commons, cold return */}
      <path d="M370,184 H 505" className="flowHot" strokeWidth="3" />
      <path d="M505,206 H 370" className="flowCold" strokeWidth="2.4" opacity=".8" />

      {/* THE GLASS COMMONS — the town under one roof */}
      <g>
        <path d="M500,218 C640,64 1010,64 1150,218" fill="#7FD8E8" opacity=".055" />
        <path d="M500,218 C640,64 1010,64 1150,218" fill="none" stroke="#9ED9A8" strokeWidth="2" />
        <path d="M510,218 C645,76 1005,76 1140,218" fill="none" stroke="#9ED9A8" strokeWidth="1" opacity=".4" />
        {[[560, 156], [640, 122], [730, 102], [825, 95], [920, 102], [1010, 122], [1090, 156]].map(([x, y]) => (
          <line key={x} x1={x} y1={y} x2={x} y2="218" stroke="#2C5763" strokeWidth="1.2" opacity=".65" />
        ))}
        {/* interior pathway */}
        <line x1="540" y1="212" x2="1112" y2="212" stroke="#5E8B89" strokeWidth="1.6" strokeDasharray="2 6" opacity=".8" />
        {/* interior trees */}
        {[[600, 0], [1064, 1]].map(([x, i]) => (
          <g key={x}>
            <line x1={x} y1="218" x2={x} y2="186" stroke="#6FAF8F" strokeWidth="2.6" />
            <circle cx={x} cy="178" r="13" fill="#9ED9A8" opacity=".85" style={{ animation: REDUCE ? "none" : `glowP ${5 + i}s ease-in-out infinite` }} />
          </g>
        ))}
        {/* garden rows */}
        {[646, 666, 686, 982, 1002, 1022].map((x) => (
          <g key={x} stroke="#9ED9A8" strokeWidth="1.8" fill="none">
            <line x1={x} y1="218" x2={x} y2="205" /><path d={`M${x},208 l-4,-5 M${x},208 l4,-5`} />
          </g>
        ))}
        {/* homes inside, on low piles */}
        {[[718, 0], [880, 1]].map(([hx, i]) => (
          <g key={hx}>
            <line x1={hx + 8} y1="210" x2={hx + 8} y2="218" stroke="#5E8B89" strokeWidth="2.6" />
            <line x1={hx + 54} y1="210" x2={hx + 54} y2="218" stroke="#5E8B89" strokeWidth="2.6" />
            <rect x={hx} y="180" width="62" height="30" fill="#0C2730" stroke="#2C5763" strokeWidth="1.5" />
            <path d={`M${hx - 4},182 L${hx + 70},172 L${hx + 70},176 L${hx - 4},186 Z`} fill="#163745" />
            <rect x={hx + 8} y="188" width="34" height="11" rx="1.5" fill="#FFC97A" style={{ animation: REDUCE ? "none" : `glowP ${4 + i}s ease-in-out infinite` }} />
          </g>
        ))}
        {/* town-centre pavilion */}
        <rect x="806" y="186" width="44" height="24" fill="#0C2730" stroke="#F08A2C" strokeWidth="1.8" />
        <rect x="812" y="192" width="32" height="9" rx="1.5" fill="#F08A2C" opacity=".85" style={{ animation: REDUCE ? "none" : "glowP 3.5s ease-in-out infinite" }} />
        <line x1="828" y1="186" x2="828" y2="170" stroke="#F08A2C" strokeWidth="2" />
        <circle cx="828" cy="167" r="2.6" fill="#F08A2C" style={{ animation: REDUCE ? "none" : "blink 3s infinite" }} />
        {/* district loop branching inside */}
        <path d="M505,196 H 560 V 208" className="flowHot" strokeWidth="2" opacity=".7" />
      </g>

      {/* autonomous hauler — foreground corridor outside the glass */}
      <line x1="560" y1="240" x2="1010" y2="240" stroke="#3C5C63" strokeWidth="2" strokeDasharray="7 8" opacity=".7" />
      {[640, 740, 840, 940].map((x) => <circle key={x} cx={x} cy="231" r="2.2" fill="#FFB35C" style={{ animation: REDUCE ? "none" : "blink 2.4s infinite" }} />)}
      <g style={{ animation: REDUCE ? "none" : "heroHaul 10s linear infinite" }}>
        <rect x="566" y="229" width="28" height="12" rx="3.5" fill="#7FD8E8" />
        <circle cx="573" cy="243" r="3.8" fill="#E8F1F2" /><circle cx="586" cy="243" r="3.8" fill="#E8F1F2" />
      </g>

      {/* caption strip */}
      {[["WIND", 64], ["SERVERS HEAT…", 246], ["THE GLASS COMMONS — HOMES, GARDENS, THE SQUARE, UNDER ONE ROOF", 500], ["ROBOTS HAUL", 1086]].map(([t, x]) => (
        <text key={t} x={x} y="248" className="mono" fontSize="8" fill="#5E8B89">{t}</text>
      ))}
    </svg>
  );
}

/* ───────────────────────── HERO ───────────────────────── */
function Hero() {
  const mountRef = useRef(null);
  const [fallback, setFallback] = useState(REDUCE);
  useEffect(() => {
    if (REDUCE || !mountRef.current) return;
    const mount = mountRef.current;
    let renderer;
    try {
      const t = document.createElement("canvas");
      if (!(t.getContext("webgl") || t.getContext("experimental-webgl"))) throw 0;
      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    } catch { setFallback(true); return; }
    const scene = new THREE.Scene();
    const cam = new THREE.PerspectiveCamera(60, mount.clientWidth / mount.clientHeight, 0.1, 100);
    cam.position.z = 12;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    mount.appendChild(renderer.domElement);
    const N = 1200, pos = new Float32Array(N * 3), spd = new Float32Array(N);
    for (let i = 0; i < N; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 40; pos[i * 3 + 1] = (Math.random() - 0.5) * 26;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 18; spd[i] = 0.008 + Math.random() * 0.02;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    const mat = new THREE.PointsMaterial({ color: 0xdfeef2, size: 0.07, transparent: true, opacity: 0.8 });
    const snow = new THREE.Points(geo, mat);
    scene.add(snow);
    let raf;
    const tick = () => {
      const p = geo.attributes.position.array;
      for (let i = 0; i < N; i++) {
        p[i * 3 + 1] -= spd[i];
        p[i * 3] += Math.sin(Date.now() * 0.0004 + i) * 0.004;
        if (p[i * 3 + 1] < -13) p[i * 3 + 1] = 13;
      }
      geo.attributes.position.needsUpdate = true;
      snow.rotation.y += 0.0004;
      renderer.render(scene, cam);
      raf = requestAnimationFrame(tick);
    };
    tick();
    return () => { cancelAnimationFrame(raf); renderer.dispose(); geo.dispose(); mat.dispose(); mount.removeChild(renderer.domElement); };
  }, []);
  return (
    <header style={{ position: "relative", height: "86vh", overflow: "hidden", background: "linear-gradient(180deg,#07161C 0%,#0B2630 55%,#123845 100%)" }}>
      <div style={{
        position: "absolute", inset: "-15% -10% auto -10%", height: "70%", pointerEvents: "none", filter: "blur(20px)",
        background: "radial-gradient(55% 85% at 28% 5%,rgba(94,156,147,.5),transparent 62%),radial-gradient(45% 75% at 70% 0%,rgba(140,210,185,.32),transparent 66%)",
        animation: REDUCE ? "none" : "auroraShift 14s ease-in-out infinite alternate",
      }} />
      <div ref={mountRef} style={{ position: "absolute", inset: 0 }} />
      {fallback && !REDUCE && (
        <div style={{ position: "absolute", inset: 0, overflow: "hidden", pointerEvents: "none" }}>
          {Array.from({ length: 60 }).map((_, i) => {
            const s = 1.5 + ((i * 7) % 10) * 0.32;
            return <div key={i} className="flake" style={{ width: s, height: s, left: `${(i * 137) % 100}vw`, opacity: 0.3 + ((i * 13) % 10) * 0.05, animationDuration: `${7 + ((i * 11) % 9)}s`, animationDelay: `${-((i * 5) % 16)}s` }} />;
          })}
        </div>
      )}
      <div style={{ position: "absolute", right: "-4vw", top: "6vh", zIndex: 1, pointerEvents: "none" }}>
        <FernFlake size={Math.min(480, typeof window !== "undefined" ? window.innerWidth * 0.42 : 480)} opacity={0.14} />
      </div>
      <BiomeScene />
      <div style={{ position: "relative", zIndex: 3, height: "100%", display: "flex", flexDirection: "column", justifyContent: "flex-start", paddingTop: "11vh", padding: "11vh 6vw 0", animation: REDUCE ? "none" : "fadeUp 1.1s ease both" }}>
        <div className="mono" style={{ fontSize: 11, color: "#8FC4BC", marginBottom: 18 }}>a fractal town platform for the northern shield</div>
        <h1 style={{ fontSize: "clamp(3.4rem,12vw,9.5rem)", fontWeight: 760, lineHeight: 0.92, letterSpacing: "-.02em" }}>FERN</h1>
        <div style={{ marginTop: 18, fontSize: "clamp(1rem,2vw,1.3rem)", color: "#A9C8C8", fontWeight: 300, maxWidth: 560 }}>
          fern (n.) — fractal by nature: every leaflet a smaller frond, every frond joined at the root. The towns are the leaflets.
        </div>
        <div style={{ display: "flex", gap: "2.2rem", flexWrap: "wrap", marginTop: 34 }}>
          {[["20 MW", "servers heat the homes", "#7FD8E8"], ["10\u2076", "agents run the loop", "#A78BDB"], ["24/7", "robots take the dark", "#6FB9C9"], ["4 kinds", "animals on task", "#C9A56A"], ["2,500", "humans, just living", "#E86A8A"]].map(([v, l, c]) => (
            <div key={l}>
              <div style={{ fontSize: "1.55rem", fontWeight: 700, color: c }}>{v}</div>
              <div className="mono" style={{ fontSize: 9.5, color: "#7FA8A6" }}>{l}</div>
            </div>
          ))}
        </div>
      </div>
    </header>
  );
}

/* ───────────────────────── LOOP (self-playing) ───────────────────────── */
const STAGES = [
  { k: "POWER", big: "wind + hydro", line: "Arctic-rated wind with battery smoothing is proven at Raglan and Diavik mines; grid hydro arrives where interties exist." },
  { k: "COMPUTE", big: "20 MW", line: "Tundra air free-cools the halls most of the year — the anchor tenant that pays for everything." },
  { k: "HEAT", big: "30→70 °C", line: "Heat pumps lift server exhaust to district temperature — the Mäntsälä, Finland model, where one data hall heats over half the town." },
  { k: "TOWN", big: "0 W wasted", line: "Homes, greenhouses, char tanks drink the heat; 25 °C water returns to cool the servers." },
];
function LoopSection() {
  const [stage, setStage] = useState(REDUCE ? 3 : 0);
  const secRef = useRef(null), timer = useRef(null), inV = useRef(false);
  const restart = useCallback(() => {
    if (REDUCE) return;
    clearInterval(timer.current);
    timer.current = setInterval(() => { if (inV.current) setStage((s) => (s + 1) % 4); }, 3400);
  }, []);
  useEffect(() => {
    const io = new IntersectionObserver((es) => es.forEach((e) => (inV.current = e.isIntersecting)), { threshold: 0.25 });
    if (secRef.current) io.observe(secRef.current);
    restart();
    return () => { io.disconnect(); clearInterval(timer.current); };
  }, [restart]);
  const pick = (i) => { setStage(i); restart(); };
  const Zone = ({ n, children }) => (
    <g style={{ opacity: stage >= n ? 1 : 0.1, transition: "opacity .6s ease, filter .6s ease", filter: stage === n ? "drop-shadow(0 0 12px rgba(240,138,44,.5))" : "none" }}>{children}</g>
  );
  const anim = (a) => (REDUCE ? "none" : a);
  const live = (n) => stage >= n;
  return (
    <section ref={secRef} style={{ padding: "5.5rem 5vw", background: "#07161C" }}>
      <div style={{ maxWidth: 1150, margin: "0 auto" }}>
        <Tag n="01" label="the loop" />
        <H2>One pipe runs the town.</H2>
        <div style={{ display: "flex", gap: 10, marginTop: 22, flexWrap: "wrap" }}>
          {STAGES.map((s, i) => (
            <button key={s.k} onClick={() => pick(i)} className="mono"
              style={{
                fontSize: 10, padding: ".55rem .95rem", borderRadius: 99, cursor: "pointer",
                border: `1px solid ${i === stage ? "#F08A2C" : "#1E4751"}`,
                background: i === stage ? "#F08A2C" : "transparent",
                color: i === stage ? "#0B1D24" : i < stage ? "#F08A2C" : "#7FA8A6", transition: "all .3s",
              }}>{String(i + 1).padStart(2, "0")} {s.k}</button>
          ))}
        </div>
        <svg viewBox="0 0 1000 470" style={{ width: "100%", marginTop: 16, display: "block" }}>
          <path d="M0,396 Q120,388 240,396 T480,394 T720,398 T1000,394 L1000,470 L0,470 Z" fill="#0A222B" />
          <path d="M0,396 Q120,388 240,396 T480,394 T720,398 T1000,394" stroke="#DCE9EC" strokeWidth="2" fill="none" opacity=".5" />
          <Zone n={0}>
            <path d="M30,396 Q140,340 280,392" fill="#0D2933" />
            {[[85, 268, 0], [160, 222, 1], [235, 282, 2]].map(([x, y, i]) => (
              <g key={i}>
                <line x1={x} y1={y + 110} x2={x} y2={y} stroke="#9ED9A8" strokeWidth="4" strokeLinecap="round" />
                <g style={{ transformOrigin: `${x}px ${y}px`, animation: live(0) ? anim(`spin ${4.5 + i}s linear infinite`) : "none" }} stroke="#9ED9A8" strokeWidth="4" strokeLinecap="round" fill="none">
                  <line x1={x} y1={y} x2={x} y2={y - 42} /><line x1={x} y1={y} x2={x + 36} y2={y + 21} /><line x1={x} y1={y} x2={x - 36} y2={y + 21} />
                </g>
                <circle cx={x} cy={y} r="5" fill="#0C2730" stroke="#9ED9A8" strokeWidth="2" />
                <circle cx={x} cy={y} r="2.4" fill="#FF6B5E" style={{ animation: live(0) ? anim("blink 2.4s infinite") : "none" }} />
              </g>
            ))}
            {[300, 340].map((x) => (
              <g key={x} stroke="#5E8B89" strokeWidth="2.5"><line x1={x} y1="396" x2={x} y2="340" /><line x1={x - 9} y1="348" x2={x + 9} y2="348" /></g>
            ))}
            <path d="M262,338 C300,330 340,346 392,344" className="flowPow" style={{ animationPlayState: live(0) ? "running" : "paused" }} />
            <text x="58" y="436" className="mono" fontSize="11" fill="#9ED9A8">WIND + BATTERY · GRID HYDRO WHERE LINKED</text>
          </Zone>
          <Zone n={1}>
            <rect x="392" y="252" width="180" height="144" rx="6" fill="#0C2730" stroke="#2C5763" strokeWidth="2" />
            <rect x="386" y="244" width="192" height="12" rx="4" fill="#163745" />
            {[428, 478, 528].map((x, i) => (
              <g key={x}>
                <circle cx={x} cy="232" r="11" fill="none" stroke="#7FD8E8" strokeWidth="2" />
                <g style={{ transformOrigin: `${x}px 232px`, animation: live(1) ? anim(`spin ${1.6 + i * 0.4}s linear infinite`) : "none" }} stroke="#7FD8E8" strokeWidth="2">
                  <line x1={x - 8} y1="232" x2={x + 8} y2="232" /><line x1={x} y1="224" x2={x} y2="240" />
                </g>
                <line x1={x} y1="243" x2={x} y2="252" stroke="#2C5763" strokeWidth="3" />
              </g>
            ))}
            {[0, 1, 2].map((i) => (
              <path key={i} d="M352,300 l12,10 l-12,10" stroke="#6FB9C9" strokeWidth="3" fill="none" style={{ animation: live(1) ? anim(`chev 1.6s ${i * 0.5}s linear infinite`) : "none" }} />
            ))}
            <text x="306" y="290" className="mono" fontSize="9" fill="#6FB9C9">−30 °C AIR IN</text>
            {[268, 282, 296, 310, 324].map((y) => <line key={y} x1="398" y1={y} x2="412" y2={y} stroke="#2C5763" strokeWidth="3" />)}
            {[0, 1, 2, 3].map((r) => [0, 1, 2, 3].map((c) => (
              <rect key={r + "-" + c} x={424 + c * 34} y={268 + r * 28} width="22" height="16" rx="2" fill="#7FD8E8"
                style={{ opacity: live(1) ? 1 : 0, animation: live(1) ? anim(`glowP ${1.8 + ((r + c) % 4) * 0.5}s infinite`) : "none" }} />
            )))}
            <text x="392" y="436" className="mono" fontSize="11" fill="#7FD8E8">DATA HALLS · 20 MW · FREE-AIR ~340 D/YR</text>
          </Zone>
          <Zone n={2}>
            <path d="M572,330 H 614" className="flowHot" opacity=".55" style={{ animationPlayState: live(2) ? "running" : "paused" }} />
            <text x="566" y="318" className="mono" fontSize="9" fill="#C9772A">30 °C</text>
            <rect x="614" y="300" width="62" height="62" rx="8" fill="#0C2730" stroke="#F08A2C" strokeWidth="2.5" />
            <circle cx="645" cy="331" r="17" fill="none" stroke="#F08A2C" strokeWidth="2.5" />
            <g style={{ transformOrigin: "645px 331px", animation: live(2) ? anim("spin 2.4s linear infinite") : "none" }} stroke="#F08A2C" strokeWidth="2.5">
              <line x1="633" y1="331" x2="657" y2="331" /><line x1="645" y1="319" x2="645" y2="343" />
            </g>
            <path d="M676,331 H 712" className="flowHot" style={{ animationPlayState: live(2) ? "running" : "paused" }} />
            <path d="M712,331 H 752" className="flowHot" style={{ animationPlayState: live(2) ? "running" : "paused" }} />
            <text x="688" y="318" className="mono" fontSize="9" fill="#F08A2C">70 °C</text>
            <text x="600" y="436" className="mono" fontSize="11" fill="#F08A2C">HEAT PUMPS · 1 kW IN → 2.3 kW HEAT (COP 2.7–4 PROVEN)</text>
          </Zone>
          <Zone n={3}>
            {/* the glass commons — homes, gardens and the square under one roof */}
            <path d="M752,396 C790,168 950,168 988,396" fill="#7FD8E8" opacity=".06" />
            <path d="M752,396 C790,168 950,168 988,396" fill="none" stroke="#9ED9A8" strokeWidth="2.2" />
            <path d="M760,396 C796,180 944,180 980,396" fill="none" stroke="#9ED9A8" strokeWidth="1" opacity=".4" />
            {[[796, 270], [834, 232], [870, 224], [906, 232], [944, 270]].map(([x, y]) => (
              <line key={x} x1={x} y1={y} x2={x} y2="396" stroke="#2C5763" strokeWidth="1.2" opacity=".6" />
            ))}
            {/* home on low piles */}
            <rect x="780" y="318" width="56" height="36" fill="#10333D" stroke="#F08A2C" strokeWidth="2" />
            <path d="M776,320 L842,309 L842,314 L776,325 Z" fill="#163745" />
            <rect x="788" y="328" width="26" height="12" fill="#FFC97A" style={{ animation: live(3) ? anim("glowP 3.5s infinite") : "none" }} />
            <line x1="790" y1="354" x2="790" y2="364" stroke="#5E8B89" strokeWidth="2.4" />
            <line x1="826" y1="354" x2="826" y2="364" stroke="#5E8B89" strokeWidth="2.4" />
            {/* the square pavilion */}
            <rect x="854" y="334" width="30" height="24" fill="#10333D" stroke="#F08A2C" strokeWidth="1.8" />
            <line x1="869" y1="334" x2="869" y2="318" stroke="#F08A2C" strokeWidth="2" />
            <circle cx="869" cy="315" r="2.4" fill="#F08A2C" style={{ animation: live(3) ? anim("blink 3s infinite") : "none" }} />
            {/* gardens + a tree, warm under glass */}
            {[898, 916, 934].map((x) => (
              <g key={x} stroke="#9ED9A8" strokeWidth="2.4" fill="none">
                <line x1={x} y1="396" x2={x} y2="372" /><path d={`M${x},377 l-6,-8 M${x},377 l6,-8`} />
              </g>
            ))}
            <line x1="956" y1="396" x2="956" y2="362" stroke="#6FAF8F" strokeWidth="2.6" />
            <circle cx="956" cy="354" r="11" fill="#9ED9A8" opacity=".85" />
            {/* interior path + heat distributing inside */}
            <line x1="772" y1="388" x2="968" y2="388" stroke="#5E8B89" strokeWidth="1.5" strokeDasharray="2 6" opacity=".8" />
            <path d="M752,340 H 800 V 352" className="flowHot" strokeWidth="2.2" opacity=".8" style={{ animationPlayState: live(3) ? "running" : "paused" }} />
            <text x="704" y="150" className="mono" fontSize="10" fill="#F08A2C">THE GLASS COMMONS · HOMES + SQUARE + GARDENS · +15 °C AT −40 °C</text>
            {/* char tank at the warm end */}
            <rect x="698" y="356" width="44" height="26" rx="7" fill="#0A2530" stroke="#6FB9C9" strokeWidth="2" />
            <g style={{ animation: live(3) ? anim("swimS 7s ease-in-out infinite") : "none" }}>
              <ellipse cx="712" cy="370" rx="6" ry="3" fill="#F08A2C" /><path d="M718,370 l6,-3.5 v7 z" fill="#F08A2C" />
            </g>
            <text x="694" y="348" className="mono" fontSize="9" fill="#6FB9C9">CHAR</text>
            {/* cold return riding the utilidor home */}
            <path d="M900,410 H 500 V 398" className="flowCold" style={{ animationPlayState: live(3) ? "running" : "paused" }} />
            <text x="610" y="424" className="mono" fontSize="9" fill="#6FB9C9">25 °C RETURN → RE-COOLS SERVERS</text>
          </Zone>
        </svg>
        <div style={{ display: "flex", alignItems: "center", gap: 24, marginTop: 6, flexWrap: "wrap" }}>
          <div style={{ fontSize: "1.7rem", fontWeight: 750, color: "#F08A2C", minWidth: 160 }}>{STAGES[stage].big}</div>
          <div style={{ fontSize: ".93rem", color: "#A9C8C8", maxWidth: 600 }}>{STAGES[stage].line}</div>
        </div>
      </div>
    </section>
  );
}

/* ───────────────────────── MODULE DIAGRAM (1k→5k scaling) ───────────────────────── */
function ModuleSection() {
  const [n, setN] = useState(2);
  const cfg = [
    { pop: "1,000", halls: 1, gh: 1, homes: 2, mw: "8 MW", note: "starter frond — one hall, one commons" },
    { pop: "2,500", halls: 2, gh: 2, homes: 3, mw: "20 MW", note: "reference frond — full loop economics" },
    { pop: "5,000", halls: 3, gh: 3, homes: 5, mw: "40 MW", note: "twin frond — second utilidor ring" },
  ][n - 1];
  return (
    <section style={{ padding: "5.5rem 5vw", background: "#0A1F27" }}>
      <div style={{ maxWidth: 1150, margin: "0 auto" }}>
        <Reveal>
          <Tag n="02" label="the frond" />
          <H2>Same kit, three sizes.</H2>
          <Sub>Every component is barge- or rail-deliverable and repeats: add a hall, add a commons, link the loop. Homes, gardens and the square live inside the glass; hardened pile-homes outside keep redundancy. Slide to scale.</Sub>
        </Reveal>
        <Reveal>
          <div style={{ display: "flex", alignItems: "center", gap: 18, marginTop: 26, flexWrap: "wrap" }}>
            <label className="mono" style={{ fontSize: 10, display: "flex", alignItems: "center", gap: 12 }}>
              population
              <input type="range" min="1" max="3" value={n} onChange={(e) => setN(+e.target.value)} style={{ width: 140 }} />
            </label>
            <div style={{ fontSize: "1.6rem", fontWeight: 750, color: "#F08A2C" }}>{cfg.pop}</div>
            <div className="mono" style={{ fontSize: 10, color: "#7FA8A6" }}>{cfg.mw} compute · {cfg.note}</div>
          </div>
          <svg viewBox="0 0 1000 300" style={{ width: "100%", marginTop: 14, display: "block" }}>
            {/* utilidor ring */}
            <rect x="120" y="60" width="760" height="180" rx="60" fill="none" stroke="#F08A2C" strokeWidth="2.5" strokeDasharray="4 7" opacity=".8" />
            {n === 3 && <rect x="170" y="92" width="660" height="116" rx="48" fill="none" stroke="#F08A2C" strokeWidth="2" strokeDasharray="3 6" opacity=".5" />}
            {/* halls */}
            {Array.from({ length: cfg.halls }).map((_, i) => (
              <g key={"h" + i} style={{ transition: "opacity .4s" }}>
                <rect x={150 + i * 70} y={120} width="56" height="38" rx="5" fill="#0C2730" stroke="#7FD8E8" strokeWidth="2" />
                {[0, 1].map((c) => <rect key={c} x={160 + i * 70 + c * 18} y={132} width="12" height="9" rx="1.5" fill="#7FD8E8" style={{ animation: REDUCE ? "none" : `glowP ${2 + i + c}s infinite` }} />)}
              </g>
            ))}
            <text x="150" y="108" className="mono" fontSize="10" fill="#7FD8E8">DATA HALLS ×{cfg.halls}</text>
            {/* glass commons — homes + gardens under each vault */}
            {Array.from({ length: cfg.gh }).map((_, i) => {
              const b = 410 + i * 155;
              return (
                <g key={"g" + i}>
                  <path d={`M${b},200 C${b + 32},100 ${b + 98},100 ${b + 130},200`} fill="#7FD8E8" opacity=".07" />
                  <path d={`M${b},200 C${b + 32},100 ${b + 98},100 ${b + 130},200`} fill="none" stroke="#9ED9A8" strokeWidth="2" />
                  <rect x={b + 36} y="160" width="34" height="22" fill="#0C2730" stroke="#F08A2C" strokeWidth="1.6" />
                  <rect x={b + 42} y="166" width="16" height="8" fill="#FFC97A" style={{ animation: REDUCE ? "none" : `glowP ${3.4 + i}s infinite` }} />
                  {[b + 88, b + 104].map((x) => (
                    <g key={x} stroke="#9ED9A8" strokeWidth="2" fill="none">
                      <line x1={x} y1="200" x2={x} y2="184" /><path d={`M${x},187 l-5,-6 M${x},187 l5,-6`} />
                    </g>
                  ))}
                </g>
              );
            })}
            <text x="410" y="226" className="mono" fontSize="10" fill="#9ED9A8">GLASS COMMONS ×{cfg.gh} — HOMES + GARDENS INSIDE</text>
            {/* char + works */}
            <circle cx="220" cy="196" r="14" fill="#0A2530" stroke="#6FB9C9" strokeWidth="2.5" />
            <text x="184" y="230" className="mono" fontSize="10" fill="#6FB9C9">CHAR + WORKS</text>
          </svg>
        </Reveal>
      </div>
    </section>
  );
}

/* ───────────────────────── SITES: NETWORK MAP ───────────────────────── */
const SITES = [
  { id: "rankin", name: "Rankin Inlet, NU", x: 466, y: 235, tier: 1, s: [5, 4, 4, 5, 5], note: "Terminus of the Inuit-led Kivalliq Hydro-Fibre Link: 150 MW of Manitoba hydro + fiber, shovels targeted 2028. Sealift port, regional hub, mining workforce." },
  { id: "gillam", name: "Gillam, MB", x: 448, y: 340, tier: 1, s: [5, 5, 5, 5, 3], note: "Sits beside the Nelson River hydro stations — gigawatts of firm clean power, rail, and fiber. The compute-heaviest frond goes here." },
  { id: "churchill", name: "Churchill, MB", x: 452, y: 301, tier: 1, s: [4, 5, 5, 4, 4], note: "Deep-water Arctic port + Hudson Bay Railway + existing (upgradeable) transmission. Bedrock coast. Canada's logistics gate to the bay." },
  { id: "thompson", name: "Thompson, MB", x: 419, y: 350, tier: 2, s: [5, 4, 4, 4, 3], note: "On the Manitoba hydro grid with rail, airport, hospital and trades base. Brownfield mining city ready for a retrofit frond." },
  { id: "baker", name: "Baker Lake, NU", x: 438, y: 211, tier: 2, s: [4, 3, 4, 4, 5], note: "Nunavut's only inland community, on the KHFL route, beside the Meadowbank mining corridor." },
  { id: "goose", name: "Goose Bay, NL", x: 769, y: 300, tier: 2, s: [5, 4, 4, 4, 3], note: "Downstream of Churchill Falls — one of the largest hydro plants on Earth. Huge airfield, port, and Innu/Inuit partnership context." },
  { id: "yk", name: "Yellowknife, NWT", x: 302, y: 219, tier: 2, s: [3, 4, 5, 4, 4], note: "Shield bedrock, Snare hydro, all-season road, territorial capital with fiber. Constrained power until Taltson expansion." },
  { id: "moosonee", name: "Moosonee, ON", x: 592, y: 407, tier: 3, s: [3, 4, 3, 3, 4], note: "Rail terminus on James Bay (Polar Bear Express) with Moose Cree partnership potential; muskeg ground needs care." },
  { id: "scheff", name: "Schefferville, QC", x: 703, y: 308, tier: 3, s: [3, 4, 5, 3, 4], note: "Iron-range rail from Sept-Îles, deep shield bedrock, Naskapi & Innu nations adjacent. Power line required." },
  { id: "radisson", name: "Radisson · Eeyou Istchee, QC", x: 612, y: 359, tier: 1, s: [5, 4, 4, 4, 4], note: "Beside the La Grande complex — the largest hydro system in North America — with an all-season road and the Cree-owned Eeyou fiber network. The Paix des Braves treaty is the partnership template at work." },
  { id: "whitehorse", name: "Whitehorse, YT", x: 148, y: 172, tier: 2, s: [3, 5, 4, 4, 4], note: "Alaska Highway, jet airport, newly twinned fiber, and eleven self-governing First Nations. The Yukon grid is small — a frond brings its own wind; the roads and trades base do the rest." },
  { id: "hayriver", name: "Hay River · Taltson, NWT", x: 283, y: 241, tier: 2, s: [4, 5, 4, 4, 4], note: "The NWT\u2019s only railhead and its Great Slave barge hub, beside Taltson hydro with expansion proposed — plus the Northern Farm Training Institute, the North\u2019s own soil school." },
  { id: "watay", name: "Watay corridor · Sioux Lookout, ON", x: 478, y: 442, tier: 2, s: [4, 4, 4, 4, 5], note: "On Wataynikaneyap Power — 1,800 km of Indigenous-majority-owned transmission reaching 17 First Nations. The governance model FERN wants already runs here, with CN rail through town." },
  { id: "flinflon", name: "Flin Flon · Island Falls, MB/SK", x: 380, y: 363, tier: 3, s: [3, 4, 5, 3, 3], note: "A century of Churchill River hydro built for mining, rail service, and the hardest Shield rock anywhere — a brownfield town ready to be re-purposed." },
  { id: "inuvik", name: "Inuvik, NWT", x: 227, y: 77, tier: 3, s: [2, 4, 3, 5, 5], note: "The town that wrote our playbook — utilidors, the arena greenhouse, the reindeer herd — on the all-season Dempster Highway with the Mackenzie Valley fiber terminus. Power is the gap until wind scales beyond today\u2019s first turbines." },
  { id: "iqaluit", name: "Iqaluit, NU", x: 629, y: 181, tier: 3, s: [2, 3, 4, 2, 5], note: "Nunavut\u2019s capital: jet airport, sealift, granite ground and Inuit institutions — waiting on its long-proposed hydro and subsea fiber to jump tiers." },
];
const CRIT = ["POWER", "TRANSPORT", "GROUND", "FIBER", "PARTNERS"];
const TIER_C = { 1: "#F08A2C", 2: "#9ED9A8", 3: "#6FB9C9" };

function SitesPage() {
  const [sel, setSel] = useState(SITES[0]);
  return (
    <div>
      <section style={{ padding: "4.5rem 5vw 3rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Tag n="PLACE" label="where the fronds land" />
          <H2>Sixteen sites. Four time zones. One loop.</H2>
          <Sub>Scored on five hard criteria: firm clean power, transport, buildable ground, fiber, and — non-negotiable — Indigenous partnership capacity. The east-of-the-bay cluster is no accident: the compute anchor needs firm megawatts, and that is where surplus hydro, tidewater and funded corridors coincide. The western and central sites trade grid surplus for what the east lacks — all-season roads, Indigenous-owned grid and fiber, and the towns that wrote our playbook. Lambert-projected from real coordinates; coastline simplified. Each dot can host a frond.</Sub>
        </div>
      </section>
      <section style={{ padding: "0 5vw 5rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto", display: "grid", gridTemplateColumns: "1.6fr 1fr", gap: 18, alignItems: "start" }}>
          <Reveal>
            <div style={{ borderRadius: 18, overflow: "hidden", border: "1px solid #1E4751", background: "#081B22" }}>
              <svg viewBox="0 0 1000 600" style={{ display: "block", width: "100%" }}>
                {/* land */}
                <rect width="1000" height="600" fill="#07161C" />
                {/* land — Lambert conformal conic, projected from real coordinates */}
                <path d="M151,396 L149,390 L141,366 L123,335 L125,310 L122,283 L132,274 L142,255 L138,211 L127,181 L116,162 L107,148 L207,34 L217,44 L218,59 L228,59 L237,57 L242,66 L253,68 L270,71 L280,93 L296,118 L323,136 L348,140 L373,143 L396,161 L424,154 L438,127 L442,102 L448,87 L456,104 L465,125 L490,148 L503,130 L520,116 L527,137 L527,159 L516,172 L503,171 L494,194 L476,226 L466,235 L452,263 L452,301 L468,329 L512,342 L563,347 L571,384 L588,401 L593,407 L607,405 L609,387 L599,363 L589,351 L604,336 L609,314 L587,287 L585,261 L574,238 L572,224 L589,223 L619,223 L639,224 L648,246 L663,256 L674,261 L680,246 L680,224 L678,218 L707,237 L733,260 L782,268 L795,275 L817,288 L817,306 L800,339 L771,358 L739,374 L729,403 L758,383 L771,384 L755,405 L753,410 L791,423 L784,444 L769,455 L724,469 L685,490 L664,513 L643,540 L597,566 L600,539 L607,518 L570,505 L566,493 L518,474 L505,474 L443,461 L151,396 Z M111,342 L117,366 L130,397 L143,398 L134,368 L119,346 Z M826,296 L831,315 L850,319 L877,320 L891,333 L893,348 L864,350 L846,363 L820,342 L818,320 Z M827,409 L827,419 L812,447 L798,471 L785,457 L796,438 L805,423 L821,411 Z M324,76 L353,55 L370,77 L394,93 L408,123 L381,129 L341,123 L323,95 Z M318,18 L333,39 L318,67 L298,50 Z M659,205 L662,184 L656,174 L644,166 L650,146 L652,118 L627,108 L601,91 L584,80 L565,70 L539,58 L512,50 L526,77 L533,92 L544,113 L561,126 L580,140 L582,157 L585,187 L622,204 L650,204 Z M501,180 L519,179 L536,200 L527,215 L509,211 L499,193 Z" fill="#0E242C" stroke="#1E4751" strokeWidth="0.8" strokeLinejoin="round" />
                {/* major lakes */}
                <ellipse cx="299" cy="231" rx="22" ry="9" fill="#07161C" />
                <ellipse cx="278" cy="151" rx="18" ry="11" fill="#07161C" />
                <ellipse cx="419" cy="408" rx="7" ry="18" fill="#07161C" />
                {/* canadian shield, southwestern margin */}
                <path d="M358,154 L337,228 L338,278 L364,332 L406,386 L420,411 L445,451 L494,450 L565,421 L590,404" fill="none" stroke="#1E4751" strokeWidth="2" strokeDasharray="3 7" opacity=".8" />
                {/* rail */}
                <path d="M422,446 L409,381 L419,350 L448,340 L452,301" stroke="#5E8B89" strokeWidth="2" fill="none" />
                <path d="M597,444 L592,407" stroke="#5E8B89" strokeWidth="2" fill="none" />
                <path d="M739,374 L703,308" stroke="#5E8B89" strokeWidth="2" fill="none" />
                <path d="M274,334 L261,273 L283,241" stroke="#5E8B89" strokeWidth="2" fill="none" />
                <path d="M450,449 L478,442 L509,437" stroke="#5E8B89" strokeWidth="2" fill="none" />
                {/* corridors */}
                <path d="M448,340 L452,301 L452,263 L463,245 L466,235 L476,226 L438,211" className="flowPow" strokeWidth="2.5" />
                <path d="M478,442 L494,419 L499,395" className="flowPow" strokeWidth="2" />
                <path d="M227,77 L238,142 L249,209 L283,241" stroke="#6FB9C9" strokeWidth="1.6" fill="none" strokeDasharray="2 6" />
                <path d="M630,424 L612,359" stroke="#5E8B89" strokeWidth="1.6" fill="none" strokeDasharray="5 5" />
                <text x="473" y="272" className="mono" fontSize="8.5" fill="#9ED9A8">KIVALLIQ HYDRO-FIBRE LINK</text>
                <text x="455" y="405" className="mono" fontSize="8" fill="#9ED9A8">WATAY GRID</text>
                <text x="211" y="139" className="mono" fontSize="8" fill="#6FB9C9">MACKENZIE FIBRE</text>
                <text x="401" y="465" className="mono" fontSize="8" fill="#5E8B89">RAIL</text>
                <text x="573" y="433" className="mono" fontSize="7.5" fill="#1E4751">SHIELD MARGIN</text>
                <text x="506" y="284" className="mono" fontSize="9" fill="#3F6770" textAnchor="middle">HUDSON BAY</text>
                <text x="591" y="380" className="mono" fontSize="8.5" fill="#3F6770" textAnchor="middle">JAMES BAY</text>
                <text x="748" y="226" className="mono" fontSize="9" fill="#3F6770" textAnchor="middle">LABRADOR SEA</text>
                <text x="242" y="30" className="mono" fontSize="9" fill="#3F6770" textAnchor="middle">BEAUFORT SEA</text>
                <text x="163" y="121" className="mono" fontSize="8.5" fill="#2E525B" textAnchor="middle">YUKON</text>
                <text x="257" y="171" className="mono" fontSize="8.5" fill="#2E525B" textAnchor="middle">N.W.T.</text>
                <text x="409" y="176" className="mono" fontSize="8.5" fill="#2E525B" textAnchor="middle">NUNAVUT</text>
                <text x="170" y="303" className="mono" fontSize="8.5" fill="#2E525B" textAnchor="middle">B.C.</text>
                <text x="264" y="327" className="mono" fontSize="8.5" fill="#2E525B" textAnchor="middle">ALTA.</text>
                <text x="339" y="359" className="mono" fontSize="8.5" fill="#2E525B" textAnchor="middle">SASK.</text>
                <text x="401" y="399" className="mono" fontSize="8.5" fill="#2E525B" textAnchor="middle">MAN.</text>
                <text x="530" y="434" className="mono" fontSize="8.5" fill="#2E525B" textAnchor="middle">ONT.</text>
                <text x="666" y="357" className="mono" fontSize="8.5" fill="#2E525B" textAnchor="middle">QUE.</text>
                <text x="730" y="288" className="mono" fontSize="8.5" fill="#2E525B" textAnchor="middle">LAB.</text>
                {/* sites */}
                {SITES.map((s) => (
                  <g key={s.id} onClick={() => setSel(s)} style={{ cursor: "pointer" }}>
                    {sel.id === s.id && !REDUCE && <circle cx={s.x} cy={s.y} fill="none" stroke={TIER_C[s.tier]} strokeWidth="2" style={{ animation: "pulseR 1.8s ease-out infinite" }} />}
                    <circle cx={s.x} cy={s.y} r={sel.id === s.id ? 9 : 6.5} fill={TIER_C[s.tier]} stroke="#07161C" strokeWidth="2.5" style={{ transition: "r .2s" }} />
                    <text x={s.x + 12} y={s.y + 4} className="mono" fontSize="9.5" fill={sel.id === s.id ? "#E8F1F2" : "#7FA8A6"}>{s.name.split(",")[0].toUpperCase()}</text>
                  </g>
                ))}
                {/* legend */}
                {[1, 2, 3].map((t, i) => (
                  <g key={t}>
                    <circle cx={40} cy={40 + i * 22} r="6" fill={TIER_C[t]} />
                    <text x={54} y={44 + i * 22} className="mono" fontSize="9" fill="#7FA8A6">{["TIER 1 — BUILD FIRST", "TIER 2 — NEXT WAVE", "TIER 3 — WATCHLIST"][i]}</text>
                  </g>
                ))}
              </svg>
            </div>
          </Reveal>
          <Reveal>
            <div style={{ background: "#0C2730", border: `1px solid ${TIER_C[sel.tier]}55`, borderRadius: 16, padding: "1.3rem 1.4rem" }}>
              <div className="mono" style={{ fontSize: 9.5, color: TIER_C[sel.tier] }}>TIER {sel.tier}</div>
              <div style={{ fontWeight: 750, fontSize: "1.25rem", margin: "4px 0 8px" }}>{sel.name}</div>
              <div style={{ fontSize: ".9rem", color: "#A9C8C8", marginBottom: 16 }}>{sel.note}</div>
              {CRIT.map((c, i) => (
                <div key={c} style={{ marginBottom: 9 }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span className="mono" style={{ fontSize: 8.5, color: "#7FA8A6" }}>{c}</span>
                    <span className="mono" style={{ fontSize: 8.5, color: TIER_C[sel.tier] }}>{sel.s[i]}/5</span>
                  </div>
                  <div style={{ height: 6, background: "#14323B", borderRadius: 3, overflow: "hidden", marginTop: 3 }}>
                    <div key={sel.id + c} style={{ width: `${sel.s[i] * 20}%`, height: "100%", background: TIER_C[sel.tier], borderRadius: 3, transformOrigin: "left", animation: REDUCE ? "none" : "growBar .6s ease both" }} />
                  </div>
                </div>
              ))}
              <div className="mono" style={{ fontSize: 8.5, color: "#5E8B89", marginTop: 14 }}>tap any dot to compare</div>
            </div>
          </Reveal>
        </div>
      </section>
    </div>
  );
}

/* ───────────────────────── ENERGY PAGE ───────────────────────── */
const LADDER = [
  { t: "NOW", c: "#9ED9A8", items: [
    { k: "Arctic wind + storage", v: "6 MW @ Raglan", d: "Two 3 MW turbines on permafrost-pile foundations with battery, flywheel + hydrogen storage displace 4.4 ML diesel/yr at Glencore's Raglan mine. Diavik runs 9.2 MW with blade de-icing." },
    { k: "Server-heat districts", v: ">50% of a town", d: "Mäntsälä, Finland heats most of the town from one 15 MW data hall (heat-pump COP 2.7–4). Stockholm warms 30,000 apartments on recovered heat. FERN's core loop is already commercial." },
    { k: "Hydro + fiber interties", v: "150 MW", d: "The Inuit-owned Kivalliq Hydro-Fibre Link will run Manitoba hydro + broadband 1,200 km to five Kivalliq communities — the template for powering shield fronds." },
  ]},
  { t: "2030s", c: "#F08A2C", items: [
    { k: "Borehole seasonal storage", v: "90–100% solar fraction", d: "Drake Landing, Alberta stores summer heat in 144 boreholes and heats 52 homes through −30 °C winters — hitting 100% solar in 2015–16. Shield bedrock is an ideal thermal battery for summer's 20-hour days." },
    { k: "Microreactors", v: "5 MWe / 8+ yrs", d: "Westinghouse's eVinci heat-pipe 'nuclear battery' (5 MWe, refuel after 8+ years, 14–44% cheaper than diesel) is in Canadian regulatory review, with northern Indigenous and mining delegations engaged. One unit = firm heat + power for a 1k frond." },
    { k: "Biogas + CO₂ cascade", v: "closed loop", d: "Digesters turn town organics into peak-heating biogas, greenhouse CO₂ and fertilizer — every output is someone's input." },
  ]},
  { t: "MARS-CLASS", c: "#7FD8E8", items: [
    { k: "Fission surface power", v: "KRUSTY, 2018", d: "NASA's Kilopower reactor — built for Mars — was nuclear-tested in 2018; microreactors are its terrestrial descendants. Design rule: if it must work on Mars, it survives a Kivalliq February." },
    { k: "Closed-loop water (ECLSS)", v: "~98% recovery", d: "ISS-grade water recycling logic applied as vacuum sewers + reuse — shrinking the heated reservoir and treatment plant." },
    { k: "ISRU thinking", v: "build from site", d: "Mars colonists print with regolith; FERN quarries local granite aggregate, banks snow as insulation berms, and ships only what the land can't provide." },
    { k: "CSA grow pods", v: "Naurvik, NU", d: "The Canadian Space Agency already co-runs Naurvik in Gjoa Haven — wind-and-solar container farms producing food at −40 °C, run by local Inuit technicians, explicitly as a space-mission analog." },
  ]},
];
function EnergyPage() {
  const [open, setOpen] = useState("Server-heat districts");
  return (
    <div>
      <section style={{ padding: "4.5rem 5vw 1rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Tag n="ENERGY" label="the biome\u2019s metabolism" />
          <H2>What feeds the loop:<br />proven now → modular 2030s → Mars-class.</H2>
          <Sub>Every rung is research-backed. Tap a cell for the evidence.</Sub>
        </div>
      </section>
      <section style={{ padding: "1.5rem 5vw 2rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto", display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))", gap: 14 }}>
          {LADDER.map((col) => (
            <Reveal key={col.t}>
              <div className="mono" style={{ fontSize: 10, color: col.c, marginBottom: 10, borderBottom: `2px solid ${col.c}`, paddingBottom: 6 }}>{col.t}</div>
              {col.items.map((it) => (
                <div key={it.k} onClick={() => setOpen(open === it.k ? null : it.k)}
                  style={{ background: "#0C2730", border: `1px solid ${open === it.k ? col.c : "#1E4751"}`, borderRadius: 12, padding: "0.9rem 1rem", marginBottom: 10, cursor: "pointer", transition: "border .3s" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 8 }}>
                    <div style={{ fontWeight: 700, fontSize: ".98rem" }}>{it.k}</div>
                    <div className="mono" style={{ fontSize: 9, color: col.c, whiteSpace: "nowrap" }}>{it.v}</div>
                  </div>
                  {open === it.k && <div style={{ fontSize: ".85rem", color: "#A9C8C8", marginTop: 8 }}>{it.d}</div>}
                </div>
              ))}
            </Reveal>
          ))}
        </div>
      </section>

      {/* the honesty chart: piezo on a log scale */}
      <section style={{ padding: "3rem 5vw 5.5rem", background: "#0A1F27" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Reveal>
            <Tag n="ENERGY" label="the honesty chart" />
            <H2>Piezo: sensors, not power plants.</H2>
            <Sub>A footstep harvests ~0.1 W for an instant; whole reviews put piezo output in the microwatt–milliwatt class. On a log scale, one day of energy from each source:</Sub>
          </Reveal>
          <Reveal>
            <svg viewBox="0 0 1000 300" style={{ width: "100%", marginTop: 24, display: "block" }}>
              {[ ["EVERY FOOTSTEP IN TOWN / DAY", "~0.2 kWh — one phone-charging strip", 90, "#6FB9C9"],
                 ["PIEZO ROAD STRIPS (1 KM) / DAY", "~5 kWh — keeps the LED wayfinding lit", 200, "#6FB9C9"],
                 ["BIOGAS DIGESTER / DAY", "~4,000 kWh — peak-morning heat", 480, "#9ED9A8"],
                 ["ONE 3 MW TURBINE / DAY", "~25,000 kWh — Raglan-class", 640, "#9ED9A8"],
                 ["20 MW DATA-HALL HEAT / DAY", "~400,000 kWh recovered", 870, "#F08A2C"],
              ].map(([k, sub, w, c], i) => (
                <g key={k}>
                  <text x="0" y={36 + i * 56} className="mono" fontSize="10" fill="#E8F1F2">{k}</text>
                  <rect x="0" y={44 + i * 56} width={w} height="14" rx="7" fill={c} style={{ transformOrigin: "left", animation: REDUCE ? "none" : `growBar .9s ${i * 0.12}s ease both` }} />
                  <text x={w + 10} y={55 + i * 56} className="mono" fontSize="9" fill="#7FA8A6">{sub}</text>
                </g>
              ))}
              <text x="0" y="296" className="mono" fontSize="8.5" fill="#5E8B89">LOG-SCALE BAR LENGTHS · ORDER-OF-MAGNITUDE ESTIMATES</text>
            </svg>
            <Sub>So FERN uses piezo where it shines: self-powered vibration sensors on utilidors, bridges and turbine towers — monitoring that never needs a battery change through polar night. The watts come from wind, hydro, recovered heat, and (next decade) microreactors.</Sub>
          </Reveal>
        </div>
      </section>
    </div>
  );
}

/* ───────────────────────── ROBOTS PAGE ───────────────────────── */
const TASKS = [
  { k: "Open-road haulage (port↔town)", r: 90, why: "Komatsu runs ~150 autonomous trucks across Canada; Suncor fields ~120 through every season. Whiteouts don't blind lidar+GPS corridors.", who: "Dispatch + maintenance techs" },
  { k: "Underground / dangerous transport", r: 85, why: "Raglan's Anuri nickel mine just completed the Arctic's first autonomous underground ramp haul — the proof for FERN's dark-season logistics.", who: "Teleoperators on standby" },
  { k: "Snow clearing, night shift", r: 80, why: "Fixed routes, repeated nightly, drift sensors — the textbook autonomous task.", who: "One supervisor per fleet" },
  { k: "Greenhouse seed→harvest", r: 65, why: "Gantries handle the repetitive 70%; Naurvik proves local technicians run the system and choose the crops.", who: "Growers, agronomists" },
  { k: "Utilidor & pipe inspection", r: 75, why: "Thermal-camera crawlers patrol weekly; humans repair what robots find.", who: "Pipefitters, welders" },
  { k: "Data-hall operations", r: 70, why: "Rack-swap robots + remote monitoring keep night staffing near zero.", who: "Day-shift technicians" },
  { k: "Drone resupply & survey", r: 60, why: "Parts to the wind farm, permafrost plot monitoring, SAR thermal support.", who: "Pilots, SAR coordinators" },
  { k: "Construction & trades", r: 25, why: "Panelized modules cut site labour, but Arctic assembly is skilled human work.", who: "Carpenters, electricians, ironworkers" },
  { k: "Teaching & administration", r: 75, why: "Tutor agents run personalized curricula; governance agents draft budgets, permits and schedules. Humans ratify, mentor, and sit juries — see the crafts below.", who: "Mentors, citizen juries" },
  { k: "Hands-on care & emergency", r: 35, why: "Diagnostic and triage agents plus remote-specialist models handle the cognition; the hands at the bedside stay human — the one labour floor that holds.", who: "Clinicians, responders" },
  { k: "Harvest & stewardship", r: 30, why: "Satellite + drone agents track herds, ice and permafrost; harvesting and land presence run as voluntary civic shifts every citizen rotates through — no standing staff.", who: "Denizens on civic rota + dog teams" },
];
function RobotsPage() {
  const [sel, setSel] = useState(TASKS[1]);
  return (
    <div>
      <section style={{ padding: "4.5rem 5vw 1rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Tag n="ROBOTS" label="division of labour" />
          <H2>Machines take dull, dark, dangerous.<br />People keep judgment, care, culture.</H2>
          <Sub>Each bar = share of the task that’s automated. Tap a row for the precedent.</Sub>
        </div>
      </section>
      <section style={{ padding: "1.5rem 5vw 3rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto", display: "grid", gridTemplateColumns: "1.5fr 1fr", gap: 18, alignItems: "start" }}>
          <Reveal>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <span className="mono" style={{ fontSize: 9, color: "#F08A2C" }}>◼ ROBOT</span>
                <span className="mono" style={{ fontSize: 9, color: "#9ED9A8" }}>HUMAN ◼</span>
              </div>
              {TASKS.map((t) => (
                <div key={t.k} onClick={() => setSel(t)} style={{ marginBottom: 10, cursor: "pointer", opacity: sel.k === t.k ? 1 : 0.78, transition: "opacity .2s" }}>
                  <div style={{ fontSize: ".88rem", fontWeight: sel.k === t.k ? 700 : 400, marginBottom: 4 }}>{t.k}</div>
                  <div style={{ display: "flex", height: 14, borderRadius: 7, overflow: "hidden", border: sel.k === t.k ? "1px solid #E8F1F2" : "1px solid transparent" }}>
                    <div style={{ width: `${t.r}%`, background: "#F08A2C", transformOrigin: "left", animation: REDUCE ? "none" : "growBar .7s ease both" }} />
                    <div style={{ width: `${100 - t.r}%`, background: "#234B44" }} />
                  </div>
                </div>
              ))}
            </div>
          </Reveal>
          <Reveal>
            <div style={{ position: "sticky", top: 80 }}>
              <div style={{ background: "#0C2730", border: "1px solid #F08A2C66", borderRadius: 16, padding: "1.3rem 1.4rem" }}>
                <div className="mono" style={{ fontSize: 9, color: "#F08A2C" }}>{sel.r}% AUTOMATED</div>
                <div style={{ fontWeight: 750, fontSize: "1.1rem", margin: "4px 0 8px" }}>{sel.k}</div>
                <div style={{ fontSize: ".88rem", color: "#A9C8C8" }}>{sel.why}</div>
                <div className="mono" style={{ fontSize: 9, color: "#9ED9A8", marginTop: 14 }}>HUMANS HERE: {sel.who}</div>
              </div>
              {/* hauler animation */}
              <svg viewBox="0 0 300 90" style={{ width: "100%", marginTop: 14 }}>
                <line x1="10" y1="64" x2="290" y2="64" stroke="#3C5C63" strokeWidth="3" strokeDasharray="8 8" />
                {[50, 120, 190, 260].map((x) => <circle key={x} cx={x} cy="48" r="3" fill="#FFB35C" style={{ animation: REDUCE ? "none" : "blink 2.2s infinite" }} />)}
                <g style={{ animation: REDUCE ? "none" : "haulBot 4.5s linear infinite" }}>
                  <rect x="14" y="44" width="34" height="16" rx="4" fill="#F08A2C" />
                  <circle cx="23" cy="63" r="5" fill="#E8F1F2" /><circle cx="39" cy="63" r="5" fill="#E8F1F2" />
                </g>
                <text x="10" y="86" className="mono" fontSize="8.5" fill="#5E8B89">BEACON CORRIDOR · RUNS THROUGH WHITEOUTS</text>
              </svg>
            </div>
          </Reveal>
        </div>
      </section>
      <section style={{ padding: "2rem 5vw 5.5rem", background: "#0A1F27" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto", display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 12 }}>
          {[ ["~150", "autonomous Komatsu trucks already running in Canada"],
             ["1st", "Arctic underground autonomous ore haul — Raglan Anuri"],
             ["−40 °C", "Naurvik grow pods run by local Inuit technicians"],
             ["≥1 job", "skilled operator role created per robot fleet — training first"],
          ].map(([v, l]) => (
            <Reveal key={l}>
              <div style={{ borderTop: "3px solid #F08A2C", paddingTop: 10 }}>
                <div style={{ fontSize: "1.7rem", fontWeight: 750, color: "#F08A2C" }}>{v}</div>
                <div style={{ fontSize: ".85rem", color: "#A9C8C8", marginTop: 4 }}>{l}</div>
              </div>
            </Reveal>
          ))}
        </div>
      </section>
    </div>
  );
}

/* ───────────────────────── FOOD PAGE ───────────────────────── */
const PLATES = [
  { k: "GROWN", c: "#9ED9A8", pct: 30, sub: "greenhouse + beds",
    d: "Loop-heated glass and LED grow rooms run all year (the Mäntsälä model gives the heat; Naurvik proves the dark-season growing). Summer adds Inuvik-style insulated raised beds under 20-hour sun — Inuvik's arena greenhouse runs 174 community plots above the Arctic Circle." },
  { k: "RAISED", c: "#6FB9C9", pct: 25, sub: "char · yaks · hens · hives",
    d: "Arctic char in loop-heated tanks — Rankin Inlet literally ran a char cannery in the 1970s. The mini-farm adds yaks on rotational tundra paddocks (milk, down, draft), hens on kitchen scraps, and bumblebee hives that pollinate the glass. Whole foods, zero processing, zero food-miles." },
  { k: "HARVESTED", c: "#F08A2C", pct: 45, sub: "country food first",
    d: "Caribou, char, geese, berries — harvested, not farmed. Caribou is the top iron source in the Inuit diet; cutting it raises anemia prevalence measurably. Paid harvester roles, a community freezer and a processing kitchen keep the most nutrient-dense food on every plate." },
];
const SOIL_LAYERS = [
  { k: "INSULATION + LINER", c: "#3C5C63", h: 16, d: "Rigid insulation isolates the bed from frozen ground — exactly how Inuvik's plots sit on gravel over permafrost." },
  { k: "CRUSHED LOCAL TILL", c: "#5E7A82", h: 30, d: "Quarry fines and glacial till from site works — free mineral skeleton; nothing barged north." },
  { k: "BIOCHAR + WOODCHIP", c: "#43585C", h: 22, d: "Charred and chipped sealift pallets and brush hold water and nutrients in a thin profile." },
  { k: "DIGESTER COMPOST", c: "#7A5A2E", h: 30, d: "Town organics + fish waste + even caribou gut — the NWT's own soil-building playbook (Ecology North) lists fish waste and forest litter as prime northern inputs." },
  { k: "LIVING TOPSOIL", c: "#8A6A36", h: 24, d: "Three seasons of cover crops and compost tea turn the stack into real soil — built, not shipped." },
  { k: "CROPS", c: "#9ED9A8", h: 18, d: "Potatoes, carrots, kale, berries outside in summer; greens, tomatoes, herbs under glass all year." },
];
const CAL = [
  { k: "GLASS COMMONS", c: "#9ED9A8", r: 70, arcs: [[0, 360]] },
  { k: "CHAR TANKS", c: "#6FB9C9", r: 92, arcs: [[0, 360]] },
  { k: "OUTDOOR BEDS", c: "#F08A2C", r: 114, arcs: [[150, 270]] },
  { k: "BERRIES (AQPIK)", c: "#E86A8A", r: 136, arcs: [[195, 255]] },
  { k: "CARIBOU", c: "#C9A56A", r: 158, arcs: [[240, 360], [0, 60]] },
  { k: "GEESE + CHAR RUN", c: "#A9C8C8", r: 180, arcs: [[105, 150], [225, 270]] },
];
const arcPath = (cx, cy, r, a0, a1) => {
  const rad = (a) => ((a - 90) * Math.PI) / 180;
  const x0 = cx + r * Math.cos(rad(a0)), y0 = cy + r * Math.sin(rad(a0));
  const x1 = cx + r * Math.cos(rad(a1)), y1 = cy + r * Math.sin(rad(a1));
  return `M${x0},${y0} A${r},${r} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${x1},${y1}`;
};

function FoodPage() {
  const [plate, setPlate] = useState(PLATES[2]);
  const [layer, setLayer] = useState(REDUCE ? SOIL_LAYERS.length : 0);
  const soilRef = useRef(null);
  useEffect(() => {
    if (REDUCE) return;
    const io = new IntersectionObserver((es) => {
      es.forEach((e) => {
        if (e.isIntersecting) {
          let i = 0;
          const t = setInterval(() => { i++; setLayer(i); if (i >= SOIL_LAYERS.length) clearInterval(t); }, 600);
          io.disconnect();
        }
      });
    }, { threshold: 0.3 });
    if (soilRef.current) io.observe(soilRef.current);
    return () => io.disconnect();
  }, []);

  // plate donut geometry
  let acc = 0;
  const slices = PLATES.map((p) => { const a0 = acc * 3.6, a1 = (acc + p.pct) * 3.6; acc += p.pct; return { ...p, a0, a1 }; });

  return (
    <div>
      <section style={{ padding: "4.5rem 5vw 1rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Tag n="FOOD" label="whole · local · unprocessed" />
          <H2>The tundra can’t be farmed.<br />It can absolutely be fed from.</H2>
          <Sub>Roughly 70% of Nunavut households face food insecurity while barged-in produce arrives near-expired. FERN’s answer is three plates — none of them a freighter.</Sub>
        </div>
      </section>

      {/* three plates donut */}
      <section style={{ padding: "1.5rem 5vw 3rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1.2fr", gap: 22, alignItems: "center" }}>
          <Reveal>
            <svg viewBox="-105 0 510 300" style={{ width: "100%", maxWidth: 460, display: "block", margin: "0 auto" }}>
              {slices.map((s) => (
                <path key={s.k} d={arcPath(150, 150, 105, s.a0 + 2, s.a1 - 2)} stroke={s.c} strokeWidth={plate.k === s.k ? 40 : 28}
                  fill="none" strokeLinecap="round" style={{ cursor: "pointer", transition: "stroke-width .25s", filter: plate.k === s.k ? `drop-shadow(0 0 10px ${s.c}88)` : "none" }}
                  onClick={() => setPlate(s)} />
              ))}
              <text x="150" y="142" textAnchor="middle" className="mono" fontSize="11" fill="#7FA8A6">TARGET PLATE</text>
              <text x="150" y="168" textAnchor="middle" fontSize="26" fontWeight="750" fill={plate.c}>{plate.pct}%</text>
              {slices.map((s) => {
                const mid = ((s.a0 + s.a1) / 2 - 90) * Math.PI / 180;
                const cx = Math.cos(mid);
                const anchor = cx < -0.35 ? "end" : cx > 0.35 ? "start" : "middle";
                return <text key={s.k + "l"} x={150 + 138 * cx + (anchor === "end" ? -8 : anchor === "start" ? 8 : 0)} y={150 + 146 * Math.sin(mid) + 4} textAnchor={anchor} className="mono" fontSize="10" fill={s.c}>{s.k}</text>;
              })}
            </svg>
          </Reveal>
          <Reveal>
            <div style={{ background: "#0C2730", border: `1px solid ${plate.c}66`, borderRadius: 16, padding: "1.3rem 1.4rem" }}>
              <div className="mono" style={{ fontSize: 9.5, color: plate.c }}>{plate.k} · {plate.sub}</div>
              <div style={{ fontSize: ".92rem", color: "#C5D9D9", marginTop: 8 }}>{plate.d}</div>
              <div className="mono" style={{ fontSize: 8.5, color: "#5E8B89", marginTop: 12 }}>tap the ring segments</div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* soil stack */}
      <section ref={soilRef} style={{ padding: "3rem 5vw", background: "#0A1F27" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Reveal>
            <Tag n="FOOD" label="soil from scratch" />
            <H2>You don’t find soil on the Shield. You manufacture it.</H2>
            <Sub>Watch the bed build itself — every layer sourced on site or from town waste streams. The recipe is the North’s own: insulated beds over frozen ground (Inuvik), fish-waste and forest-litter compost (Ecology North’s NWT guide), even caribou-gut compost (Up Here).</Sub>
          </Reveal>
          <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 20, marginTop: 26, alignItems: "end" }}>
            <svg viewBox="0 0 600 260" style={{ width: "100%", display: "block" }}>
              {/* bedrock */}
              <rect x="0" y="216" width="600" height="44" fill="#163137" />
              <g stroke="#2C5763" strokeWidth="1.5">{[60, 140, 220, 300, 380, 460, 540].map((x) => <line key={x} x1={x} y1="222" x2={x - 18} y2="258" />)}</g>
              <text x="14" y="246" className="mono" fontSize="10" fill="#9FC2C4">BEDROCK / TILL</text>
              {/* bed frame */}
              <rect x="120" y="64" width="360" height="152" rx="6" fill="none" stroke="#5E8B89" strokeWidth="3" />
              {(() => { let y = 216; return SOIL_LAYERS.map((L, i) => { y -= L.h; const vis = layer > i; return (
                <g key={L.k} style={{ opacity: vis ? 1 : 0, transition: "opacity .5s" }}>
                  <rect x="123" y={y} width="354" height={L.h - 2} fill={L.c} rx="3" />
                  <text x="490" y={y + L.h / 2 + 3} className="mono" fontSize="9" fill={vis ? "#E8F1F2" : "#5E8B89"}>{L.k}</text>
                </g>
              ); }); })()}
              {/* plants on top when complete */}
              {layer >= SOIL_LAYERS.length && [180, 250, 320, 390].map((x, i) => (
                <g key={x} stroke="#9ED9A8" strokeWidth="3" fill="none" style={{ opacity: 0, animation: REDUCE ? "none" : `fadeUp .6s ${i * 0.15}s ease both` }}>
                  <line x1={x} y1="86" x2={x} y2="62" /><path d={`M${x},68 l-9,-10 M${x},68 l9,-10`} />
                </g>
              ))}
            </svg>
            <div style={{ background: "#0C2730", border: "1px solid #1E4751", borderRadius: 14, padding: "1.1rem 1.2rem" }}>
              <div className="mono" style={{ fontSize: 9, color: "#9ED9A8" }}>LAYER {Math.min(layer, SOIL_LAYERS.length)} / {SOIL_LAYERS.length}</div>
              <div style={{ fontWeight: 700, marginTop: 4 }}>{SOIL_LAYERS[clamp(layer - 1, 0, SOIL_LAYERS.length - 1)].k}</div>
              <div style={{ fontSize: ".85rem", color: "#A9C8C8", marginTop: 6 }}>{SOIL_LAYERS[clamp(layer - 1, 0, SOIL_LAYERS.length - 1)].d}</div>
            </div>
          </div>
        </div>
      </section>

      {/* food calendar wheel */}
      <section style={{ padding: "4rem 5vw" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto", display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 22, alignItems: "center" }}>
          <Reveal>
            <svg viewBox="0 0 420 420" style={{ width: "100%", maxWidth: 460, display: "block", margin: "0 auto" }}>
              {["J","F","M","A","M","J","J","A","S","O","N","D"].map((m, i) => {
                const a = (i * 30 - 90) * Math.PI / 180;
                return <text key={i} x={210 + 198 * Math.cos(a)} y={214 + 198 * Math.sin(a)} textAnchor="middle" className="mono" fontSize="10" fill="#5E8B89">{m}</text>;
              })}
              {CAL.map((ring) => ring.arcs.map(([a0, a1], j) => (
                <path key={ring.k + j} d={arcPath(210, 210, ring.r, a0 + 3, a1 - 3)} stroke={ring.c} strokeWidth="13" fill="none" strokeLinecap="round"
                  style={{ opacity: .92, animation: REDUCE ? "none" : `fadeUp .8s ${ring.r / 300}s ease both` }} />
              )))}
              <text x="210" y="204" textAnchor="middle" className="mono" fontSize="10" fill="#7FA8A6">WHAT’S ON</text>
              <text x="210" y="222" textAnchor="middle" className="mono" fontSize="10" fill="#7FA8A6">THE TABLE</text>
            </svg>
          </Reveal>
          <Reveal>
            <Tag n="FOOD" label="the year, eaten" />
            <H2>Something fresh every month of polar night.</H2>
            <div style={{ marginTop: 16 }}>
              {CAL.map((r) => (
                <div key={r.k} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                  <div style={{ width: 22, height: 6, borderRadius: 3, background: r.c }} />
                  <span className="mono" style={{ fontSize: 9.5, color: "#A9C8C8" }}>{r.k}</span>
                </div>
              ))}
            </div>
            <Sub>Inner rings never stop: the loop keeps greens and char coming through −40 °C. Outer rings follow the land’s own calendar — that’s a feature. Eating with the seasons is what whole-food cultures do.</Sub>
          </Reveal>
        </div>
      </section>

      {/* greenspace microclimate */}
      <section style={{ padding: "3rem 5vw 5.5rem", background: "#0A1F27" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Reveal>
            <Tag n="FOOD" label="greenspace on rock" />
            <H2>Green grows in the lee.</H2>
            <Sub>The windscreen block isn’t just housing — it manufactures a microclimate. Calm air on the lee side reads several degrees warmer; that’s where the courtyard gardens, willow shelterbelts and berry sods live. Beyond the fence line, the rule flips: tundra is not a lawn — lichen mats take decades to regrow, so the wild stays wild. And the town core needs no lee at all — homes, pathways and the square live inside the glass commons: +15 °C of public green through the polar night.</Sub>
          </Reveal>
          <Reveal>
            <svg viewBox="0 0 1000 280" style={{ width: "100%", marginTop: 24, display: "block" }}>
              {/* wind arrows */}
              {[0, 1, 2].map((i) => (
                <path key={i} d={`M30,${70 + i * 36} h46 l-12,-9 m12,9 l-12,9`} stroke="#6FB9C9" strokeWidth="3" fill="none"
                  style={{ animation: REDUCE ? "none" : `chev 1.8s ${i * 0.5}s linear infinite` }} />
              ))}
              <text x="28" y="50" className="mono" fontSize="10" fill="#6FB9C9">NW WIND −40 °C</text>
              {/* windscreen block */}
              <path d="M180,230 L180,90 Q200,70 220,90 L220,230 Z" fill="#10333D" stroke="#F08A2C" strokeWidth="2.5" />
              <text x="150" y="252" className="mono" fontSize="10" fill="#F08A2C">WINDSCREEN BLOCK</text>
              {/* calm lee zone */}
              <path d="M222,230 Q400,150 620,230 Z" fill="#9ED9A8" opacity=".1" />
              <text x="330" y="146" className="mono" fontSize="10" fill="#9ED9A8">CALM LEE COURTYARD · FEELS WARMER</text>
              {/* raised beds */}
              {[270, 340, 410].map((x) => <rect key={x} x={x} y="196" width="52" height="18" rx="4" fill="#7A5A2E" stroke="#9ED9A8" strokeWidth="2" />)}
              {/* willows */}
              {[500, 540, 580].map((x, i) => (
                <g key={x} stroke="#9ED9A8" strokeWidth="2.5" fill="none">
                  <line x1={x} y1="226" x2={x} y2="192" />
                  <path d={`M${x},200 l-10,-12 M${x},200 l10,-12 M${x},212 l-8,-9 M${x},212 l8,-9`} />
                </g>
              ))}
              <text x="262" y="252" className="mono" fontSize="9" fill="#9ED9A8">RAISED BEDS</text>
              <text x="492" y="252" className="mono" fontSize="9" fill="#9ED9A8">WILLOW + BERRY SODS</text>
              {/* fence + wild tundra */}
              <line x1="660" y1="160" x2="660" y2="236" stroke="#5E8B89" strokeWidth="2" strokeDasharray="5 6" />
              <text x="676" y="150" className="mono" fontSize="10" fill="#C9A56A">BEYOND THE FENCE: WILD</text>
              {[720, 790, 860, 930].map((x, i) => (
                <ellipse key={x} cx={x} cy={222 + (i % 2) * 8} rx="26" ry="8" fill="none" stroke="#C9A56A" strokeWidth="2" opacity=".7" />
              ))}
              <text x="712" y="252" className="mono" fontSize="9" fill="#C9A56A">LICHEN MATS · DECADES TO REGROW · NO VEHICLES</text>
              <line x1="0" y1="232" x2="1000" y2="232" stroke="#DCE9EC" strokeWidth="2" opacity=".4" />
            </svg>
          </Reveal>
          <Reveal>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))", gap: 12, marginTop: 30 }}>
              {[ ["174", "garden plots at Inuvik's arena greenhouse — above the Arctic Circle"],
                 ["+10 °C", "inside Inuvik's glass on midnight sun alone"],
                 ["#1 iron", "caribou's rank in the Inuit diet — country food is the nutrition anchor"],
                 ["0 km", "processing distance: tank, bed and freezer to table"],
              ].map(([v, l]) => (
                <div key={l} style={{ borderTop: "3px solid #9ED9A8", paddingTop: 10 }}>
                  <div style={{ fontSize: "1.6rem", fontWeight: 750, color: "#9ED9A8" }}>{v}</div>
                  <div style={{ fontSize: ".84rem", color: "#A9C8C8", marginTop: 4 }}>{l}</div>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </section>
    </div>
  );
}

/* ───────────────────────── DENIZENS PAGE (the terrarium) ───────────────────────── */
const EPOCHS = [
  { k: "2030s", sub: "today's stack, deployed hard", agents: "2,400", robots: "300", animals: "220" },
  { k: "2040s", sub: "self-improving ops, embodied fleets", agents: "60,000", robots: "900", animals: "450" },
  { k: "DIASPORA+", sub: "polis-scale software civics", agents: "10⁶+", robots: "3,000+", animals: "600" },
];
const BEINGS = [
  { t: "Polar-night perimeter & bear awareness", b: "QIMMIIT + DRONES", c: "#C9A56A", kind: "animal",
    d: "Canadian Inuit dog teams read bears, weather and thin ice before any sensor does; thermal drones extend their reach. No battery quits at −50 °C, and no robot earns trust the way a dog does." },
  { t: "Transport when everything else fails", b: "DOG TEAMS", c: "#C9A56A", kind: "animal",
    d: "The original autonomous vehicle: self-fueling, self-healing, runs in total whiteout. Kept in working service — qimmiit nearly vanished once; a town that depends on them again won't let that repeat." },
  { t: "Tundra forage → milk, fiber, draft", b: "YAKS", c: "#C9A56A", kind: "animal",
    d: "Yaks thrive past −40 °C on rough sedge, give dense down, rich milk and haul power — a mini-farm that maintains itself on land no tractor should touch. Paddocked on rotation so the tundra never overgrazes." },
  { t: "Pollinating two hectares of glass", b: "BUMBLEBEES", c: "#FFC97A", kind: "animal",
    d: "Boxed bumblebee colonies are the commercial-greenhouse standard worldwide — tireless, precise, and they work for flowers." },
  { t: "Kitchen scraps → eggs", b: "HENS", c: "#FFC97A", kind: "animal",
    d: "Northern coops already run on local protein — Up Here's narwhal-fed chickens are real. The coop rides the heat loop; the flock rides the food cycle." },
  { t: "Landscape-scale herd protein", b: "REINDEER + HERD AGENTS", c: "#C9A56A", kind: "hybrid",
    d: "Canada has herded reindeer near the Mackenzie Delta since the 1930s. Satellite collars and drone agents let a two-person crew steward what once took dozens — herding as a craft, upgraded." },
  { t: "Manufacturing living soil", b: "MICROBES + WORMS", c: "#9ED9A8", kind: "living",
    d: "Vermicompost beds and digester cultures run chemistry no machine matches. The smallest denizens carry the food system." },
  { t: "Holding 70 °C through a blizzard", b: "AGENTS", c: "#A78BDB", kind: "software",
    d: "Setpoints, dispatch, forecasting, logistics — software's native habitat. Governance agents draft; the town ratifies." },
  { t: "Hauling through whiteouts, all night", b: "ROBOTS", c: "#7FD8E8", kind: "machine",
    d: "Beacon corridors, lidar, no circadian rhythm. Machines take the dull, dark and dangerous so nobody has to." },
  { t: "A hand on a shoulder at 3 a.m.", b: "HUMANS", c: "#E86A8A", kind: "human",
    d: "Care, consent, ceremony, teaching by presence, judgment under uncertainty. Not what's left over after automation — what everything else exists to protect." },
];
const CRAFTS = [
  { k: "Agent & constitution craft", c: "#A78BDB", e: [60, 40, 12], mix: [{ h: 30, a: 70, r: 0, an: 0, l: 0 }, { h: 18, a: 82, r: 0, an: 0, l: 0 }, { h: 8, a: 92, r: 0, an: 0, l: 0 }], skills: "Evals · red-team · audit tooling · public reasoning logs" },
  { k: "Embodied-AI & fleet craft", c: "#7FD8E8", e: [90, 50, 14], mix: [{ h: 20, a: 25, r: 55, an: 0, l: 0 }, { h: 10, a: 30, r: 60, an: 0, l: 0 }, { h: 4, a: 36, r: 60, an: 0, l: 0 }], skills: "Cold-rated actuators · sim-to-real · teleop escalation" },
  { k: "Infra, fiber & compute craft", c: "#6FB9C9", e: [70, 30, 8], mix: [{ h: 25, a: 55, r: 20, an: 0, l: 0 }, { h: 12, a: 63, r: 25, an: 0, l: 0 }, { h: 5, a: 65, r: 30, an: 0, l: 0 }], skills: "Data-hall SRE · SCADA security · sovereign networks" },
  { k: "Twin & simulation craft", c: "#9ED9A8", e: [40, 20, 6], mix: [{ h: 20, a: 80, r: 0, an: 0, l: 0 }, { h: 10, a: 90, r: 0, an: 0, l: 0 }, { h: 4, a: 96, r: 0, an: 0, l: 0 }], skills: "Town-twin · permafrost models · policy sandboxing" },
  { k: "Medicine craft", c: "#E86A8A", e: [60, 30, 10], mix: [{ h: 50, a: 38, r: 12, an: 0, l: 0 }, { h: 30, a: 45, r: 25, an: 0, l: 0 }, { h: 12, a: 55, r: 33, an: 0, l: 0 }], skills: "Clinicians with diagnostic agents · hands-on floor" },
  { k: "Emergency & SAR craft", c: "#FFC97A", e: [25, 15, 6], mix: [{ h: 35, a: 20, r: 35, an: 10, l: 0 }, { h: 22, a: 28, r: 40, an: 10, l: 0 }, { h: 12, a: 33, r: 45, an: 10, l: 0 }], skills: "Drone-swarm incident command · cold-water rescue · SAR dogs" },
  { k: "Animal husbandry craft", c: "#C9A56A", e: [30, 35, 40], mix: [{ h: 35, a: 12, r: 8, an: 45, l: 0 }, { h: 28, a: 17, r: 10, an: 45, l: 0 }, { h: 22, a: 20, r: 12, an: 46, l: 0 }], skills: "Dog teams · yak paddocks · hives · herd stewardship" },
  { k: "Growing & soil craft", c: "#9ED9A8", e: [45, 40, 35], mix: [{ h: 22, a: 15, r: 23, an: 10, l: 30 }, { h: 14, a: 18, r: 28, an: 10, l: 30 }, { h: 8, a: 20, r: 30, an: 10, l: 32 }], skills: "Glass + beds + vermiculture · the food cycle" },
  { k: "Making & repair craft", c: "#F08A2C", e: [90, 35, 12], mix: [{ h: 45, a: 15, r: 40, an: 0, l: 0 }, { h: 25, a: 20, r: 55, an: 0, l: 0 }, { h: 10, a: 22, r: 68, an: 0, l: 0 }], skills: "Generalist trades riding with repair-bots" },
  { k: "Raising & teaching craft", c: "#E86A8A", e: [45, 25, 15], mix: [{ h: 50, a: 40, r: 2, an: 8, l: 0 }, { h: 30, a: 58, r: 4, an: 8, l: 0 }, { h: 15, a: 72, r: 5, an: 8, l: 0 }], skills: "Presence-first; tutor-agents as instruments · dogs for growing up with" },
];
const SHIFTS = ["STEWARDSHIP WALKS", "HARVEST CREWS", "ELDER & CHILD TIME", "CITIZEN JURIES", "TEACHING CIRCLES", "KITCHEN NIGHTS"];
const DTYPES = [["h", "HUMANS", "#E86A8A"], ["a", "AGENTS", "#A78BDB"], ["r", "ROBOTS", "#7FD8E8"], ["an", "ANIMALS", "#C9A56A"], ["l", "LIVING SYSTEMS", "#9ED9A8"]];

function MixDonut({ mix, epoch }) {
  let acc = 0;
  const segs = DTYPES.filter(([key]) => mix[key] > 0).map(([key, label, c]) => {
    const a0 = acc * 3.6, a1 = (acc + mix[key]) * 3.6;
    acc += mix[key];
    return { key, label, c, v: mix[key], a0, a1 };
  });
  return (
    <div style={{ background: "#0C2730", border: "1px solid #1E4751", borderRadius: 16, padding: "1rem 1.1rem", marginTop: 14 }}>
      <div className="mono" style={{ fontSize: 8.5, color: "#7FA8A6", marginBottom: 6 }}>WHO DOES THIS CRAFT'S WORK · {epoch}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <svg viewBox="0 0 120 120" width="116" style={{ flexShrink: 0 }}>
          {segs.map((s) => (
            <path key={s.key} d={arcPath(60, 60, 44, s.a0 + (s.v < 99 ? 4 : 0), s.a1 - (s.v < 99 ? 4 : 0.01))}
              stroke={s.c} strokeWidth="15" fill="none" strokeLinecap="round"
              style={{ transition: "d .4s" }} />
          ))}
        </svg>
        <div style={{ display: "grid", gap: 4 }}>
          {segs.map((s) => (
            <div key={s.key} style={{ display: "flex", alignItems: "center", gap: 7 }}>
              <span style={{ width: 10, height: 10, borderRadius: 3, background: s.c, display: "inline-block" }} />
              <span className="mono" style={{ fontSize: 8, color: "#A9C8C8" }}>{s.label} {s.v}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function DenizensPage() {
  const [ep, setEp] = useState(1);
  const [sel, setSel] = useState(BEINGS[0]);
  const [cr, setCr] = useState(CRAFTS[6]);
  const max = Math.max(...CRAFTS.map((g) => Math.max(...g.e)));
  return (
    <div>
      {/* census */}
      <section style={{ padding: "4.5rem 5vw 1rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Tag n="DENIZENS" label="a terrarium, not an org chart" />
          <H2>One ecosystem. Every denizen on the right task.</H2>
          <Sub>Nobody here is "staff" and nobody is "just a resident" — humans, agents, robots, animals and living systems are all denizens of one loop, each doing what it’s best built for. Slide the epoch to watch the mix evolve.</Sub>
          <div style={{ display: "flex", gap: 10, marginTop: 22, flexWrap: "wrap", alignItems: "center" }}>
            {EPOCHS.map((e, i) => (
              <button key={e.k} onClick={() => setEp(i)} className="mono"
                style={{ fontSize: 10, padding: ".55rem 1rem", borderRadius: 99, cursor: "pointer",
                  border: `1px solid ${ep === i ? "#9ED9A8" : "#1E4751"}`,
                  background: ep === i ? "#9ED9A8" : "transparent",
                  color: ep === i ? "#0B1D24" : "#7FA8A6", transition: "all .3s" }}>{e.k}</button>
            ))}
            <span className="mono" style={{ fontSize: 9, color: "#5E8B89" }}>{EPOCHS[ep].sub}</span>
          </div>
        </div>
      </section>
      <section style={{ padding: "1.5rem 5vw 2.5rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto", display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(170px,1fr))", gap: 12 }}>
          {[["HUMANS", "2,500", "#E86A8A", "every one of them crew"],
            ["AGENTS", EPOCHS[ep].agents, "#A78BDB", "govern · operate · teach"],
            ["ROBOTS", EPOCHS[ep].robots, "#7FD8E8", "haul · build · inspect"],
            ["ANIMALS", EPOCHS[ep].animals, "#C9A56A", "qimmiit · yaks · bees · hens"],
            ["LIVING SYSTEMS", "10¹⁴+", "#9ED9A8", "flora · microbiome · the land itself"],
          ].map(([k, v, c, s]) => (
            <div key={k} style={{ background: "#0C2730", border: `1px solid ${c}55`, borderRadius: 14, padding: "1rem 1.1rem" }}>
              <div className="mono" style={{ fontSize: 8.5, color: c }}>{k}</div>
              <div style={{ fontSize: "1.8rem", fontWeight: 760, color: c, transition: "all .4s" }}>{v}</div>
              <div className="mono" style={{ fontSize: 7.6, color: "#5E8B89" }}>{s}</div>
            </div>
          ))}
        </div>
      </section>

      {/* right being, right task */}
      <section style={{ padding: "2.5rem 5vw", background: "#0A1F27" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Reveal>
            <Tag n="DENIZENS" label="the matching principle" />
            <H2>Right denizen, right task.</H2>
          </Reveal>
          <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 18, marginTop: 22, alignItems: "start" }}>
            <Reveal>
              <div>
                {BEINGS.map((b) => (
                  <div key={b.t} onClick={() => setSel(b)}
                    style={{ display: "flex", justifyContent: "space-between", gap: 12, padding: ".62rem .8rem", borderRadius: 10, cursor: "pointer", marginBottom: 6,
                      background: sel.t === b.t ? "#0C2730" : "transparent",
                      border: `1px solid ${sel.t === b.t ? b.c : "transparent"}`, transition: "all .2s" }}>
                    <span style={{ fontSize: ".88rem", fontWeight: sel.t === b.t ? 700 : 400 }}>{b.t}</span>
                    <span className="mono" style={{ fontSize: 8.5, color: b.c, whiteSpace: "nowrap" }}>{b.b}</span>
                  </div>
                ))}
              </div>
            </Reveal>
            <Reveal>
              <div style={{ position: "sticky", top: 80 }}>
                <div style={{ background: "#0C2730", border: `1px solid ${sel.c}66`, borderRadius: 16, padding: "1.3rem 1.4rem" }}>
                  {/* being icon */}
                  <svg viewBox="0 0 60 44" width="64" style={{ marginBottom: 6 }}>
                    {sel.kind === "animal" && (<g stroke={sel.c} strokeWidth="2.5" fill="none" strokeLinecap="round">
                      <path d="M10,34 q6,-14 18,-14 q12,0 18,8 l6,-4 v8 l-5,2 q-4,6 -14,6 q-16,0 -23,-6 z" />
                      <circle cx="46" cy="26" r="1.6" fill={sel.c} /><path d="M14,40 v3 M26,42 v3 M38,42 v3" />
                    </g>)}
                    {sel.kind === "software" && (<g stroke={sel.c} strokeWidth="2.5" fill="none">
                      <circle cx="30" cy="22" r="11" /><circle cx="30" cy="22" r="4" fill={sel.c} />
                      {[0, 60, 120, 180, 240, 300].map((a) => { const r = a * Math.PI / 180; return <line key={a} x1={30 + 13 * Math.cos(r)} y1={22 + 13 * Math.sin(r)} x2={30 + 18 * Math.cos(r)} y2={22 + 18 * Math.sin(r)} />; })}
                    </g>)}
                    {sel.kind === "machine" && (<g stroke={sel.c} strokeWidth="2.5" fill="none">
                      <rect x="14" y="14" width="32" height="18" rx="4" /><circle cx="22" cy="38" r="4" /><circle cx="38" cy="38" r="4" />
                      <line x1="30" y1="14" x2="30" y2="7" /><circle cx="30" cy="6" r="2" fill={sel.c} />
                    </g>)}
                    {sel.kind === "human" && (<g stroke={sel.c} strokeWidth="2.5" fill="none" strokeLinecap="round">
                      <circle cx="30" cy="13" r="6" /><path d="M18,40 q0,-16 12,-16 q12,0 12,16" />
                    </g>)}
                    {sel.kind === "living" && (<g stroke={sel.c} strokeWidth="2.5" fill="none" strokeLinecap="round">
                      <path d="M30,42 V20 M30,28 q-10,-2 -12,-12 q10,2 12,12 M30,24 q10,-2 12,-12 q-10,2 -12,12" />
                    </g>)}
                    {sel.kind === "hybrid" && (<g stroke={sel.c} strokeWidth="2.5" fill="none" strokeLinecap="round">
                      <path d="M12,36 q5,-10 14,-10 q9,0 14,6" /><circle cx="44" cy="20" r="7" strokeDasharray="3 3" />
                    </g>)}
                  </svg>
                  <div className="mono" style={{ fontSize: 9.5, color: sel.c }}>{sel.b}</div>
                  <div style={{ fontWeight: 750, fontSize: "1.05rem", margin: "4px 0 8px" }}>{sel.t}</div>
                  <div style={{ fontSize: ".88rem", color: "#A9C8C8" }}>{sel.d}</div>
                </div>
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      {/* crafts */}
      <section style={{ padding: "3rem 5vw" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Reveal>
            <Tag n="DENIZENS" label="human crafts, not headcount" />
            <H2>Everyone is crew. Most hold three crafts.</H2>
            <Sub>No payroll line defines anyone. Bars show hands practicing each craft per 2,500 denizens at the selected epoch — note husbandry and growing crafts <i>rise</i> as automation deepens: machines absorb the grind, people move toward the living work.</Sub>
          </Reveal>
          <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr", gap: 18, marginTop: 24, alignItems: "start" }}>
            <Reveal>
              <div>
                {CRAFTS.map((g) => (
                  <div key={g.k} onClick={() => setCr(g)} style={{ marginBottom: 10, cursor: "pointer", opacity: cr.k === g.k ? 1 : 0.78, transition: "opacity .2s" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                      <span style={{ fontSize: ".88rem", fontWeight: cr.k === g.k ? 700 : 400 }}>{g.k}</span>
                      <span className="mono" style={{ fontSize: 9.5, color: g.c }}>{g.e[ep]}</span>
                    </div>
                    <div style={{ height: 13, background: "#14323B", borderRadius: 7, overflow: "hidden", border: cr.k === g.k ? "1px solid #E8F1F2" : "1px solid transparent" }}>
                      <div style={{ width: `${(g.e[ep] / max) * 100}%`, height: "100%", background: g.c, borderRadius: 7, transition: "width .6s ease" }} />
                    </div>
                  </div>
                ))}
                <div className="mono" style={{ fontSize: 8.5, color: "#5E8B89", marginTop: 8 }}>NEEDS — HOME, HEAT, FOOD, CARE — ARE INFRASTRUCTURE DIVIDENDS, NOT WAGES. THE LEDGER TRACKS CONTRIBUTION, NOT EMPLOYMENT.</div>
              </div>
            </Reveal>
            <Reveal>
              <div style={{ position: "sticky", top: 80 }}>
                <div style={{ background: "#0C2730", border: `1px solid ${cr.c}66`, borderRadius: 16, padding: "1.3rem 1.4rem" }}>
                  <div className="mono" style={{ fontSize: 9, color: cr.c }}>{cr.e[ep]} HANDS · {EPOCHS[ep].k}</div>
                  <div style={{ fontWeight: 750, fontSize: "1.12rem", margin: "4px 0 8px" }}>{cr.k}</div>
                  <div className="mono" style={{ fontSize: 8.5, color: "#9FC2C4", lineHeight: 1.8 }}>{cr.skills}</div>
                </div>
                <MixDonut mix={cr.mix[ep]} epoch={EPOCHS[ep].k} />
                {/* civic wheel, compact */}
                <svg viewBox="0 0 340 250" style={{ width: "100%", marginTop: 14 }}>
                  <g style={{ transformOrigin: "170px 125px", animation: REDUCE ? "none" : "spin 60s linear infinite" }}>
                    {SHIFTS.map((s, i) => {
                      const a = (i * 60 - 90) * Math.PI / 180;
                      return (
                        <g key={s}>
                          <line x1="170" y1="125" x2={170 + 88 * Math.cos(a)} y2={125 + 88 * Math.sin(a)} stroke="#1E4751" strokeWidth="1.5" />
                          <circle cx={170 + 88 * Math.cos(a)} cy={125 + 88 * Math.sin(a)} r="27" fill="#0C2730" stroke="#9ED9A8" strokeWidth="2" />
                          <text x={170 + 88 * Math.cos(a)} y={125 + 88 * Math.sin(a)} textAnchor="middle" className="mono" fontSize="5.6" fill="#9ED9A8">
                            {s.split(" ").map((w, j) => <tspan key={j} x={170 + 88 * Math.cos(a)} dy={j === 0 ? -2 : 7}>{w}</tspan>)}
                          </text>
                        </g>
                      );
                    })}
                  </g>
                  <circle cx="170" cy="125" r="33" fill="#0C2730" stroke="#F08A2C" strokeWidth="2.5" />
                  <text x="170" y="122" textAnchor="middle" className="mono" fontSize="7" fill="#F08A2C">CIVIC</text>
                  <text x="170" y="132" textAnchor="middle" className="mono" fontSize="7" fill="#F08A2C">ROTA</text>
                </svg>
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      {/* hard locks */}
      <section style={{ padding: "3rem 5vw 5.5rem", background: "#0A1F27" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Reveal>
            <Tag n="DENIZENS" label="what never automates" />
            <H2>Three locks, held by people.</H2>
          </Reveal>
          <Reveal>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(250px,1fr))", gap: 14, marginTop: 24 }}>
              {[["LAND", "#9ED9A8", "Footprint, extraction and anything beyond the fence line require a community vote. Agents model options; only denizens cast ballots."],
                ["LIFE", "#E86A8A", "Medical consent, use of force, child and animal welfare terminate at a human, always — agents advise, never decide."],
                ["LEDGER", "#FFC97A", "Equity shares, treasury and the agents' own constitution change only by ratified referendum, with public reasoning logs and a standing kill switch."],
              ].map(([k, c, d]) => (
                <div key={k} style={{ background: "#0C2730", border: `2px solid ${c}`, borderRadius: 16, padding: "1.2rem 1.3rem" }}>
                  <svg viewBox="0 0 40 40" width="34" height="34" style={{ marginBottom: 8 }}>
                    <rect x="8" y="18" width="24" height="16" rx="4" fill="none" stroke={c} strokeWidth="2.5" />
                    <path d="M13,18 v-5 a7,7 0 0 1 14,0 v5" fill="none" stroke={c} strokeWidth="2.5" />
                    <circle cx="20" cy="26" r="2.6" fill={c} />
                  </svg>
                  <div style={{ fontWeight: 750, fontSize: "1.1rem", color: c }}>{k}</div>
                  <div style={{ fontSize: ".86rem", color: "#A9C8C8", marginTop: 6 }}>{d}</div>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </section>
    </div>
  );
}

/* ───────────────────────── CHARTER PAGE ───────────────────────── */
const QUAYSIDE = [
  ["Land-price spiral made affordability impossible", "Greenfield shield land secured at cost under an IBA — no speculative basis to inflate, equity vests to residents and host nations"],
  ["Imposed on existing neighbors who never opted in", "Nobody is annexed: every denizen joins by application — and host Indigenous communities hold equity and veto"],
  ["A corporate entity holding the city's data", "A community data trust on sovereign local compute; every governance agent publishes its reasoning logs; sensing is opt-in"],
  ["One company's balance sheet, one exit decision", "Break-even co-op pricing, anchor-tenant revenue, and a charter no single backer can dissolve"],
];
function CharterPage() {
  return (
    <div>
      <section style={{ padding: "4.5rem 5vw 1rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Tag n="CHARTER" label="opt-in by design" />
          <H2>Nobody is moved here.<br />Everybody chose here.</H2>
          <Sub>Citizenship is chosen, never assigned<Ref ids="C3" />. The village is lived as a prototype before a single foundation is poured<Ref ids="C2" />, and the charter is written so no single backer can unwrite it.</Sub>
        </div>
      </section>

      {/* join flow */}
      <section style={{ padding: "1.5rem 5vw 2.5rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Reveal>
            <svg viewBox="0 0 1000 150" style={{ width: "100%", display: "block" }}>
              {[["SPORES", "join the digital commons from anywhere", "#A78BDB"],
                ["FIDDLEHEAD", "season-zero popup village — the spiral before it unfurls", "#9ED9A8"],
                ["FROND DENIZEN", "move in · equity begins vesting", "#F08A2C"],
                ["THE OPEN DOOR", "leave anytime, equity travels with you", "#6FB9C9"],
              ].map(([k, sub, c], i) => (
                <g key={k}>
                  <rect x={15 + i * 250} y="28" width="210" height="68" rx="14" fill="#0C2730" stroke={c} strokeWidth="2" />
                  <text x={120 + i * 250} y="54" textAnchor="middle" className="mono" fontSize="9.5" fill={c}>{k}</text>
                  <text x={120 + i * 250} y="74" textAnchor="middle" fontSize="9" fill="#A9C8C8">
                    {sub.length > 34 ? <><tspan x={120 + i * 250} dy="0">{sub.slice(0, sub.lastIndexOf(" ", 34))}</tspan><tspan x={120 + i * 250} dy="12">{sub.slice(sub.lastIndexOf(" ", 34) + 1)}</tspan></> : sub}
                  </text>
                  {i < 3 && <path d={`M${227 + i * 250},62 h20 l-8,-6 m8,6 l-8,6`} stroke="#5E8B89" strokeWidth="2.5" fill="none" />}
                </g>
              ))}
              <text x="15" y="136" className="mono" fontSize="9" fill="#5E8B89">THE FIDDLEHEAD RUNS EVERY SUMMER, BEFORE AND AFTER PERMANENT BUILD — EACH FROND IS PROTOTYPED BY ITS FUTURE DENIZENS, WITH HOST COMMUNITIES AS FIRST CITIZENS [C2]</text>
            </svg>
          </Reveal>
        </div>
      </section>

      {/* quayside autopsy */}
      <section style={{ padding: "2.5rem 5vw", background: "#0A1F27" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Reveal>
            <Tag n="CHARTER" label="the failure modes" />
            <H2>Top-down smart cities die four ways.<br />Each one is designed out.<Ref ids="C1" /></H2>
          </Reveal>
          <Reveal>
            <div style={{ marginTop: 24 }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 40px 1fr", gap: 8, marginBottom: 10 }}>
                <div className="mono" style={{ fontSize: 9, color: "#E86A8A" }}>THE TOP-DOWN MODEL †</div>
                <div />
                <div className="mono" style={{ fontSize: 9, color: "#9ED9A8" }}>THE FERN CHARTER</div>
              </div>
              {QUAYSIDE.map(([a, b], i) => (
                <div key={i} style={{ display: "grid", gridTemplateColumns: "1fr 40px 1fr", gap: 8, marginBottom: 10, alignItems: "stretch" }}>
                  <div style={{ background: "#0C2730", border: "1px solid #E86A8A44", borderRadius: 12, padding: ".85rem 1rem", fontSize: ".85rem", color: "#C5A9B0" }}>{a}</div>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <svg viewBox="0 0 24 24" width="22"><path d="M3,12 h14 m-5,-5 l5,5 l-5,5" stroke="#5E8B89" strokeWidth="2.5" fill="none" /></svg>
                  </div>
                  <div style={{ background: "#0C2730", border: "1px solid #9ED9A844", borderRadius: 12, padding: ".85rem 1rem", fontSize: ".85rem", color: "#A9C8C8" }}>{b}</div>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </section>

      {/* terrarium covenant + edge principles */}
      <section style={{ padding: "3rem 5vw 5.5rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto", display: "grid", gridTemplateColumns: "1.1fr 1fr", gap: 26, alignItems: "center" }}>
          <Reveal>
            <svg viewBox="0 0 420 320" style={{ width: "100%", maxWidth: 460, display: "block", margin: "0 auto" }}>
              {/* dome */}
              <path d="M50,260 q160,-260 320,0" fill="none" stroke="#9ED9A8" strokeWidth="2.5" strokeDasharray="6 7" />
              <line x1="20" y1="262" x2="400" y2="262" stroke="#DCE9EC" strokeWidth="2" opacity=".4" />
              {/* inside: town elements */}
              <path d="M150,260 l16,-14 l16,14 z" fill="#10333D" stroke="#F08A2C" strokeWidth="2" />
              <path d="M196,260 q20,-24 40,0 z" fill="#F08A2C" opacity=".75" style={{ animation: REDUCE ? "none" : "glowP 4s infinite" }} />
              <rect x="252" y="238" width="40" height="22" rx="4" fill="#0C2730" stroke="#7FD8E8" strokeWidth="2" />
              {/* yak + dog silhouettes */}
              <g stroke="#C9A56A" strokeWidth="2.2" fill="none" strokeLinecap="round">
                <path d="M104,256 q4,-10 14,-10 q10,0 14,6 m-28,4 v5 m24,-5 v5" />
                <path d="M318,256 q3,-8 10,-8 q8,0 12,5 l4,-3 v6 m-26,0 v4 m18,-4 v4" />
              </g>
              {/* birds + aurora */}
              <path d="M120,80 q6,-6 12,0 M140,72 q6,-6 12,0" stroke="#9FC2C4" strokeWidth="2" fill="none" />
              <text x="210" y="300" textAnchor="middle" className="mono" fontSize="9" fill="#9ED9A8">THE COVENANT: ≤2% OF THE LEASE FOOTPRINT EVER BUILT · EVERYTHING INSIDE CIRCULAR · EVERYTHING OUTSIDE WILD</text>
            </svg>
          </Reveal>
          <Reveal>
            <Tag n="CHARTER" label="the four principles" />
            <H2>Co-created. Healthy.<br />Multigenerational. Multispecies.<Ref ids="C2" /></H2>
            <div style={{ display: "grid", gap: 10, marginTop: 18 }}>
              {[["CO-CREATED", "denizens build the town by living in it — Season Zero is a working lab, not a sales suite"],
                ["HEALTHY BY DEFAULT", "whole local food, the windscreen square, dogs to run with, no commute"],
                ["MULTIGENERATIONAL", "toddlers to elders in one loop; elder knowledge is core curriculum"],
                ["MULTISPECIES", "the terrarium principle — every being in the loop is a denizen"],
              ].map(([k, d]) => (
                <div key={k} style={{ borderLeft: "3px solid #9ED9A8", paddingLeft: 12 }}>
                  <div className="mono" style={{ fontSize: 9.5, color: "#9ED9A8" }}>{k}</div>
                  <div style={{ fontSize: ".86rem", color: "#A9C8C8" }}>{d}</div>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </section>
    </div>
  );
}

/* ───────────────────────── RESEARCH PAGE ───────────────────────── */
const REFS = [
  { t: "HEAT LOOP", c: "#F08A2C", items: [
    ["Sitra / Nivos — Mäntsälä, Finland", "A 15 MW data center supplies ~54% of the town's district heat; heat recovery cut local heating prices 11%; heat-pump COP 2.7–4."],
    ["Stockholm Exergi — Open District Heating", "20+ heat suppliers including data centers warm ~30,000 apartments; excess heat is bought as a commodity."],
    ["Bloomberg (2025) — Finland's data centers", "A 75 MW hall heats the equivalent of 2,500 homes ~5 km away; Microsoft's Espoo campus targets ~40% of regional district heat."],
  ]},
  { t: "ENERGY", c: "#9ED9A8", items: [
    ["Tugliq / Glencore — Raglan Mine, Nunavik", "Two 3 MW Arctic-rated turbines on permafrost pile foundations + flywheel, Li-ion and hydrogen storage displace ~4.4 ML diesel/yr; >15 ML abated since 2014."],
    ["Arctic Council — Diavik wind farm, NWT", "9.2 MW wind-diesel hybrid with blade de-icing offset 3.8 ML diesel in year one."],
    ["NRCan — Drake Landing Solar Community, AB", "144-borehole seasonal store delivers 90–100% of winter space heat from summer sun in a 5,200 °C-day climate; optimal replication 200–300 homes."],
    ["Westinghouse / Bruce Power — eVinci microreactor", "5 MWe heat-pipe 'battery', 8+ year core, est. 14–44% cheaper than diesel; in CNSC review with northern Indigenous & mining delegations engaged."],
    ["NASA / NNSA — Kilopower KRUSTY (2018)", "Only fully nuclear-tested microreactor; built for Mars/lunar surface power — the design ancestor of remote-community units."],
    ["Nukik Corp. / CBC — Kivalliq Hydro-Fibre Link", "$3.3B, 1,200 km, 150 MW Manitoba-hydro + fiber corridor to five Kivalliq communities; Inuit-owned; shovels targeted 2028."],
    ["IOP / JR East — piezoelectric reality check", "Footstep harvesting ≈0.1 W instantaneous; reviews place piezo in the µW–mW class → sensors and wayfinding, not bulk power."],
  ]},
  { t: "FOOD & SOIL", c: "#6FB9C9", items: [
    ["CSA / Arctic Research Foundation — Naurvik, Gjoa Haven", "Community-led container farm 250 km above the Arctic Circle, wind+solar powered, run by local Inuit technicians; an explicit space-mission analog through 24-hour darkness."],
    ["Town of Inuvik / Carrot City — Inuvik Community Greenhouse", "North America's northernmost commercial greenhouse, in a converted arena: 174 insulated raised plots on gravel over permafrost, +10 °C on midnight sun alone, commercial hydroponics funding operations."],
    ["Ecology North — Building Your Soil (NWT guide)", "Northern soil recipe book: woodchips, forest litter, fish waste, hair and household compost as locally sourced bed-building organics."],
    ["Up Here — Can the North Feed Itself?", "Caribou-gut compost, narwhal-fed chickens — and Rankin Inlet's 1970s Arctic char cannery as precedent for northern food industry."],
    ["Cambridge BJN / PMC — Inuit dietary transition", "Store-food diets are energy-dense and nutrient-poor (sweet drinks = 82% of vitamin C intake); traditional foods carry far higher nutrient density."],
    ["BMC Nutrition — caribou & anemia", "Caribou is the top dietary iron source; modelled removal raises anemia prevalence ~6 points from a 26.5% baseline — country food access is health policy."],
    ["Global Citizen / Action Canada", "≈70% of Nunavut households face moderate-to-high food insecurity — six times the national rate."],
    ["Climate-envelope settlements (design lineage)", "Frei Otto and Buckminster Fuller\u2019s 1971 \u2018Arctic City\u2019 study proposed an Arctic town under a ~2 km pneumatic climate dome; Sweden\u2019s Naturhus tradition wraps whole homes in greenhouse skins. FERN scales the lineage to block size — several linked glass commons rather than one mega-dome, for fire, failure-mode and span-cost reasons."],
  ]},
  { t: "CHARTER & ECOSYSTEM", c: "#E86A8A", items: [
    ["Tomorrow.City — Sidewalk Toronto postmortem", "Quayside (2017–2020) collapsed under land-price escalation that broke its affordability model, pandemic shock, and neighborhood opposition to imposed change — the failure map the charter is drawn against."],
    ["Edge Esmeralda / Edge City", "A 500-person month-long popup village in Healdsburg prototyping a permanent town (Esmeralda) on four principles — co-created, healthy by default, multigenerational, multidisciplinary — including a live Agent Village experiment of humans and AI agents cohabiting. The popup-village-as-prototype method underpinning the Fiddlehead season."],
    ["The Network State (Balaji Srinivasan)", "Communities that form digitally around shared values, then materialize physically — citizenship by volition rather than birth or annexation; the legal-social template for FERN's join flow."],
    ["Working animals in the North (established practice)", "Qimmiit (Canadian Inuit dogs) as working sled/guard partners and a nearly-lost heritage breed; reindeer herded near the Mackenzie Delta since the 1930s; yaks farmed in cold-climate Canada; boxed bumblebees as the global greenhouse-pollination standard."],
  ]},
  { t: "ROBOTS", c: "#7FD8E8", items: [
    ["Komatsu / SMS Equipment", "~150 autonomous haul trucks deployed across Canada; 400+ worldwide with zero attributed safety incidents and ~15% lower haul costs."],
    ["Suncor — Base Plant, AB", "~120 autonomous ultra-class trucks running around the clock through every season."],
    ["Glencore — Raglan Anuri (2026)", "First Arctic underground autonomous ramp haul: ore climbed and dumped at surface with no driver."],
  ]},
];
function ResearchPage() {
  return (
    <div>
      <section style={{ padding: "4.5rem 5vw 1rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          <Tag n="RESEARCH" label="the receipts" />
          <H2>Every claim on this site, sourced.</H2>
          <Sub>Bracketed codes across the site — [L·], [E·], [F·], [C·], [R·] — resolve here. Concept synthesis is ours; the underlying facts are drawn from the named organizations, publications and peer-reviewed studies (compiled June 2026 — verify before citing onward).</Sub>
        </div>
      </section>
      <section style={{ padding: "1.5rem 5vw 5.5rem" }}>
        <div style={{ maxWidth: 1150, margin: "0 auto" }}>
          {REFS.map((g) => (
            <Reveal key={g.t}>
              <div className="mono" style={{ fontSize: 10, color: g.c, margin: "26px 0 12px", borderBottom: `2px solid ${g.c}`, paddingBottom: 6 }}>{g.t}</div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(300px,1fr))", gap: 12 }}>
                {g.items.map(([src2, find], i) => (
                  <div key={src2} style={{ background: "#0C2730", borderLeft: `3px solid ${g.c}`, borderRadius: 10, padding: ".9rem 1rem" }}>
                    <div className="mono" style={{ fontSize: 8.5, color: g.c }}>{({ "HEAT LOOP": "L", "ENERGY": "E", "FOOD & SOIL": "F", "CHARTER & ECOSYSTEM": "C", "ROBOTS": "R" }[g.t] || "X")}{i + 1}</div>
                    <div style={{ fontWeight: 700, fontSize: ".92rem", margin: "3px 0 6px" }}>{src2}</div>
                    <div style={{ fontSize: ".82rem", color: "#A9C8C8" }}>{find}</div>
                  </div>
                ))}
              </div>
            </Reveal>
          ))}
        </div>
      </section>
    </div>
  );
}

/* ───────────────────────── CROSS-SECTION (system page) ───────────────────────── */
function CrossSection() {
  return (
    <section style={{ padding: "5.5rem 5vw", background: "#07161C" }}>
      <div style={{ maxWidth: 1150, margin: "0 auto" }}>
        <Reveal>
          <Tag n="03" label="the ground" />
          <H2>Built for the 2080 climate.</H2>
        </Reveal>
        <Reveal>
          <svg viewBox="0 0 1000 360" style={{ width: "100%", marginTop: "2rem", display: "block" }}>
            <line x1="0" y1="200" x2="1000" y2="200" stroke="#DCE9EC" strokeWidth="2" opacity=".5" />
            <rect x="0" y="202" width="560" height="100" fill="#10333D" />
            <text x="20" y="258" className="mono" fontSize="11" fill="#6FB9C9">ICE-RICH PERMAFROST · KEPT FROZEN</text>
            <rect x="560" y="202" width="440" height="158" fill="#163137" />
            <g stroke="#2C5763" strokeWidth="1.5">{[600, 660, 720, 780, 840, 900, 960].map((x) => <line key={x} x1={x} y1="212" x2={x - 26} y2="350" />)}</g>
            <text x="760" y="258" className="mono" fontSize="11" fill="#9FC2C4">BEDROCK · FROND CORE</text>
            <rect x="0" y="302" width="560" height="58" fill="#0C2730" />
            <g>
              <path d="M96,200 C150,84 290,84 344,200" fill="#7FD8E8" opacity=".05" />
              <path d="M96,200 C150,84 290,84 344,200" fill="none" stroke="#9ED9A8" strokeWidth="1.8" />
              <path d="M104,200 C156,94 284,94 336,200" fill="none" stroke="#9ED9A8" strokeWidth="1" opacity=".35" />
              <text x="96" y="58" className="mono" fontSize="10" fill="#9ED9A8">GLASS COMMONS ENVELOPE — DOUBLE SKIN, SNOW-SHEDDING</text>
              <rect x="120" y="120" width="200" height="60" rx="6" fill="#0C2730" stroke="#F08A2C" strokeWidth="2" />
              <rect x="140" y="138" width="14" height="11" fill="#FFC97A" style={{ animation: REDUCE ? "none" : "glowP 4s infinite" }} />
              <rect x="170" y="138" width="14" height="11" fill="#FFC97A" style={{ animation: REDUCE ? "none" : "glowP 3s infinite" }} />
              {[150, 220, 290].map((x) => <line key={x} x1={x} y1="180" x2={x} y2="250" stroke="#9FC2C4" strokeWidth="5" />)}
              {[185, 255].map((x) => (
                <g key={x}>
                  <line x1={x} y1="170" x2={x} y2="270" stroke="#6FB9C9" strokeWidth="3" />
                  <path d={`M${x},268 V 188`} className="flowCold" strokeWidth="2.5" />
                  <circle cx={x} cy="166" r="7" fill="none" stroke="#6FB9C9" strokeWidth="2.5" />
                </g>
              ))}
              <text x="96" y="74" className="mono" fontSize="10" fill="#E8F1F2">HOMES INSIDE · PILES + THERMOSYPHONS BELOW (RAGLAN-PROVEN)</text>
            </g>
            <g>
              <rect x="360" y="158" width="180" height="30" rx="10" fill="none" stroke="#2C5763" strokeWidth="2.5" />
              {[395, 455, 515].map((x) => <line key={x} x1={x} y1="188" x2={x} y2="200" stroke="#2C5763" strokeWidth="4" />)}
              <path d="M368,168 H 532" className="flowHot" strokeWidth="3" />
              <path d="M368,179 H 532" className="flowCold" strokeWidth="3" />
              <text x="360" y="144" className="mono" fontSize="11" fill="#F08A2C">ELEVATED UTILIDOR</text>
            </g>
            <g>
              <rect x="640" y="128" width="240" height="72" rx="6" fill="#0C2730" stroke="#7FD8E8" strokeWidth="2" />
              {[660, 690, 720].map((x) => <rect key={x} x={x} y="148" width="16" height="12" rx="2" fill="#7FD8E8" style={{ animation: REDUCE ? "none" : "glowP 2.6s infinite" }} />)}
              <text x="640" y="112" className="mono" fontSize="11" fill="#7FD8E8">DATA HALLS — DIRECT ON ROCK</text>
            </g>
            {/* borehole field on bedrock */}
            <g>
              {[760, 790, 820, 850].map((x) => <line key={x} x1={x} y1="220" x2={x} y2="330" stroke="#F08A2C" strokeWidth="2.5" strokeDasharray="3 5" opacity=".8" />)}
              <text x="744" y="350" className="mono" fontSize="9" fill="#F08A2C">BOREHOLE HEAT BANK (DRAKE LANDING MODEL)</text>
            </g>
          </svg>
        </Reveal>
      </div>
    </section>
  );
}

/* ───────────────────────── FOOTER ───────────────────────── */
function Footer() {
  return (
    <footer style={{ padding: "3rem 5vw", background: "#07161C", borderTop: "1px solid #14323B" }}>
      <div style={{ maxWidth: 1150, margin: "0 auto" }}>
        <div className="mono" style={{ fontSize: 9, color: "#5E8B89", lineHeight: 2 }}>
          FERN · TOWN NAMES TO BE CHOSEN BY HOST COMMUNITIES<br />
          ALL CLAIMS SOURCED — SEE THE RESEARCH PAGE
        </div>
      </div>
    </footer>
  );
}

/* ───────────────────────── APP ───────────────────────── */
export default function App() {
  const [page, setPage] = useState("SYSTEM");
  useEffect(() => { window.scrollTo({ top: 0 }); }, [page]);
  return (
    <div className="pf">
      <style dangerouslySetInnerHTML={{ __html: GLOBAL_CSS }} />
      <Nav page={page} setPage={setPage} />
      {page === "SYSTEM" && (<><Hero /><LoopSection /><ModuleSection /><CrossSection /></>)}
      {page === "THE BIOME" && (<>
        <JumpChips items={[["DENIZENS", "sec-denizens"], ["ROBOTS", "sec-robots"], ["ENERGY", "sec-energy"], ["FOOD", "sec-food"]]} />
        <div id="sec-denizens" style={{ scrollMarginTop: 64 }}><DenizensPage /></div>
        <div id="sec-robots" style={{ scrollMarginTop: 64 }}><RobotsPage /></div>
        <div id="sec-energy" style={{ scrollMarginTop: 64 }}><EnergyPage /></div>
        <div id="sec-food" style={{ scrollMarginTop: 64 }}><FoodPage /></div>
      </>)}
      {page === "PLACE" && <SitesPage />}
      {page === "CHARTER" && (<>
        <JumpChips items={[["THE CHARTER", "sec-charter"], ["RESEARCH — THE RECEIPTS", "sec-research"]]} />
        <div id="sec-charter" style={{ scrollMarginTop: 64 }}><CharterPage /></div>
        <div id="sec-research" style={{ scrollMarginTop: 64 }}><ResearchPage /></div>
      </>)}
      <Footer />
    </div>
  );
}
