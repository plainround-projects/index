# Drawing kit for the README diagrams

Every repository gets two drawings in its README: an architecture figure and a flow figure of one run. This page is all you need to draw them. Copy a template, change the coordinates and the words, run the checker.

Worked examples, finished and on GitHub: `kafka-order-events`, `ai-cited-answers` and `gcp-landing-zone-slice`, each under `docs/diagrams/`. Open one when a rule here is not clear. `pilot/` holds their screenshots.

## 1. What you produce

| File | What |
| --- | --- |
| `docs/diagrams/architecture.svg` | The components and how they connect. Drawn by hand. |
| `docs/diagrams/flow.svg` | One run or request, as numbered steps. Drawn by hand. |
| `docs/diagrams/architecture-dark.svg`, `flow-dark.svg` | The dark twins. Never edit these: `check.py --write-dark` writes them. |
| `README.md` | Two new sections (Section 8). |
| `ARCHITECTURE.md` | One line pointing at the figures. The Mermaid block stays. |
| `CHANGELOG.md` | One line under `## [Unreleased]`. |

Order of work: read (Section 2), draw both light files (Sections 3 to 7), edit the Markdown (Section 8), check and push (Section 9).

## 2. Read before you draw

Read the repository's `README.md`, all of `ARCHITECTURE.md`, and the code its walk-through names. Then:

- **Names come from `ARCHITECTURE.md` and the code, spelled exactly.** `order-events`, `HybridRetriever`, `prod-data-sensitive`. No invented parts. No part the walk-through names may be missing.
- **Every number on a drawing is in the repository:** partition counts, thresholds, CIDR ranges, measured results. Use the numbers the README states, and do not round them differently.
- **The failure path is the one the lesson teaches.** Take it from the section "Failure modes the lesson teaches". Pick the one the lesson is about, two at most. Do not draw every row of that table.
- **Do not trust the prose over the code.** Check each edge you draw against the code: who calls whom, and which library does the work. Where `ARCHITECTURE.md` and the code disagree, draw what the code does and list the disagreement in your report. Do not fix the prose or the code in this job.
- **The walk-through's step numbers are the flow's step numbers.** Step 4 in `ARCHITECTURE.md` is circle 4 in the drawing.
- **No Mermaid block?** Four repositories have no Mermaid `flowchart` (`ai-event-driven-ai-worker`, `ai-ship-an-ai-service`, `ai-streaming-assistant-latency-budget`, `payments-secure-open-banking`). Their section "Data flow" still has the steps, as a list or a text figure. Draw from that and the components table. Keep any Mermaid block that is there, and put the pointer line under the "Data flow" heading all the same.
- **Not a service?** Some repositories are a pipeline, a set of documents or infrastructure. The same two drawings still apply. Architecture: the stages, documents or resources and what connects them. Flow: the one run the walk-through follows, even if that run is `make run` or `terraform apply`.

## 3. Theme: two files, one drawing

GitHub shows a README on white (`#ffffff`) or near black (`#0d1117`). **We use two files switched by a `<picture>` element with `prefers-color-scheme`.**

Why not one palette for both: on a transparent background it cannot be done. Text needs 4.5 to 1 on both backgrounds. That means a luminance of at most 0.183 for white and at least 0.2 for `#0d1117`. No color is both, and the best any color reaches is about 4.35 to 1.

So each file carries its own opaque paper, and the palette is one line of CSS variables. You draw only the light file. `check.py --write-dark` swaps that line and writes the twin, so a drawing is never edited twice. The paper is opaque, so a viewer that ignores `<picture>` still shows a readable card.

## 4. The canvas, palette and type

Start by copying the whole template file (`cp tools/diagrams/template-architecture.svg <repo>/docs/diagrams/architecture.svg`, and the same for the flow), then edit only the root's size, `<title>`, `<desc>` and everything after `</defs>`. **The `<style>` and `<defs>` blocks stay unchanged; the checker compares them byte for byte.** Any color or size you want is already a class. If you think you need a new one, you do not: change the layout.

- **Canvas:** 1200 wide, as tall as it needs, set in `width`, `height` and `viewBox` together. Two rects draw the paper: `class="paper"` (height H-1) and `class="grid"` (height H-2). Margin 48 on the left and right.
- **Head:** `<text class="title" x="48" y="68">` in the serif, then `<text class="caption" x="48" y="100">`, one mono line of at most 115 characters on what to look at. Content starts at y=128.
- **Legend:** the last row, at y = H-44, the same x positions as the template. Delete the items the drawing does not use and leave the others where they are.
- **Root:** keep `role="img"` and `aria-labelledby="t d"`. `<title>` names the figure. `<desc>` tells the whole picture in words, like a reader with no image would need.

