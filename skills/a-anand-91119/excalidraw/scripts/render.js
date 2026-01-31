#!/usr/bin/env node
/**
 * Excalidraw JSON → PNG renderer
 * Uses roughjs for hand-drawn style + resvg-js for SVG→PNG
 *
 * Features:
 *   - Auto-binding: arrows with startBinding/endBinding auto-connect to element edges
 *   - Simplified arrows: just specify "from" and "to" element IDs
 *   - All Excalidraw shape types: rectangle, ellipse, diamond, arrow, line, text, freedraw
 *
 * Usage:
 *   node render.js input.excalidraw output.png
 *   cat input.json | node render.js - output.png
 *   node render.js input.excalidraw  # outputs to input.png
 */

import { readFileSync } from "fs";
import { writeFileSync } from "fs";
import { resolve, basename, dirname, join } from "path";
import { JSDOM } from "jsdom";
import rough from "roughjs";
import { Resvg } from "@resvg/resvg-js";

// ── Config ──────────────────────────────────────────────
const SCALE = 2;
const PADDING = 50;
const ARROW_GAP = 8; // gap between arrow tip and element edge
const FONT_DIR = join(dirname(new URL(import.meta.url).pathname), "fonts");

// ── Font embedding ──────────────────────────────────────
function loadFontBase64(name) {
  try {
    const buf = readFileSync(join(FONT_DIR, name));
    return buf.toString("base64");
  } catch {
    return null;
  }
}

function fontFaceCSS() {
  const fonts = [];
  const virgil = loadFontBase64("Virgil.woff2");
  if (virgil) {
    fonts.push(`@font-face { font-family: "Virgil"; src: url("data:font/woff2;base64,${virgil}") format("woff2"); }`);
  }
  const cascadia = loadFontBase64("CascadiaCode.woff2");
  if (cascadia) {
    fonts.push(`@font-face { font-family: "Cascadia"; src: url("data:font/woff2;base64,${cascadia}") format("woff2"); }`);
  }
  return fonts.join("\n");
}

// ── Font family mapping ─────────────────────────────────
function getFontFamily(ff) {
  switch (ff) {
    case 1: return '"Virgil", "Segoe UI Emoji", sans-serif';
    case 2: return '"Helvetica", "Arial", sans-serif';
    case 3: return '"Cascadia", "Fira Code", monospace';
    default: return '"Virgil", sans-serif';
  }
}

// ── Parse input ─────────────────────────────────────────
function parseInput(inputPath) {
  let raw;
  if (inputPath === "-") {
    raw = readFileSync(0, "utf-8");
  } else {
    raw = readFileSync(resolve(inputPath), "utf-8");
  }
  const data = JSON.parse(raw);
  if (Array.isArray(data)) return { elements: data };
  return data;
}

// ── Element geometry helpers ────────────────────────────

/** Get the bounding box of a shape element */
function getElementBBox(el) {
  const x = el.x ?? 0;
  const y = el.y ?? 0;
  const w = el.width ?? 0;
  const h = el.height ?? 0;
  return { x, y, w, h, cx: x + w / 2, cy: y + h / 2 };
}

/**
 * Find the intersection point where a line from center to an external point
 * crosses the element's boundary. Works for rectangles, ellipses, and diamonds.
 */
function getEdgePoint(el, targetX, targetY) {
  const { x, y, w, h, cx, cy } = getElementBBox(el);
  const dx = targetX - cx;
  const dy = targetY - cy;

  if (dx === 0 && dy === 0) return { x: cx, y: cy };

  const type = el.type || "rectangle";

  if (type === "ellipse") {
    // Ellipse intersection: parametric
    const a = w / 2;
    const b = h / 2;
    const angle = Math.atan2(dy, dx);
    return {
      x: cx + a * Math.cos(angle),
      y: cy + b * Math.sin(angle),
    };
  }

  if (type === "diamond") {
    // Diamond (rhombus) intersection
    const a = w / 2;
    const b = h / 2;
    const adx = Math.abs(dx);
    const ady = Math.abs(dy);
    // Line from center to edge of diamond
    const t = 1 / (adx / a + ady / b);
    return {
      x: cx + dx * t,
      y: cy + dy * t,
    };
  }

  // Rectangle intersection
  const a = w / 2;
  const b = h / 2;
  const adx = Math.abs(dx);
  const ady = Math.abs(dy);

  let scale;
  if (adx * b > ady * a) {
    // Hits left or right edge
    scale = a / adx;
  } else {
    // Hits top or bottom edge
    scale = b / ady;
  }

  return {
    x: cx + dx * scale,
    y: cy + dy * scale,
  };
}

