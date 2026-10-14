const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");
const { applyTheme } = require("/root/.claude/skills/synced/ff5b1d5d-d175-46b8-b3f4-e64212c4048a_9e04934e-b6f0-41f6-a6be-94a773705624/pptx/scripts/apply_theme.js");

const IMG = path.join(__dirname, "..", "img");
const OUT = path.join(__dirname, "HeatCast_NCR_Presentation.pptx");
const SCRIPT = path.join(__dirname, "script.json");

const THEME = {
  name: "HeatCast NCR",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "2E1406", lt1: "FFFFFF", dk2: "A63A0C", lt2: "FBF4EC",
    accent1: "A63A0C", accent2: "F28C28", accent3: "F2C14E", accent4: "C0392B",
    accent5: "6F5C51", accent6: "4C9BE8", hlink: "A63A0C", folHlink: "6F5C51",
  },
};
const HEX = { dark: "2E1406", burnt: "A63A0C", peach: "F6C9A0", cream: "FDEBDC", muted: "6F5C51",
  caution: "F2C14E", ec: "F28C28", danger: "C0392B", xdanger: "6E0000", nh: "4C9BE8", grid: "E9D9CB", bg: "FBF4EC", learn: "EBC9A6" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "HeatCast NCR";
pres.author = "Edrian Tala, Harry Verdeflor, Marc Lawrence David";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const W = 13.333;
const script = [];
const ICON = (k) => path.join(IMG, "icons", k + ".png");   // slide-by-slide script for the printable speaker script

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "Cover",
  background: { path: path.join(IMG, "bg_warm.jpg") },
  objects: [{ rect: { x: 0.45, y: 0.38, w: W - 0.9, h: 6.74, fill: { type: "none" }, line: { color: "FFFFFF", width: 1.75 } } }],
});
pres.defineSlideMaster({
  title: "Statement",
  background: { color: HEX.dark },
  objects: [{ rect: { x: 0.45, y: 0.38, w: W - 0.9, h: 6.74, fill: { type: "none" }, line: { color: HEX.peach, width: 0.75 } } }],
  slideNumber: { x: 12.0, y: 6.62, w: 0.55, h: 0.3, fontFace: "Calibri", fontSize: 11, color: HEX.peach, align: "right" },
});
pres.defineSlideMaster({
  title: "Content",
  background: { color: HEX.bg },
  objects: [
    { rect: { x: 0.45, y: 0.38, w: W - 0.9, h: 6.74, fill: { type: "none" }, line: { color: HEX.dark, width: 0.75 } } },
    { placeholder: { options: { name: "title", type: "title", x: 0.95, y: 0.7, w: 11.45, h: 0.75, fontFace: "Cambria",
      fontSize: 34, color: C.text1, charSpacing: 5, align: "center", valign: "middle", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.0, y: 6.62, w: 0.55, h: 0.3, fontFace: "Calibri", fontSize: 11, color: HEX.muted, align: "right" },
});

// ---------- helpers ----------
function pill(slide, text, y, w, opts = {}) {
  slide.addText(text, { x: (W - w) / 2, y, w, h: 0.46, fill: { color: opts.fill || HEX.peach }, fontSize: 15, color: HEX.dark,
    bold: !!opts.bold, charSpacing: 1, margin: 4, align: "center", valign: "middle", isTextBox: true, objectName: "Subtitle pill" });
}
function content(title, section, sub, subW, subOpts) {
  const s = pres.addSlide({ masterName: "Content", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  if (sub) pill(s, sub, 1.55, subW, subOpts);
  return s;
}
function notes(s, no, title, who, time, text) {
  s.addNotes(`${who.toUpperCase()} (${time})\n\n${text}`);
  script.push({ no, title, who, time, text });
}
function card(s, x, y, w, h, fill, name) {
  s.addShape(pres.ShapeType.rect, { x, y, w, h, fill: { color: fill }, line: { type: "none" }, objectName: name });
}

// ================= 1. Title =================
pres.addSection({ title: "Introduction" });
let s = pres.addSlide({ masterName: "Cover", sectionTitle: "Introduction" });
s.addText("Edrian Tala   ·   Harry Verdeflor   ·   Marc Lawrence David", { x: (W - 7.2) / 2, y: 1.05, w: 7.2, h: 0.45,
  shape: pres.ShapeType.roundRect, rectRadius: 0.08, fill: { color: "FFFFFF" }, fontSize: 15, color: C.text1, align: "center",
  valign: "middle", isTextBox: true, objectName: "Authors" });
s.addText("HEATCAST NCR", { x: 0.9, y: 2.45, w: W - 1.8, h: 1.2, fontFace: "Cambria", fontSize: 66, charSpacing: 16,
  color: C.text1, align: "center", valign: "middle", isTextBox: true, objectName: "Title" });
s.addText("Can machine learning predict tomorrow's heat level in Metro Manila better than just copying today's?", {
  x: 1.6, y: 3.75, w: W - 3.2, h: 0.9, fontFace: "Cambria", fontSize: 24, italic: true, color: HEX.burnt, align: "center",
  valign: "top", isTextBox: true, objectName: "Question" });
s.addText("CCMACLRL Introduction to Machine Learning  ·  COM241ML  ·  Dr. Armida P. Salazar", { x: 1.5, y: 6.1, w: W - 3,
  h: 0.4, fontSize: 14, color: C.text1, align: "center", isTextBox: true, objectName: "Course" });
notes(s, 1, "Title", "Edrian", "20 seconds",
  "Good morning. We are Edrian, Harry and Marc, and this is HeatCast NCR. Our question: can machine learning predict tomorrow's heat level in Metro Manila better than just copying today's level? Let's start with a simple example.");

// ================= 2. The question, as an example =================
s = content("OUR QUESTION", "Introduction", "One city, one day ahead", 3.6);
s.addText("Today, Manila's heat index reached 44 °C, which is Danger. Tomorrow can go one of three ways:", { x: 1.2, y: 2.15, w: W - 2.4, h: 1.0,
  fontFace: "Cambria", fontSize: 28, color: HEX.dark, align: "center", valign: "middle", isTextBox: true, objectName: "Example" });
const q2 = [["Hotter", "Extreme Danger", "52 °C and up", "up", HEX.xdanger, "FFFFFF"],
  ["Same level", "Danger again", "42 to 51 °C", "same", HEX.danger, "FFFFFF"],
  ["Cooler", "Extreme Caution or lower", "below 42 °C", "down", HEX.ec, HEX.dark]];
q2.forEach(([head, lvl, rng, ic, f, t], i) => {
  const x = 0.95 + i * 3.88, y = 3.35, w = 3.69, h = 2.6;
  card(s, x, y, w, h, HEX.cream, "Outcome " + head);
  s.addImage({ path: ICON(ic), x: x + 0.3, y: y + 0.3, w: 0.8, h: 0.8, altText: head, objectName: "Outcome icon " + (i + 1) });
  s.addText(head, { x: x + 1.3, y: y + 0.3, w: w - 1.6, h: 0.8, fontFace: "Cambria", fontSize: 26, color: HEX.dark, margin: 0, valign: "middle", isTextBox: true, objectName: "Outcome head " + (i + 1) });
  s.addText([{ text: lvl, options: { bold: true, breakLine: true } }, { text: rng }], { x: x + 0.3, y: y + 1.4, w: w - 0.6, h: 0.9, fill: { color: f },
    fontSize: 17, color: t, align: "center", valign: "middle", margin: 4, isTextBox: true, objectName: "Outcome level " + (i + 1) });
});
s.addText("HeatCast NCR picks one of these for each of the 16 cities, every day.", { x: 0.95, y: 6.1, w: 11.45, h: 0.45,
  fontFace: "Cambria", fontSize: 20, italic: true, color: HEX.burnt, align: "center", valign: "middle", isTextBox: true, objectName: "Our job" });
notes(s, 2, "Our question", "Edrian", "30 seconds",
  "Here is our question as an example. Today Manila's heat index reached 44 degrees, which is Danger. Tomorrow can go three ways: hotter, Extreme Danger; the same level, Danger again; or cooler. " +
  "HeatCast NCR has to pick one of these, for each of the 16 cities, every day. So which one happens most often?");

// ================= 3. Answer =================
s = pres.addSlide({ masterName: "Statement", sectionTitle: "Introduction" });
s.addText("82%", { x: 1.0, y: 1.2, w: 6.6, h: 1.9, fontFace: "Cambria", fontSize: 130, color: HEX.peach, align: "left", valign: "middle", margin: 0, isTextBox: true, objectName: "Big number" });
s.addText("of the time in 2025, tomorrow's heat level was the same as today's.", { x: 1.0, y: 3.2, w: 6.4, h: 1.3,
  fontFace: "Cambria", fontSize: 30, color: HEX.bg, align: "left", valign: "top", margin: 0, isTextBox: true, objectName: "Statement" });
s.addText("So simply copying today's level is already a strong forecast. We call it the copy-today rule, and it is the rule our models had to beat.", {
  x: 1.0, y: 4.75, w: 6.2, h: 1.3, fontSize: 20, color: HEX.peach, align: "left", valign: "top", margin: 0, isTextBox: true, objectName: "So what" });
const gx = 8.25, gy = 1.25, sq = 0.4;
for (let r = 0; r < 10; r++) for (let c = 0; c < 10; c++) {
  const k = r * 10 + c, same = k < 82;
  s.addShape(pres.ShapeType.rect, { x: gx + c * sq, y: gy + r * sq, w: sq - 0.06, h: sq - 0.06,
    fill: same ? { color: HEX.peach } : { type: "none" }, line: same ? { type: "none" } : { color: HEX.peach, width: 1 }, objectName: "Square " + (k + 1) });
}
s.addText([{ text: "Filled: same level as the day before", options: { breakLine: true } }, { text: "Empty: the level changed" }],
  { x: gx, y: gy + 10 * sq + 0.15, w: 4.0, h: 0.65, fontSize: 14, color: HEX.peach, margin: 0, valign: "top", isTextBox: true, objectName: "Grid key" });
notes(s, 3, "The answer: 82%", "Edrian", "20 seconds",
  "Most often, the same level. Each square here is one percent of the city-days in 2025. In 82 out of every 100, tomorrow's level was the same as today's. So the simplest forecast, copy today, is already right most of the time. We call it the copy-today rule, and the real question of our project is whether machine learning can beat it.");

// ================= 4. Problem and data =================
s = content("THE PROBLEM AND THE DATA", "Introduction", "Who needs a one-day heat warning, and what we used", 6.6);
s.addText([
  { text: "Who needs it", options: { fontFace: "Cambria", fontSize: 20, color: HEX.burnt, breakLine: true } },
  { text: "Schools, employers of outdoor workers and city offices. A day ahead, they decide to move activities, prepare water and cooling, or warn residents.", options: { fontSize: 17, color: HEX.dark, breakLine: true, paraSpaceAfter: 14 } },
  { text: "Our task", options: { fontFace: "Cambria", fontSize: 20, color: HEX.burnt, breakLine: true } },
  { text: "Predict tomorrow's PAGASA heat level for each city, using only today's weather in that city.", options: { fontSize: 17, color: HEX.dark } },
], { x: 0.95, y: 2.3, w: 5.3, h: 2.75, margin: 0, valign: "top", isTextBox: true, objectName: "Problem text" });
s.addText("The PAGASA heat index levels (the heat index is how hot it feels)", { x: 0.95, y: 5.12, w: 5.6, h: 0.3, fontSize: 12, color: HEX.muted, margin: 0,
  isTextBox: true, objectName: "Levels label" });
const lv = [["Not Hazardous", "below 27 °C", HEX.nh, "FFFFFF"], ["Caution", "27–32 °C", HEX.caution, HEX.dark],
  ["Extreme Caution", "33–41 °C", HEX.ec, HEX.dark], ["Danger", "42–51 °C", HEX.danger, "FFFFFF"], ["Extreme Danger", "52 °C and up", HEX.xdanger, "FFFFFF"]];
lv.forEach(([n, r, f, t], i) => {
  s.addText([{ text: n, options: { bold: true, breakLine: true } }, { text: r }], { x: 0.95 + i * 1.07, y: 5.45, w: 1.01, h: 0.78,
    fill: { color: f }, fontSize: 12, color: t, align: "center", valign: "middle", margin: 2, isTextBox: true, objectName: "Level " + n });
});
const tiles = [["16", "cities of Metro Manila (NCR)"], ["29,168", "rows: one per city per day, 2021 to 2025"],
  ["5", "weather readings about today: heat index, lowest temperature, rain, air pressure, sunshine"], ["1 day", "ahead: we predict tomorrow's level in the same city"]];
tiles.forEach(([big, lab], i) => {
  const x = 6.75 + (i % 2) * 2.9, y = 2.3 + Math.floor(i / 2) * 2.0;
  card(s, x, y, 2.75, 1.85, HEX.cream, "Tile " + big);
  s.addText(big, { x: x + 0.2, y: y + 0.15, w: 2.35, h: 0.7, fontFace: "Cambria", fontSize: 40, color: HEX.burnt, margin: 0, valign: "middle", isTextBox: true });
  s.addText(lab, { x: x + 0.2, y: y + 0.9, w: 2.35, h: 0.85, fontSize: 14, color: C.text1, margin: 0, valign: "top", isTextBox: true });
});
s.addText("Weather: hourly estimates from Open-Meteo (ERA5)", { x: 6.75, y: 6.32, w: 5.65, h: 0.28, fontSize: 11, color: HEX.muted, margin: 0, isTextBox: true });
notes(s, 4, "The problem and the data", "Harry", "50 seconds",
  "Thanks, Edrian. The heat index is how hot it feels when you combine temperature and humidity. PAGASA groups it into five levels; Danger starts at 42 degrees. " +
  "Schools, employers of outdoor workers and city offices need to know a day ahead whether tomorrow will reach Danger. " +
  "Our data covers the 16 cities of Metro Manila from 2021 to 2025: 29,168 rows, one per city per day. Each row has five weather readings about today, and the answer is tomorrow's level in the same city. " +
  "The weather comes from Open-Meteo's hourly estimates.");

// ================= 5. What the data showed =================
pres.addSection({ title: "Data" });
s = content("WHAT THE DATA SHOWED", "Data", "Three findings, and what each one changed", 5.6);
const finds = [
  ["8%", "of city-days were Danger, and 78.5% were Extreme Caution", "So \"percent correct\" misleads: always guessing Extreme Caution is already 78% right."],
  ["May", "Danger peaks in April to June (nearly 1 in 3 May days) and never happens December to February", "So we split the data by time, like real forecasting."],
  ["17% vs 2%", "Some cities get far more Danger days: Malabon, Navotas, Valenzuela vs Muntinlupa, San Juan", "So every city keeps its own rows, and the city is an input."],
];
finds.forEach(([big, f, d], i) => {
  const y = 2.3 + i * 1.45;
  s.addText(big, { x: 0.95, y, w: 2.05, h: 0.75, fontFace: "Cambria", fontSize: 32, color: HEX.burnt, margin: 0, valign: "top", isTextBox: true, objectName: "Finding number " + (i + 1) });
  s.addText([{ text: f, options: { bold: true, breakLine: true } }, { text: d, options: { color: HEX.muted } }],
    { x: 3.05, y, w: 3.55, h: 1.35, fontSize: 14, color: C.text1, margin: 0, valign: "top", paraSpaceAfter: 4, isTextBox: true, objectName: "Finding text " + (i + 1) });
});
const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
s.addChart(pres.ChartType.bar, [
  { name: "Not Hazardous", labels: months, values: [0.5, 0.6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0] },
  { name: "Caution", labels: months, values: [62.0, 29.3, 13.5, 1.9, 0, 0, 6.3, 2.8, 6.3, 3.2, 2.2, 34.6] },
  { name: "Extreme Caution", labels: months, values: [37.5, 70.1, 83.6, 86.0, 68.9, 78.1, 84.8, 89.9, 86.9, 96.1, 95.8, 64.4] },
  { name: "Danger", labels: months, values: [0, 0, 2.9, 12.1, 31.1, 21.9, 8.9, 7.3, 6.8, 0.8, 2.0, 0] },
], { x: 6.85, y: 2.2, w: 5.6, h: 4.35, barDir: "col", barGrouping: "percentStacked", barGapWidthPct: 35,
  chartColors: [HEX.nh, HEX.caution, HEX.ec, HEX.danger], showTitle: true, title: "Share of each level by month (2021 to 2024)", titleFontSize: 14,
  titleColor: HEX.dark, titleFontFace: "+mn-lt", showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt", legendColor: HEX.dark,
  catAxisLabelColor: HEX.muted, valAxisLabelColor: HEX.muted, catAxisLabelFontSize: 11, valAxisLabelFontSize: 11,
  catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", valGridLine: { color: HEX.grid, size: 0.5 }, catGridLine: { style: "none" },
  valAxisLabelFormatCode: "0%", objectName: "Chart level by month" });
notes(s, 5, "What the data showed", "Marc", "1 minute",
  "Before building models, we explored the data, using only the training years. Three findings changed our decisions. " +
  "One: Danger is rare, 8% of city-days, while 78.5% are Extreme Caution. So a lazy model that always says Extreme Caution is already 78% correct. That is why we do not judge the models by percent correct. " +
  "Two, in the chart: the red part is Danger. It peaks from April to June, nearly one in three May days, and it never happens from December to February. So we split the data by time, the way a real forecast works. " +
  "Three: cities are different. Malabon, Navotas and Valenzuela have Danger on 17% of days, Muntinlupa and San Juan on only 2%. So each city keeps its own rows.");

// ================= 6. A fair test =================
pres.addSection({ title: "Method" });
s = content("A FAIR TEST, LIKE AN EXAM", "Method", "Every model studied the same days and took the same final exam", 7.4);
const x0 = 0.95, trainW = 9.05, testX = 10.12, testW = 2.28;
["2021", "2022", "2023", "2024"].forEach((yr, i) => s.addText(yr, { x: x0 + i * (trainW / 4), y: 2.2, w: 1.0, h: 0.3, fontSize: 12, color: HEX.muted, margin: 0, isTextBox: true }));
s.addText("2025", { x: testX, y: 2.2, w: 1.0, h: 0.3, fontSize: 12, color: HEX.muted, margin: 0, isTextBox: true });
s.addText("Study: the models learn only from 2021 to 2024", { x: x0, y: 2.55, w: trainW, h: 0.55, fill: { color: HEX.peach },
  fontSize: 16, color: HEX.dark, align: "center", valign: "middle", isTextBox: true, objectName: "Training bar" });
s.addText("Final exam: 2025, once", { x: testX, y: 2.55, w: testW, h: 0.55, fill: { color: HEX.burnt }, fontSize: 15, color: "FFFFFF",
  bold: true, align: "center", valign: "middle", isTextBox: true, objectName: "Test bar" });
const day = trainW / 1457;
for (let k = 1; k <= 5; k++) {
  const y = 3.35 + (k - 1) * 0.27, chk = 247 + 242 * (k - 1);
  s.addShape(pres.ShapeType.rect, { x: x0, y, w: (chk - 1) * day, h: 0.2, fill: { color: HEX.learn }, line: { type: "none" }, objectName: "Quiz study " + k });
  s.addShape(pres.ShapeType.rect, { x: x0 + chk * day, y, w: 242 * day, h: 0.2, fill: { color: HEX.ec }, line: { type: "none" }, objectName: "Quiz check " + k });
}
s.addText("5 practice quizzes", { x: testX, y: 3.3, w: 2.3, h: 0.32, fontSize: 13, bold: true, color: HEX.dark, margin: 0, valign: "middle", isTextBox: true });
s.addShape(pres.ShapeType.rect, { x: testX, y: 3.75, w: 0.22, h: 0.18, fill: { color: HEX.learn }, line: { type: "none" } });
s.addText("study earlier days", { x: testX + 0.3, y: 3.68, w: 2.0, h: 0.32, fontSize: 12, color: HEX.dark, margin: 0, valign: "middle", isTextBox: true });
s.addShape(pres.ShapeType.rect, { x: testX, y: 4.12, w: 0.22, h: 0.18, fill: { color: HEX.ec }, line: { type: "none" } });
s.addText("quiz on the next days", { x: testX + 0.3, y: 4.05, w: 2.0, h: 0.32, fontSize: 12, color: HEX.dark, margin: 0, valign: "middle", isTextBox: true });
const cards = [["The score", "How well a model does on Caution, Extreme Caution and Danger, each counted equally (0 to 1, higher is better)."],
  ["The rule", "First, catch more Danger days than the copy-today rule. Then the best score wins."],
  ["The baseline", "Copy today: tomorrow's level is today's level in the same city."]];
cards.forEach(([h, t], i) => {
  const x = 0.95 + i * 3.88;
  card(s, x, 4.85, 3.69, 1.6, HEX.cream, "Card " + h);
  s.addText([{ text: h, options: { fontFace: "Cambria", fontSize: 19, color: HEX.burnt, breakLine: true } }, { text: t, options: { fontSize: 14, color: HEX.dark } }],
    { x: x + 0.2, y: 4.95, w: 3.3, h: 1.45, margin: 0, valign: "top", paraSpaceAfter: 4, isTextBox: true });
});
s.addText("In technical terms: chronological split, 5-fold time-series cross-validation, macro F1.", { x: 0.95, y: 6.55, w: 9.0, h: 0.28, fontSize: 11, italic: true, color: HEX.muted, margin: 0, isTextBox: true });
notes(s, 6, "A fair test, like an exam", "Harry", "1 minute",
  "To compare the models fairly, think of an exam. All three models studied the same days, 2021 to 2024, and took the same final exam, 2025, which we opened only once at the very end. " +
  "While choosing settings, each model took five practice quizzes: it studies earlier days and is quizzed on the days right after, never the other way around, because we cannot use the future to predict the past. " +
  "The score counts Caution, Extreme Caution and Danger equally, from 0 to 1. Our rule, fixed before the final exam: first, a model must catch more Danger days than the copy-today rule; then the best score wins. " +
  "Technically this is a chronological split with time-series cross-validation, and the score is macro F1.");

// ================= 7. Which mistake is worse =================
s = content("WHICH MISTAKE IS WORSE?", "Method", "Every forecast is sometimes wrong, in one of two ways", 6.6);
const q7 = [["Missing a real Danger day", "Nobody prepares, and students play outside at 44 °C.", "The cost: someone may get heat exhaustion or heat stroke.", "run", "F8D5CF", "WORSE", HEX.danger],
  ["A false alarm", "Activities are moved indoors, but the day was not that hot.", "The cost: a change of plans for nothing.", "bell", HEX.cream, "LESS COSTLY", HEX.muted]];
q7.forEach(([head, what, cost, ic, f, tag, tagc], i) => {
  const x = 0.95 + i * 5.875, y = 2.3, w = 5.575, h = 3.55;
  card(s, x, y, w, h, f, "Mistake " + (i + 1));
  s.addImage({ path: ICON(ic), x: x + 0.35, y: y + 0.3, w: 1.0, h: 1.0, altText: head, objectName: "Mistake icon " + (i + 1) });
  s.addText(tag, { x: x + w - 2.0, y: y + 0.35, w: 1.65, h: 0.42, fill: { color: tagc }, fontSize: 13, bold: true, color: "FFFFFF", charSpacing: 1,
    align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "Mistake tag " + (i + 1) });
  s.addText(head, { x: x + 0.35, y: y + 1.3, w: w - 0.7, h: 0.6, fontFace: "Cambria", fontSize: 28, color: HEX.dark, margin: 0, valign: "middle", isTextBox: true });
  s.addText(what, { x: x + 0.35, y: y + 1.95, w: w - 0.7, h: 0.75, fontSize: 18, color: HEX.dark, margin: 0, valign: "top", isTextBox: true });
  s.addText(cost, { x: x + 0.35, y: y + 2.75, w: w - 0.7, h: 0.6, fontSize: 16, bold: true, color: HEX.burnt, margin: 0, valign: "top", isTextBox: true });
});
s.addText("So our rule: a model must first catch more Danger days than copy-today.", { x: 0.95, y: 6.05, w: 11.45, h: 0.5,
  fontFace: "Cambria", fontSize: 20, italic: true, color: HEX.burnt, align: "center", valign: "middle", isTextBox: true, objectName: "Our choice" });
notes(s, 7, "Which mistake is worse?", "Marc", "40 seconds",
  "Every forecast is sometimes wrong, and it can be wrong in two ways. One: it misses a real Danger day, so nobody prepares, students play outside at 44 degrees, and someone may get sick. " +
  "Two: a false alarm, so activities are moved indoors on a day that was not that hot. " +
  "We decided the first mistake is worse: a missed Danger day can hurt people, while a false alarm only costs a change of plans. That is why our rule asks a model to catch more Danger days first. Keep this in mind for the results.");

// ================= 8. Three models =================
s = content("THREE MODELS VS. COPY-TODAY", "Method", "Practice-quiz results: the average of the 5 quizzes", 6.4);
const cats = ["Copy-today rule", "Logistic Regression", "Random Forest", "Gradient Boosting"];
const chartBase = () => ({ barDir: "bar", barGrouping: "clustered", barGapWidthPct: 45, showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 13,
  dataLabelColor: HEX.dark, dataLabelFontFace: "+mn-lt", valAxisHidden: true, valAxisMinVal: 0, valGridLine: { style: "none" }, catGridLine: { style: "none" },
  catAxisLabelColor: HEX.dark, catAxisLabelFontSize: 13, catAxisLabelFontFace: "+mn-lt", catAxisOrientation: "maxMin", showLegend: false, showTitle: true,
  titleFontSize: 15, titleColor: HEX.dark, titleFontFace: "+mn-lt" });
s.addChart(pres.ChartType.bar, [{ name: "Score", labels: cats, values: [0.679, 0.632, 0.653, 0.643] }],
  Object.assign(chartBase(), { x: 0.85, y: 2.15, w: 6.7, h: 2.2, chartColors: ["E9A26B"], valAxisMaxVal: 0.9, dataLabelFormatCode: "0.000",
    title: "Score (0 to 1, higher is better)", objectName: "Chart score" }));
s.addChart(pres.ChartType.bar, [{ name: "Danger days caught", labels: cats, values: [0.518, 0.276, 0.672, 0.670] }],
  Object.assign(chartBase(), { x: 0.85, y: 4.4, w: 6.7, h: 2.2, chartColors: [HEX.burnt], valAxisMaxVal: 0.9, dataLabelFormatCode: "0%",
    title: "Danger days caught", objectName: "Chart Danger caught" }));
const models = [
  ["Logistic Regression", "Harry", "Draws straight dividing lines between the levels.", "Careful, but caught only 28% of Danger days.", false],
  ["Random Forest", "Edrian", "500 decision trees that vote on the answer.", "Caught 67% of Danger days with the best score of the three.", true],
  ["Gradient Boosting", "Marc", "Trees built one after another, each fixing the last one's mistakes.", "Almost tied with Random Forest.", false],
];
models.forEach(([n, who, how, res, sel], i) => {
  const y = 2.2 + i * 1.45;
  card(s, 7.85, y, 4.55, 1.33, sel ? HEX.peach : HEX.cream, "Model " + n);
  s.addText([{ text: n, options: { fontFace: "Cambria", fontSize: 18, bold: true, color: HEX.dark } }, { text: "   " + who, options: { fontSize: 12, color: HEX.muted, breakLine: true } },
    { text: how, options: { fontSize: 13, color: HEX.muted, breakLine: true } }, { text: res, options: { fontSize: 14, color: HEX.dark } }],
    { x: 8.05, y: y + 0.08, w: 4.2, h: 1.2, margin: 0, valign: "top", isTextBox: true });
  if (sel) s.addText("SELECTED", { x: 11.2, y: y + 0.12, w: 1.05, h: 0.32, fill: { color: HEX.burnt }, fontSize: 11, bold: true, color: "FFFFFF",
    align: "center", valign: "middle", charSpacing: 1, margin: 0, isTextBox: true, objectName: "Selected tag" });
});
notes(s, 8, "Three models vs. copy-today", "Harry, Edrian, Marc", "1 minute 15 (about 25 seconds each)",
  "HARRY: Here are the practice-quiz results. Top chart: the score. Bottom chart: the share of Danger days each one caught. Look at the copy-today rule at the top: its score, 0.679, is the highest. None of our models beat it on score. " +
  "My model, Logistic Regression, draws straight dividing lines between levels. It was careful, but it caught only 28% of Danger days, even fewer than copying today.\n" +
  "EDRIAN: Random Forest is 500 decision trees that vote. We told it that Danger days matter more, and it caught 67% of them, more than copy-today, with the best score of our three. By our rule, it was selected.\n" +
  "MARC: Gradient Boosting builds trees one after another, each fixing the last one's mistakes. It was almost tied with Random Forest, 0.643 against 0.653, so either would have worked.");

// ================= 9. Danger days caught =================
pres.addSection({ title: "Results" });
s = content("DANGER DAYS CAUGHT", "Results", "The final exam: 2025, opened once", 5.2);
s.addText("In 2025 there were 347 Danger days across the 16 cities. Here is how many got a warning the day before.", { x: 1.2, y: 2.15, w: W - 2.4, h: 1.0,
  fontFace: "Cambria", fontSize: 28, color: HEX.dark, align: "center", valign: "middle", isTextBox: true, objectName: "Setup" });
// two bars on the same 0 to 347 track
const bx = 4.1, bw = 8.3;
[["Copy-today rule", "the baseline", 207, HEX.ec, HEX.dark], ["Our Random Forest", "the selected model", 293, HEX.danger, "FFFFFF"]].forEach(([n, sub, v, f, t], i) => {
  const y = 3.45 + i * 1.15;
  s.addText([{ text: n, options: { fontFace: "Cambria", fontSize: 22, color: HEX.dark, breakLine: true } }, { text: sub, options: { fontSize: 14, color: HEX.muted } }],
    { x: 0.95, y, w: 3.0, h: 0.9, margin: 0, valign: "middle", isTextBox: true, objectName: "Bar label " + (i + 1) });
  s.addShape(pres.ShapeType.rect, { x: bx, y, w: bw, h: 0.9, fill: { color: HEX.cream }, line: { type: "none" }, objectName: "Track " + (i + 1) });
  s.addText([{ text: String(v), options: { fontFace: "Cambria", fontSize: 30, bold: true } }, { text: `  of 347 (${Math.round(v / 347 * 100)}%)`, options: { fontSize: 15 } }],
    { x: bx, y, w: bw * v / 347, h: 0.9, fill: { color: f }, color: t, align: "right", valign: "middle", margin: [0, 14, 0, 0], isTextBox: true, objectName: "Bar " + (i + 1) });
});
s.addText([{ text: "86 more Danger days", options: { bold: true } }, { text: " got a warning the day before, compared with copying today." }], {
  x: 0.95, y: 5.95, w: 11.45, h: 0.62, fill: { color: HEX.dark }, fontFace: "Cambria", fontSize: 20, color: HEX.bg,
  align: "center", valign: "middle", margin: 6, isTextBox: true, objectName: "Difference" });
notes(s, 9, "Danger days caught", "Marc", "25 seconds",
  "Now the final exam, 2025, which we opened only once. There were 347 Danger days across the 16 cities. Copying today warned about 207 of them, 60%. " +
  "Our Random Forest warned about 293, 84%. That is 86 more Danger days with a warning the day before.");

// ================= 10. Final exam result =================
s = content("FINAL EXAM RESULT", "Results", "The selected Random Forest on 2025, compared with copy-today", 7.2);
const stats = [["293", "of 347 Danger days caught (84%)", "Copy-today caught 207 (60%)", HEX.danger],
  ["36%", "of its Danger warnings were right", "293 of 816: about 2 false alarms for each real Danger day", HEX.burnt],
  ["0.61", "score, below copy-today's 0.68", "It did not beat copy-today overall", HEX.dark]];
stats.forEach(([big, lab, sub, col], i) => {
  const x = 0.95 + i * 3.88;
  card(s, x, 2.3, 3.69, 2.75, HEX.cream, "Stat " + big);
  s.addText(big, { x: x + 0.25, y: 2.45, w: 3.2, h: 1.25, fontFace: "Cambria", fontSize: 66, color: col, margin: 0, valign: "middle", isTextBox: true });
  s.addText(lab, { x: x + 0.25, y: 3.75, w: 3.2, h: 0.6, fontSize: 17, bold: true, color: HEX.dark, margin: 0, valign: "top", isTextBox: true });
  s.addText(sub, { x: x + 0.25, y: 4.38, w: 3.2, h: 0.6, fontSize: 13, color: HEX.muted, margin: 0, valign: "top", isTextBox: true });
});
s.addText("Not a better all-round forecaster, but a good early warning: it catches far more Danger days than copying today, at the price of more false alarms.", {
  x: 0.95, y: 5.3, w: 11.45, h: 1.1, fill: { color: HEX.dark }, fontFace: "Cambria", italic: true, fontSize: 20, color: HEX.bg,
  align: "center", valign: "middle", margin: 18, isTextBox: true, objectName: "Takeaway" });
notes(s, 10, "Final exam result", "Marc", "50 seconds",
  "Here is the full picture. Catching 293 Danger days has a price: " +
  "when it warned Danger, it was right only 36% of the time, about two false alarms for every real Danger day. And its overall score, 0.61, is below copy-today's 0.68. " +
  "Remember our choice: we said missing a Danger day is worse than a false alarm. So it is not a better all-round forecaster, but it is a good early warning. Edrian will show it live.");

// ================= 11. Live demo =================
s = content("LIVE DEMO", "Results", "heatcast-ncr.streamlit.app", 4.2, { bold: true });
const steps = [["A hot day in Manila", "We choose Manila and type a hot day: heat index 45.5 °C, lowest 29 °C, no rain, 1,008 hPa, sunshine 7,000."],
  ["A mistake on purpose", "Rain of −5 mm is impossible: the app shows the accepted range and gives no prediction."],
  ["An empty form", "Every missing value is named by the app; nothing is filled in silently."]];
steps.forEach(([h, t], i) => {
  const y = 2.35 + i * 1.3;
  s.addShape(pres.ShapeType.ellipse, { x: 0.95, y, w: 0.62, h: 0.62, fill: { color: HEX.burnt }, line: { type: "none" }, objectName: "Step dot " + (i + 1) });
  s.addText(String(i + 1), { x: 0.95, y, w: 0.62, h: 0.62, fontFace: "Cambria", fontSize: 22, color: "FFFFFF", align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addText([{ text: h, options: { fontFace: "Cambria", fontSize: 20, color: HEX.dark, breakLine: true } }, { text: t, options: { fontSize: 14, color: HEX.muted } }],
    { x: 1.8, y: y - 0.05, w: 4.1, h: 1.25, margin: 0, valign: "top", isTextBox: true, objectName: "Step " + (i + 1) });
});
s.addText("The app uses the same saved Random Forest that took the final exam.", {
  x: 0.95, y: 6.25, w: 4.95, h: 0.35, fontSize: 12, color: HEX.muted, italic: true, margin: 0, valign: "top", isTextBox: true });
s.addImage({ path: path.join(IMG, "app_land.png"), x: 12.4 - 4.45 * 1212 / 852, y: 2.15, w: 4.45 * 1212 / 852, h: 4.45,
  altText: "Screenshot of the HeatCast NCR app: a Danger prediction for Manila, the map and the error messages", objectName: "App screenshot" });
s.addShape(pres.ShapeType.rect, { x: 12.4 - 4.45 * 1212 / 852, y: 2.15, w: 4.45 * 1212 / 852, h: 4.45, fill: { type: "none" }, line: { color: "E2CDBB", width: 0.75 }, objectName: "Screenshot frame" });
notes(s, 11, "Live demo", "Edrian", "1 minute 45",
  "BEFORE THE TALK: open heatcast-ncr.streamlit.app; the first load can take about a minute. If the internet fails, show this screenshot, or run it locally with: streamlit run app/streamlit_app.py.\n\n" +
  "Let's try it with Manila. (Choose it at the top; the city lights up blue on the map.) Say today was very hot there: heat index 45.5, lowest temperature 29, rain 0, pressure 1008, sunshine 7000. Click the button. " +
  "It predicts the level for tomorrow with the probability of each level, and the city takes that level's colour on the map. It also reminds users it is a decision aid, not a PAGASA advisory. " +
  "Now a mistake on purpose: rain of minus 5. The app refuses it and shows the accepted range. And if we clear the form and click, it names every missing value instead of guessing. " +
  "This is the same saved model that took the final exam, and the input checks are covered by 51 automated tests.");

// ================= 12. Conclusion =================
pres.addSection({ title: "Conclusion" });
s = content("CONCLUSION", "Conclusion", "What we learned", 3.4);
const conclIcons = ["answer", "warn", "route"];
const concl = [["01", "The answer", "No. None of our models beat copying today's level on overall score: tomorrow's heat is mostly today's heat."],
  ["02", "What ML adds", "Told that Danger days matter more, the Random Forest caught 84% of them in 2025. We deployed it as an early warning."],
  ["03", "Limits and next steps", "Weather estimates, not station readings; only five years. Next: add the month and recent days, a weather forecast, and more years."]];
concl.forEach(([n, h, t], i) => {
  const x = 0.95 + i * 3.88;
  card(s, x, 2.3, 3.69, 3.95, i === 1 ? HEX.peach : HEX.cream, "Conclusion " + n);
  s.addText(n, { x: x + 0.3, y: 2.5, w: 1.5, h: 0.85, fontFace: "Cambria", fontSize: 44, color: HEX.burnt, margin: 0, valign: "top", isTextBox: true });
  s.addImage({ path: ICON(conclIcons[i]), x: x + 3.69 - 1.15, y: 2.55, w: 0.8, h: 0.8, altText: h, objectName: "Conclusion icon " + n });
  s.addText([{ text: h, options: { fontFace: "Cambria", fontSize: 24, color: HEX.dark, breakLine: true } }, { text: t, options: { fontSize: 19, color: HEX.dark } }],
    { x: x + 0.3, y: 3.55, w: 3.1, h: 2.6, margin: 0, valign: "top", paraSpaceAfter: 8, isTextBox: true });
});
notes(s, 12, "Conclusion", "Harry", "50 seconds",
  "So, our answer: no, none of our models beat simply copying today's level on overall score. Tomorrow's heat is mostly today's heat. " +
  "But machine learning adds something specific: when we told the Random Forest that Danger days matter more, it caught 84% of them in 2025, so we deployed it as an early warning. " +
  "Its limits: the weather values are estimates, not station readings, and we used only five years. Next we would add the month and the previous days, a weather forecast for tomorrow, and more years. Thank you.");

// ================= 13. Thank you =================
s = pres.addSlide({ masterName: "Cover", sectionTitle: "Conclusion" });
s.addText("THANK YOU", { x: 0.9, y: 2.5, w: W - 1.8, h: 1.2, fontFace: "Cambria", fontSize: 66, charSpacing: 16, color: C.text1,
  align: "center", valign: "middle", isTextBox: true, objectName: "Thank you" });
s.addText("Questions?", { x: 0.9, y: 3.7, w: W - 1.8, h: 0.7, fontFace: "Cambria", fontSize: 30, italic: true, color: HEX.burnt,
  align: "center", valign: "middle", isTextBox: true, objectName: "Questions" });
s.addText("Try it: heatcast-ncr.streamlit.app   ·   Code: github.com/keyyum/heatcast-ncr-simple", { x: (W - 9.4) / 2, y: 5.0, w: 9.4, h: 0.45,
  shape: pres.ShapeType.roundRect, rectRadius: 0.08, fill: { color: "FFFFFF" }, fontSize: 15, color: C.text1, align: "center",
  valign: "middle", isTextBox: true, objectName: "Links" });
notes(s, 13, "Thank you / questions", "All", "Q&A",
  "Thank you. We are happy to take questions. The next slide is a backup with plain meanings of the technical words, in case a question uses them.");

// ================= 14. Backup: key terms =================
s = content("BACKUP: KEY TERMS", "Conclusion", "For questions only; we do not present this slide", 5.8, { fill: HEX.cream });
const terms = [
  ["Heat index", "How hot it feels, from temperature and humidity (US National Weather Service formula)."],
  ["Copy-today rule", "The persistence baseline: tomorrow's level = today's level in the same city."],
  ["Score (macro F1)", "F1 for each level, averaged over Caution, Extreme Caution and Danger; each level counts equally."],
  ["Danger days caught", "Danger recall: of the real Danger days, the share the model called Danger."],
  ["Warnings that were right", "Danger precision: of the model's Danger calls, the share that really were Danger."],
  ["Told Danger matters more", "Balanced class weights: rare levels count more while the model learns."],
  ["Practice quizzes", "5-fold time-series cross-validation inside 2021 to 2024; never learns from later days."],
  ["Weather estimates", "ERA5 reanalysis via Open-Meteo: a grid of about 25 km, not station readings."],
];
const cell = (text, i, extra = {}) => ({ text, options: Object.assign({ fill: { color: i % 2 ? HEX.bg : HEX.cream } }, extra) });
const rows = [[{ text: "Word on the slides", options: { bold: true, color: "FFFFFF", fill: { color: HEX.burnt } } },
  { text: "What it means", options: { bold: true, color: "FFFFFF", fill: { color: HEX.burnt } } }]]
  .concat(terms.map(([a, b], i) => [cell(a, i, { bold: true }), cell(b, i)]));
s.addTable(rows, { x: 0.95, y: 2.2, w: 11.45, colW: [3.2, 8.25], fontSize: 14, color: HEX.dark, fontFace: "Calibri", rowH: 0.47,
  border: { type: "solid", pt: 0.5, color: "E2CDBB" }, valign: "middle", margin: 0.06, objectName: "Key terms" });
notes(s, 14, "Backup: key terms", "Anyone, if asked", "only during Q&A",
  "Use this slide only if a question needs it. Likely questions: Why not percent correct? Because Danger is rare; always saying Extreme Caution is already 78% correct. " +
  "Why split by time? Because we forecast the future; a random split would let a model peek at the same days. " +
  "Why Random Forest over Gradient Boosting? Our rule picked the best score among the models that catch more Danger days; the two were almost tied. " +
  "Why did no model beat copy-today? Tomorrow's level is the same as today's on most days, and the models only see today's values.");

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  fs.writeFileSync(SCRIPT, JSON.stringify(script, null, 1));
  console.log("wrote", OUT);
})();