| Token | Light | Dark | Use |
| --- | --- | --- | --- |
| `--paper` | `#ffffff` | `#0d1117` | the card |
| `--ink` | `#10243d` | `#f5f4f8` | names, main text |
| `--mute` | `#52677f` | `#9a96ab` | details, boundaries, stores, reads |
| `--accent` | `#0a6aa8` | `#6ec8ff` | services and the path that works |
| `--good` | `#19743f` | `#7ce0a1` | the result the run should end in |
| `--warn` | `#8a5a00` | `#ffd166` | the failure path the lesson teaches |

These are the Plainround figure tokens, so repositories and lessons look like one family. The checker fails a palette color under 4.5 to 1 on its paper.

| Class | Size | Characters that fit in 100 px | For |
| --- | --- | --- | --- |
| `title` | 36 serif | | the headline, sentence case |
| `caption` | 16 | 10.4 | the line under it |
| `name` | 20 bold | 8.3 | a node's name |
| `lane` | 17 bold | 9.8 | a swimlane header |
| `sub` | 15 | 11.1 | a detail line in a node or a step |
| `label` | 15 | 11.1 | text on an edge; add a tone class |
| `tag` | 15 | 11.1 | a boundary's name |
| `num` | 15 bold | | the number in a step circle |
| `legend` | 14 | | legend text only |

The mono font is 0.6 of its size wide: 20 px is 12 px per character, 15 px is 9 px. **Count characters before you place text.** Tone classes for text: `t-accent`, `t-good`, `t-warn`, `t-ink`; `b` makes it bold. Example: `class="label b t-warn"`.

Fixed rules: every label is real `<text>`, one line per element, 14 px or more. No `<tspan>`, no `transform`, no `style` attribute, no `<image>`, `<use>`, filters or gradients, no drop shadows, no hex color outside the palette line, no external reference. Do not write words as paths. Fonts are system stacks because an SVG inside `<img>` cannot load a web font. A file stays under 150 kB; the pilots are about 10 kB.

## 5. Shapes

Copy these. `x`, `y`, `w` and `h` are yours.

```xml
<!-- Service: anything that runs. Name at y+32, detail lines 24 then 22 lower. Text starts at x+16. -->
<rect class="svc" x="412" y="360" width="292" height="84" rx="12"/>
<text class="name" x="428" y="392">Group coordinator</text>
<text class="sub" x="428" y="416">the broker: runs rebalances</text>

<!-- Store: a database, table, bucket, file set. Cylinder: M x y+ry, a w/2 ry 0 0 1 w 0, v body, a w/2 ry 0 0 1 -w 0, z; the rim repeats the top arc. -->
<path class="store" d="M412 488a146 12 0 0 1 292 0v64a146 12 0 0 1 -292 0z"/>
<path class="rim" d="M412 488a146 12 0 0 0 292 0"/>
<text class="name" x="558" y="528" text-anchor="middle">__consumer_offsets</text>
<text class="sub" x="558" y="550" text-anchor="middle">committed offsets</text>

<!-- Queue or topic: a service rect with one slot per partition (or three unnumbered slots for a queue). -->
<rect class="svc" x="412" y="176" width="292" height="120" rx="12"/>
<rect class="slot" x="428" y="244" width="38" height="36" rx="5"/>
<text class="label t-accent" x="447" y="267" text-anchor="middle">0</text>

<!-- External actor: a person, a client, a machine or system outside the build. rx is half the height. -->
<rect class="actor" x="48" y="176" width="168" height="72" rx="36"/>
<text class="name" x="132" y="208" text-anchor="middle">Reader</text>
<text class="sub" x="132" y="230" text-anchor="middle">POST /ask</text>

<!-- Boundary: a container, cluster, cloud project, folder. Tag 28 below the top, 16 in. -->
<rect class="boundary" x="392" y="132" width="332" height="456" rx="14"/>
<text class="tag" x="408" y="160">Single-node Kafka 4 in a container</text>

<!-- Trust zone: a boundary that enforces something, such as a perimeter. At most one per drawing. -->
<rect class="zone" x="580" y="272" width="324" height="224" rx="14"/>
<text class="tag b t-accent" x="596" y="298">Perimeter sensitive_data</text>

<!-- Failure note: what goes wrong and the command that shows it. Good spot: empty space near the failure edge. -->
<rect class="note" x="48" y="340" width="300" height="124" rx="10"/>
<text class="label b t-warn" x="64" y="370">make run-unkeyed</text>
<text class="sub" x="64" y="396">no key: one order's events</text>

<!-- Result box: the line the run ends on, in a flow. -->
<rect class="win" x="424" y="708" width="300" height="40" rx="10"/>
<text class="label b t-good" x="440" y="733">out-of-order events logged: 0</text>

<!-- A small chip, for a short list inside a boundary (policies, stages): a slot with a label. -->
<rect class="slot" x="204" y="178" width="87" height="32" rx="6"/>
<text class="label t-accent" x="247" y="199" text-anchor="middle">no keys</text>
```