// ── Arrow binding resolution ────────────────────────────

/**
 * Pre-process elements: resolve arrow bindings.
 * 
 * Supports two binding formats:
 * 
 * 1. Excalidraw-native: startBinding: { elementId: "id" }, endBinding: { elementId: "id" }
 * 2. Simplified: "from": "elementId", "to": "elementId" (we add as a convenience)
 * 
 * When binding is present, the arrow's x/y and points are recalculated to connect
 * the edges of the source and target elements.
 */
function resolveBindings(elements) {
  // Build element lookup by id
  const byId = new Map();
  for (const el of elements) {
    if (el.id) byId.set(el.id, el);
  }

  for (const el of elements) {
    if (el.type !== "arrow" && el.type !== "line") continue;

    // Get binding element IDs from either format
    const startId = el.from || el.startBinding?.elementId || null;
    const endId = el.to || el.endBinding?.elementId || null;

    if (!startId && !endId) continue;

    const startEl = startId ? byId.get(startId) : null;
    const endEl = endId ? byId.get(endId) : null;

    // We need at least one binding to recalculate
    if (!startEl && !endEl) continue;

    // Get centers
    const startBBox = startEl ? getElementBBox(startEl) : null;
    const endBBox = endEl ? getElementBBox(endEl) : null;

    // Determine start and end points
    let sx, sy, ex, ey;

    if (startEl && endEl) {
      // Both bound: arrow goes from edge of start to edge of end
      // First get centers for direction calculation
      const sCx = startBBox.cx;
      const sCy = startBBox.cy;
      const eCx = endBBox.cx;
      const eCy = endBBox.cy;

      // Get edge points
      const sEdge = getEdgePoint(startEl, eCx, eCy);
      const eEdge = getEdgePoint(endEl, sCx, sCy);

      // Apply gap
      const angle = Math.atan2(eCy - sCy, eCx - sCx);
      sx = sEdge.x + ARROW_GAP * Math.cos(angle);
      sy = sEdge.y + ARROW_GAP * Math.sin(angle);
      ex = eEdge.x - ARROW_GAP * Math.cos(angle);
      ey = eEdge.y - ARROW_GAP * Math.sin(angle);
    } else if (startEl) {
      // Only start bound: use existing end point
      const pts = el.points || [[0, 0], [100, 0]];
      const lastPt = pts[pts.length - 1];
      ex = (el.x ?? 0) + lastPt[0];
      ey = (el.y ?? 0) + lastPt[1];
      const sEdge = getEdgePoint(startEl, ex, ey);
      const angle = Math.atan2(ey - startBBox.cy, ex - startBBox.cx);
      sx = sEdge.x + ARROW_GAP * Math.cos(angle);
      sy = sEdge.y + ARROW_GAP * Math.sin(angle);
    } else {
      // Only end bound: use existing start point
      sx = el.x ?? 0;
      sy = el.y ?? 0;
      const eEdge = getEdgePoint(endEl, sx, sy);
      const angle = Math.atan2(endBBox.cy - sy, endBBox.cx - sx);
      ex = eEdge.x - ARROW_GAP * Math.cos(angle);
      ey = eEdge.y - ARROW_GAP * Math.sin(angle);
    }

    // Check for waypoints (intermediate points beyond simple start/end)
    if (el.points && el.points.length > 2) {
      // Multi-segment arrow with waypoints.
      // Waypoints can be specified as:
      //   a) Relative to arrow's x,y (Excalidraw native format)
      //   b) Absolute positions if "absolutePoints" flag is set (convenience)
      const pts = el.points;
      const oldX = el.x ?? 0;
      const oldY = el.y ?? 0;

      let absPoints;
      if (el.absolutePoints) {
        // Points are already absolute coordinates
        absPoints = pts.map(([px, py]) => [px, py]);
      } else {
        // Convert relative points to absolute
        absPoints = pts.map(([px, py]) => [oldX + px, oldY + py]);
      }

      // Replace first/last with bound edge points
      if (startEl) {
        // Recalculate start edge toward the second waypoint (not the end element)
        const nextPt = absPoints[1];
        const sEdge2 = getEdgePoint(startEl, nextPt[0], nextPt[1]);
        const angle2 = Math.atan2(nextPt[1] - startBBox.cy, nextPt[0] - startBBox.cx);
        absPoints[0] = [sEdge2.x + ARROW_GAP * Math.cos(angle2), sEdge2.y + ARROW_GAP * Math.sin(angle2)];
      }
      if (endEl) {
        // Recalculate end edge from the second-to-last waypoint
        const prevPt = absPoints[absPoints.length - 2];
        const eEdge2 = getEdgePoint(endEl, prevPt[0], prevPt[1]);
        const angle2 = Math.atan2(endBBox.cy - prevPt[1], endBBox.cx - prevPt[0]);
        absPoints[absPoints.length - 1] = [eEdge2.x - ARROW_GAP * Math.cos(angle2), eEdge2.y - ARROW_GAP * Math.sin(angle2)];
      }

      // New origin is first point, rest relative
      el.x = absPoints[0][0];
      el.y = absPoints[0][1];
      el.points = absPoints.map(([ax, ay]) => [ax - el.x, ay - el.y]);
    } else {
      // Simple two-point arrow
      el.x = sx;
      el.y = sy;
      el.points = [[0, 0], [ex - sx, ey - sy]];
    }
  }

  return elements;
}