A rect with class `svc`, `note`, `win` or `actor` must hold its text: the checker fails a line that spills out. Text in a cylinder has no such check, so keep it 16 px inside the sides and above the bottom curve. Size a cylinder from its text: width at least the longest line plus 32, body height 26 per line plus 24. With `y` the top of the shape, the straight sides run from y + ry to y + ry + body, and the lowest point is y + 2 ry + body.

## 6. Edges

Each edge is one `<path class="..." d="..."/>`; the class carries the stroke and the arrowhead. **Draw edges after the nodes.** Use `H` and `V`, and round a corner with `Q` and a 12 px radius: `M992 300H892Q880 300 880 312V374`. No diagonal lines.

| Class | Looks | Means | The arrow points |
| --- | --- | --- | --- |
| `sync` | solid accent | a call that waits for an answer | from caller to callee |
| `async` | dashed accent, open head | a message: sent and not waited for | the way the message travels |
| `read` | dotted neutral, open head | reading data with no change | from the data to the reader |
| `fail` | solid warning, thick | the failure path the lesson teaches | the way the failure goes |
| `ok` | solid success | the result handed back | to whoever receives it |

`<path class="stop" d="M904 408V432"/>` is a short thick bar across a `fail` edge, at the place the request is refused.

Text on an edge: `class="label t-accent"` (or `t-warn`, `t-good`), 10 to 12 px above the line, starting 8 to 12 px past the node. Reads use plain `label`. Keep labels to a method, a key or a few words.

Layout habits that kept the pilots clean:

- **Check every label against every line.** The checker sees text over text, not text over a line. A label must not sit on a boundary stroke or a lifeline: leave a gap between columns as wide as the longest label, or split the label over two lines, one above the edge and one below.
- **No crossings.** Reorder the nodes first. If two sources each feed the same two targets, put one target between the sources (`ai-cited-answers`: `Embedder` sits between `HybridRetriever` and `ingest`, so both reach it and the store without crossing).
- **Fan-out:** give each branch its own vertical. Two dashed paths that share a stretch show a tick where they part.
- **One edge from a boundary** stands for all members, for example `heartbeat, commit` leaves the group's box, not each consumer.
- **Arrow ends:** stop on the node's edge. On a cylinder, stop on its top (y) or on a straight side, never on the curved corners.
- **Whitespace is fine.** Leave it, or use it for a failure note. Do not add parts to fill it.

## 7. The two drawings

### Architecture: `template-architecture.svg`

Left to right in the direction the data moves: who starts things on the left, boundaries in the middle, what is read or written on the right. Stack downwards when a column is full. Three to five columns on a grid of 8; a column of nodes is 200 to 300 wide with at least 120 between columns where a label sits. Draw every boundary the walk-through crosses (container, cluster, project, trust zone) and everything named in the component table that a run touches. Helpers that nothing teaches (logging, settings, retry) stay off, or go in a detail line.

Typical size: 1200 by 800 to 900.

### Flow: `template-flow.svg`

A swimlane sequence, not a second architecture. The geometry is fixed, so copy it.