// ── Bounding box ────────────────────────────────────────
function computeBounds(elements) {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const el of elements) {
    if (el.isDeleted) continue;
    const x = el.x ?? 0;
    const y = el.y ?? 0;
    const w = el.width ?? 0;
    const h = el.height ?? 0;

    if (el.points && el.points.length) {
      for (const [px, py] of el.points) {
        minX = Math.min(minX, x + px);
        minY = Math.min(minY, y + py);
        maxX = Math.max(maxX, x + px);
        maxY = Math.max(maxY, y + py);
      }
    } else {
      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x + w);
      maxY = Math.max(maxY, y + h);
    }
  }
  return { minX, minY, maxX, maxY };
}

// ── Roughjs options from element ────────────────────────
function roughOpts(el) {
  const opts = {
    stroke: el.strokeColor || "#1e1e1e",
    strokeWidth: el.strokeWidth ?? 2,
    roughness: el.roughness ?? 1,
    seed: el.seed ?? Math.floor(Math.random() * 2 ** 31),
    bowing: 1,
  };

  if (el.backgroundColor && el.backgroundColor !== "transparent") {
    opts.fill = el.backgroundColor;
    opts.fillStyle = el.fillStyle || "hachure";
    opts.fillWeight = (el.strokeWidth ?? 2) / 2;
    opts.hachureGap = 4;
  }

  if (el.strokeStyle === "dashed") {
    opts.strokeLineDash = [8, 6];
  } else if (el.strokeStyle === "dotted") {
    opts.strokeLineDash = [2, 4];
  }

  if (el.roughness === 0) opts.roughness = 0;
  return opts;
}

// ── Arrow head ──────────────────────────────────────────
function drawArrowHead(svgEl, doc, tipX, tipY, fromX, fromY, color, strokeWidth) {
  const angle = Math.atan2(tipY - fromY, tipX - fromX);
  const headLen = 12 + strokeWidth * 2;
  const headAngle = Math.PI / 6;

  const x1 = tipX - headLen * Math.cos(angle - headAngle);
  const y1 = tipY - headLen * Math.sin(angle - headAngle);
  const x2 = tipX - headLen * Math.cos(angle + headAngle);
  const y2 = tipY - headLen * Math.sin(angle + headAngle);

  const path = doc.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", `M ${x1} ${y1} L ${tipX} ${tipY} L ${x2} ${y2}`);
  path.setAttribute("stroke", color);
  path.setAttribute("stroke-width", String(strokeWidth));
  path.setAttribute("fill", "none");
  path.setAttribute("stroke-linecap", "round");
  path.setAttribute("stroke-linejoin", "round");
  svgEl.appendChild(path);
}