- **Lanes:** three to five headers at y=128, height 48, starting right of x=396. Lane centers about 150 apart, for example 460, 610, 770, 940, 1088. A header is 120 to 170 wide: the name's characters times 10.2, plus 28. Same shape as in the architecture: `actor` or `svc`, class `lane` for the text. A long name takes two lines at y=148 and y=168. Only the parts the walk-through touches get a lane. Merge the rest: `POST /ask` stands for the reader and the HTTP layer, and several tables of one database share one lane named after the database, with the table's name on the edge or in the row text.
- **Lifelines:** one `<path class="hair">` with `M<x> 176V<end>` per lane. End each one below the last row that uses it.
- **Rail:** `<path class="hair" d="M66 216V<last row>"/>`.
- **Rows:** the first at y=216, one every 64. A row is a circle at x=66, a bold line at x=96 (y-4), a detail at x=96 (y+16), and its message at y on the right. Row text ends before x=420: at most 33 characters of `sub`. A row with a third line needs 16 more before the next row.
- **Message:** an edge from lane to lane, label above it. Keep the label inside the gap between lifelines (about 16 characters in a gap of 150), or put a `mask` rect behind it when it must cross one: `<rect class="mask" x="782" y="330" width="366" height="26" rx="4"/>`. A step on one lane is a `slot` rect 12 wide and 36 tall on the lifeline, with its label to the right.
- **Numbering:** `dot` and white number for a normal step, `dot-g` for the step that ends well, `dot-w` for a failure. A failure that branches off step 3 is a new row marked `3x`, placed right after step 3, with its bold line in `t-warn`. If a step of the walk-through is the failure itself, it keeps its number and turns `dot-w`. Two outcomes of one step are `3a` and `3b`.
- **Failure branch:** `fail` edges and `t-warn` labels. When a failure shows up later than its cause, draw both rows and join them with one `fail` path (`kafka-order-events`: `3x` to `6x`).
- **End:** the last row ends in a `win` box with the words the run prints, or the outcome, when the walk-through has one. Put it on that row, in free lane space, joined by an `ok` edge where the row has a lane to join. Do not float it below the rows.

Typical size: 1200 by 700 to 840; a row is 64, so ten rows make about 940, which is fine. More than ten rows: merge neighbors that touch the same lanes, and say so in your report.

## 8. The Markdown

In `README.md`, insert these two sections **right after the opening block**, that is after the opening paragraph and its table of Lesson, Planned hours and so on, before the first existing `## ` heading. They must be the first two `## ` sections.

```markdown
## Architecture

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/diagrams/architecture-dark.svg">
  <img alt="ALT TEXT" src="docs/diagrams/architecture.svg">
</picture>

ONE SENTENCE on what to notice.

## How one run flows

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/diagrams/flow-dark.svg">
  <img alt="ALT TEXT" src="docs/diagrams/flow.svg">
</picture>

ONE SENTENCE on what the run does and what the warning rows show.
```

- Keep the attributes in exactly that order: the checker reads them with a pattern. No double quotes inside the alt text.
- Alt text: one or two sentences of what the figure says, with the real names. Not "architecture diagram".
- Call the warning color "amber" if the sentence mentions it.

In `ARCHITECTURE.md`, add one line under the heading that holds the Mermaid block or the data flow, with a blank line on each side. The Mermaid block stays as it is.

```markdown
Drawn versions of this figure and of the walk-through: [the architecture](docs/diagrams/architecture.svg) and [one run](docs/diagrams/flow.svg).
```

In `CHANGELOG.md`, add above the newest version (or to an existing `## [Unreleased]`):

```markdown
## [Unreleased]

### Added

- Drawn architecture and flow figures in `docs/diagrams/`, light and dark, shown in the README.
```

## 9. Check, look once, push

From `/Users/sumitsrivastava/Code/plainround-projects`:

```bash
python3 tools/diagrams/check.py --write-dark <repo>
```

Rerun that after every edit of a light file, until it prints `0 problems`. It checks the viewBox, the 14 px floor, embedded or external content, the 150 kB limit, the copied style and defs, text over text, text off the canvas or out of its box, the dark twin, the README and the `ARCHITECTURE.md` line. It cannot see a label on a line, a clipped cylinder or a wrong arrow. So look once, in headless Chrome, at the width GitHub uses:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --window-size=1200,<H> --screenshot=<scratch>/shot.png "file://$PWD/<repo>/docs/diagrams/architecture.svg"
```

Read the picture for: a label touching a line, text clipped by a shape, an arrow that means the wrong thing, an edge that crosses another. One look per drawing, one fix pass, then stop. If you changed only words or a few coordinates, the checker is enough for the second pass.

Commit and push only the files of this job:

```bash
git -C <repo> add docs/diagrams README.md ARCHITECTURE.md CHANGELOG.md
gitleaks git --staged <repo>
git -C <repo> commit -m "docs: add drawn architecture and flow figures to the README"
git -C <repo> push origin main
```

Never force-push. `git status` must show nothing else from this job. Files that were already modified or untracked before you started are not yours: leave them and say so.

Report per repository: the commit hash, and anything in `ARCHITECTURE.md` that disagreed with the code.