// ── Render elements ─────────────────────────────────────
function renderElements(elements, svgEl, rc, doc, offsetX, offsetY) {
  const sorted = [...elements].filter(e => !e.isDeleted);

  for (const el of sorted) {
    const x = (el.x ?? 0) + offsetX;
    const y = (el.y ?? 0) + offsetY;
    const w = el.width ?? 0;
    const h = el.height ?? 0;
    const opts = roughOpts(el);

    const g = doc.createElementNS("http://www.w3.org/2000/svg", "g");
    if (el.opacity != null && el.opacity !== 100) {
      g.setAttribute("opacity", String(el.opacity / 100));
    }
    if (el.angle) {
      const cx = x + w / 2;
      const cy = y + h / 2;
      g.setAttribute("transform", `rotate(${(el.angle * 180) / Math.PI} ${cx} ${cy})`);
    }

    switch (el.type) {
      case "rectangle": {
        const rOpts = { ...opts };
        if (el.roundness) {
          // roughjs doesn't support rounded rect natively, approximate with slightly lower roughness
          rOpts.roughness = Math.max(0, (rOpts.roughness ?? 1) - 0.3);
        }
        const node = rc.rectangle(x, y, w, h, rOpts);
        g.appendChild(node);
        break;
      }
      case "ellipse": {
        const cx = x + w / 2;
        const cy = y + h / 2;
        const node = rc.ellipse(cx, cy, w, h, opts);
        g.appendChild(node);
        break;
      }
      case "diamond": {
        const cx = x + w / 2;
        const cy = y + h / 2;
        const points = [[cx, y], [x + w, cy], [cx, y + h], [x, cy]];
        const node = rc.polygon(points, opts);
        g.appendChild(node);
        break;
      }
      case "line":
      case "arrow": {
        const pts = el.points || [[0, 0]];
        if (pts.length >= 2) {
          const absPoints = pts.map(([px, py]) => [x + px, y + py]);
          const lineOpts = { ...opts };
          delete lineOpts.fill;
          delete lineOpts.fillStyle;

          if (pts.length === 2) {
            const node = rc.line(absPoints[0][0], absPoints[0][1], absPoints[1][0], absPoints[1][1], lineOpts);
            g.appendChild(node);
          } else {
            const node = rc.linearPath(absPoints, lineOpts);
            g.appendChild(node);
          }

          if (el.type === "arrow") {
            const last = absPoints[absPoints.length - 1];
            const prev = absPoints[absPoints.length - 2];
            drawArrowHead(g, doc, last[0], last[1], prev[0], prev[1], opts.stroke, opts.strokeWidth);

            if (el.startArrowhead) {
              const first = absPoints[0];
              const next = absPoints[1];
              drawArrowHead(g, doc, first[0], first[1], next[0], next[1], opts.stroke, opts.strokeWidth);
            }
          }
        }
        break;
      }
      case "freedraw": {
        if (el.points && el.points.length > 1) {
          let d = `M ${x + el.points[0][0]} ${y + el.points[0][1]}`;
          for (let i = 1; i < el.points.length; i++) {
            d += ` L ${x + el.points[i][0]} ${y + el.points[i][1]}`;
          }
          const path = doc.createElementNS("http://www.w3.org/2000/svg", "path");
          path.setAttribute("d", d);
          path.setAttribute("stroke", el.strokeColor || "#1e1e1e");
          path.setAttribute("stroke-width", String(el.strokeWidth ?? 2));
          path.setAttribute("fill", "none");
          path.setAttribute("stroke-linecap", "round");
          path.setAttribute("stroke-linejoin", "round");
          g.appendChild(path);
        }
        break;
      }
      case "text": {
        const textEl = doc.createElementNS("http://www.w3.org/2000/svg", "text");
        textEl.setAttribute("x", String(x));
        textEl.setAttribute("fill", el.strokeColor || "#1e1e1e");
        textEl.setAttribute("font-family", getFontFamily(el.fontFamily));
        textEl.setAttribute("font-size", String(el.fontSize || 20));
        textEl.setAttribute("dominant-baseline", "text-before-edge");

        const align = el.textAlign || "left";
        if (align === "center") {
          textEl.setAttribute("x", String(x + w / 2));
          textEl.setAttribute("text-anchor", "middle");
        } else if (align === "right") {
          textEl.setAttribute("x", String(x + w));
          textEl.setAttribute("text-anchor", "end");
        }

        const lines = (el.text || "").split("\n");
        const lineHeight = (el.fontSize || 20) * 1.25;
        const totalHeight = lines.length * lineHeight;
        const vAlign = el.verticalAlign || "top";
        let startY = y;
        if (vAlign === "middle") {
          startY = y + (h - totalHeight) / 2;
        }

        lines.forEach((line, i) => {
          const tspan = doc.createElementNS("http://www.w3.org/2000/svg", "tspan");
          tspan.setAttribute("x", textEl.getAttribute("x"));
          tspan.setAttribute("dy", i === 0 ? String(startY - y) : String(lineHeight));
          tspan.setAttribute("y", i === 0 ? String(startY) : "");
          if (i > 0) tspan.removeAttribute("y");
          tspan.textContent = line;
          textEl.appendChild(tspan);
        });

        g.appendChild(textEl);
        break;
      }
      case "image": {
        const rect = rc.rectangle(x, y, w, h, { ...opts, fill: "#f0f0f0", fillStyle: "solid" });
        g.appendChild(rect);
        const txt = doc.createElementNS("http://www.w3.org/2000/svg", "text");
        txt.setAttribute("x", String(x + w / 2));
        txt.setAttribute("y", String(y + h / 2));
        txt.setAttribute("text-anchor", "middle");
        txt.setAttribute("dominant-baseline", "central");
        txt.setAttribute("font-size", "14");
        txt.setAttribute("fill", "#999");
        txt.textContent = "[image]";
        g.appendChild(txt);
        break;
      }
    }

    svgEl.appendChild(g);
  }
}

// ── Main ────────────────────────────────────────────────
function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error("Usage: render.js <input.excalidraw|-> [output.png]");
    process.exit(1);
  }

  const inputPath = args[0];
  let outputPath = args[1];

  if (!outputPath) {
    if (inputPath === "-") {
      outputPath = "output.png";
    } else {
      outputPath = resolve(dirname(inputPath), basename(inputPath).replace(/\.[^.]+$/, "") + ".png");
    }
  }

  let data;
  try {
    data = parseInput(inputPath);
  } catch (err) {
    console.error(`Failed to parse input: ${err.message}`);
    process.exit(1);
  }

  let elements = data.elements || [];
  if (elements.length === 0) {
    console.error("No elements found in input");
    process.exit(1);
  }

  // ── Resolve arrow bindings ──────────────────────────
  elements = resolveBindings(elements);

  // ── Compute bounds ──────────────────────────────────
  const bounds = computeBounds(elements);
  const width = bounds.maxX - bounds.minX + PADDING * 2;
  const height = bounds.maxY - bounds.minY + PADDING * 2;
  const offsetX = -bounds.minX + PADDING;
  const offsetY = -bounds.minY + PADDING;

  // ── Create SVG ──────────────────────────────────────
  const dom = new JSDOM("<!DOCTYPE html><html><body></body></html>");
  const doc = dom.window.document;

  const svgEl = doc.createElementNS("http://www.w3.org/2000/svg", "svg");
  svgEl.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  svgEl.setAttribute("width", String(Math.ceil(width)));
  svgEl.setAttribute("height", String(Math.ceil(height)));
  svgEl.setAttribute("viewBox", `0 0 ${Math.ceil(width)} ${Math.ceil(height)}`);

  const bgColor = data.appState?.viewBackgroundColor || "#ffffff";
  const bgRect = doc.createElementNS("http://www.w3.org/2000/svg", "rect");
  bgRect.setAttribute("width", "100%");
  bgRect.setAttribute("height", "100%");
  bgRect.setAttribute("fill", bgColor);
  svgEl.appendChild(bgRect);

  const style = doc.createElementNS("http://www.w3.org/2000/svg", "style");
  style.textContent = fontFaceCSS();
  svgEl.appendChild(style);

  const rc = rough.svg(svgEl);
  renderElements(elements, svgEl, rc, doc, offsetX, offsetY);

  const svgString = svgEl.outerHTML;

  // ── Render PNG ──────────────────────────────────────
  const fontFiles = [];
  try { fontFiles.push(join(FONT_DIR, "Virgil.ttf")); } catch {}
  try { fontFiles.push(join(FONT_DIR, "CascadiaCode.ttf")); } catch {}

  const resvgOpts = {
    fitTo: { mode: "zoom", value: SCALE },
    font: {
      fontFiles,
      loadSystemFonts: true,
      defaultFontFamily: "Virgil",
    },
    logLevel: "off",
  };

  try {
    const resvg = new Resvg(svgString, resvgOpts);
    const pngData = resvg.render();
    const pngBuffer = pngData.asPng();
    writeFileSync(resolve(outputPath), pngBuffer);
    console.log(`✓ Rendered ${elements.length} elements → ${outputPath} (${Math.ceil(width * SCALE)}×${Math.ceil(height * SCALE)}px)`);
  } catch (err) {
    console.error(`Failed to render PNG: ${err.message}`);
    process.exit(1);
  }
}

main();
