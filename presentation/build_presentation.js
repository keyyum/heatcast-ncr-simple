const pptxgen = require("pptxgenjs");
const path = require("path");
const { applyTheme } = require("/root/.claude/skills/synced/ff5b1d5d-d175-46b8-b3f4-e64212c4048a_9e04934e-b6f0-41f6-a6be-94a773705624/pptx/scripts/apply_theme.js");

const IMG = path.join(__dirname, "..", "img");
const OUT = path.join(__dirname, "HeatCast_NCR_Presentation.pptx");

const THEME = {
  name: "HeatCast NCR",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "2E1406", lt1: "FFFFFF", dk2: "A63A0C", lt2: "FBF4EC",
    accent1: "A63A0C", accent2: "F28C28", accent3: "F2C14E", accent4: "C0392B",
    accent5: "7A675C", accent6: "4C9BE8", hlink: "A63A0C", folHlink: "7A675C",
  },
};
const HEX = { dark: "2E1406", burnt: "A63A0C", peach: "F6C9A0", cream: "FDEBDC", muted: "7A675C",
  caution: "F2C14E", ec: "F28C28", danger: "C0392B", xdanger: "6E0000", nh: "4C9BE8", grid: "E9D9CB", bg: "FBF4EC" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "HeatCast NCR";
pres.author = "Edrian Tala, Harry Verdeflor, Marc Lawrence David";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const W = 13.333;

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "Cover",
  background: { path: path.join(IMG, "bg_warm.jpg") },
  objects: [
    { rect: { x: 0.45, y: 0.38, w: W - 0.9, h: 6.74, fill: { type: "none" }, line: { color: "FFFFFF", width: 1.75 } } },
  ],
});
pres.defineSlideMaster({
  title: "Content",
  background: { color: HEX.bg },
  objects: [
    { rect: { x: 0.45, y: 0.38, w: W - 0.9, h: 6.74, fill: { type: "none" }, line: { color: HEX.dark, width: 0.75 } } },
    { placeholder: { options: { name: "title", type: "title", x: 0.95, y: 0.7, w: 11.45, h: 0.75, fontFace: "Cambria",
      fontSize: 34, color: C.text1, charSpacing: 5, valign: "middle", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.0, y: 6.62, w: 0.55, h: 0.3, fontFace: "Calibri", fontSize: 11, color: HEX.muted, align: "right" },
});

// ---------- helpers ----------
function pill(slide, text, x, y, w) {
  slide.addText(text, { x: (W - w) / 2, y, w, h: 0.44, fill: { color: HEX.peach }, fontSize: 14, color: C.text1, charSpacing: 1,
    margin: 4, align: "center", valign: "middle", isTextBox: true, objectName: "Subtitle pill" });
}
function content(title, section, sub, subW) {
  const s = pres.addSlide({ masterName: "Content", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  if (sub) pill(s, sub, 0.95, 1.55, subW);
  return s;
}

// ================= 1. Title =================
pres.addSection({ title: "Introduction" });
let s = pres.addSlide({ masterName: "Cover", sectionTitle: "Introduction" });
s.addText("Edrian Tala   ·   Harry Verdeflor   ·   Marc Lawrence David", { x: (W - 7.2) / 2, y: 1.05, w: 7.2, h: 0.45,
  shape: pres.ShapeType.roundRect, rectRadius: 0.08, fill: { color: "FFFFFF" }, fontSize: 15, color: C.text1, align: "center",
  valign: "middle", isTextBox: true, objectName: "Authors" });
s.addText("HEATCAST NCR", { x: 0.9, y: 2.45, w: W - 1.8, h: 1.2, fontFace: "Cambria", fontSize: 66, charSpacing: 16,
  color: C.text1, align: "center", valign: "middle", isTextBox: true, objectName: "Title" });
s.addText("Can machine learning predict tomorrow's heat level in Metro Manila better than copying today's?", {
  x: 1.6, y: 3.75, w: W - 3.2, h: 0.9, fontFace: "Cambria", fontSize: 24, italic: true, color: HEX.burnt, align: "center",
  valign: "top", isTextBox: true, objectName: "Question" });
s.addText("CCMACLRL Introduction to Machine Learning  ·  COM241ML  ·  Dr. Armida P. Salazar", { x: 1.5, y: 6.1, w: W - 3,
  h: 0.4, fontSize: 14, color: C.text1, align: "center", isTextBox: true, objectName: "Course" });
s.addNotes("EDRIAN (about 30 seconds)\n\nGood morning. We are Edrian Tala, Harry Verdeflor and Marc Lawrence David. Our project is HeatCast NCR. " +
  "Our question is simple: can machine learning predict tomorrow's heat level in Metro Manila better than just copying today's level? " +
  "We will show you the data, how we compared three models fairly, the result on an untouched test year, and then a live demo.");

// ================= 2. Problem and data =================
s = content("THE PROBLEM AND THE DATA", "Introduction", "Next-day heat risk for the 16 cities of Metro Manila", 6.2);
s.addText([
  { text: "Schools, employers of outdoor workers and city offices must decide a day ahead whether to move activities, prepare water and cooling, or warn residents.", options: { breakLine: true, paraSpaceAfter: 12 } },
  { text: "We predict the PAGASA level of tomorrow's highest heat index for each city, from today's weather in that city.", options: {} },
], { x: 0.95, y: 2.3, w: 5.25, h: 2.4, fontSize: 18, color: C.text1, valign: "top", margin: 0, isTextBox: true, objectName: "Problem text" });
s.addText("The five PAGASA heat index levels", { x: 0.95, y: 4.95, w: 5.25, h: 0.3, fontSize: 12, color: HEX.muted, margin: 0,
  isTextBox: true, objectName: "Levels label" });
const lv = [["Not Hazardous", "below 27 °C", HEX.nh, "FFFFFF"], ["Caution", "27–32 °C", HEX.caution, HEX.dark],
  ["Extreme Caution", "33–41 °C", HEX.ec, HEX.dark], ["Danger", "42–51 °C", HEX.danger, "FFFFFF"], ["Extreme Danger", "52 °C and up", HEX.xdanger, "FFFFFF"]];
lv.forEach(([n, r, f, t], i) => {
  s.addText([{ text: n, options: { bold: true, breakLine: true } }, { text: r }], { x: 0.95 + i * 1.065, y: 5.3, w: 1.0, h: 0.72,
    fill: { color: f }, fontSize: 11, color: t, align: "center", valign: "middle", margin: 2, isTextBox: true, objectName: "Level " + n });
});
const tiles = [["16", "cities of the National Capital Region, each with its own row"], ["29,168", "city-days from 2021 to 2025 (ERA5 weather via Open-Meteo)"],
  ["5 + city", "inputs about today: heat index, lowest temperature, rain, pressure, sunshine"], ["1 day", "ahead: the target is tomorrow's PAGASA level in that city"]];
tiles.forEach(([big, lab], i) => {
  const x = 6.75 + (i % 2) * 2.9, y = 2.3 + Math.floor(i / 2) * 1.92;
  s.addShape(pres.ShapeType.rect, { x, y, w: 2.75, h: 1.75, fill: { color: HEX.cream }, line: { type: "none" }, objectName: "Tile " + big });
  s.addText(big, { x: x + 0.2, y: y + 0.15, w: 2.35, h: 0.7, fontFace: "Cambria", fontSize: 38, color: HEX.burnt, margin: 0, valign: "middle", isTextBox: true });
  s.addText(lab, { x: x + 0.2, y: y + 0.88, w: 2.35, h: 0.75, fontSize: 13, color: C.text1, margin: 0, valign: "top", isTextBox: true });
});
s.addNotes("EDRIAN (about 1 minute)\n\nAir temperature alone understates how hot it feels when it is humid; the heat index combines both. " +
  "PAGASA groups it into five levels, shown at the bottom left. Danger starts at 42 degrees. " +
  "Schools, employers of outdoor workers and city offices need to know a day ahead whether tomorrow will reach Danger. " +
  "Our data: the 16 cities of the NCR, 29,168 city-days from 2021 to 2025, built from hourly ERA5 weather from Open-Meteo. " +
  "Each row has five values about today plus the city, and the target is tomorrow's level in that same city.");

// ================= 3. What the data showed =================
pres.addSection({ title: "Data" });
s = content("WHAT THE DATA SHOWED", "Data", "Three findings, three decisions (training days only)", 6.2);
const finds = [
  ["7.9%", "of rows are Danger; 78.5% are Extreme Caution", "So we judge models by macro F1 and Danger recall, not accuracy, and try class weights."],
  ["Apr–Jun", "Danger peaks in April to June (31% of May rows) and never occurs in December to February", "So the split follows time, never a random shuffle."],
  ["17% vs 2%", "Danger rows in Malabon, Navotas and Valenzuela vs Muntinlupa and San Juan", "So every city keeps its own row, and the city is an input."],
];
finds.forEach(([big, f, d], i) => {
  const y = 2.3 + i * 1.45;
  s.addText(big, { x: 0.95, y, w: 2.05, h: 0.75, fontFace: "Cambria", fontSize: 30, color: HEX.burnt, margin: 0, valign: "top", isTextBox: true, objectName: "Finding number " + (i + 1) });
  s.addText([{ text: f, options: { bold: true, breakLine: true } }, { text: d, options: { color: HEX.muted } }],
    { x: 3.1, y, w: 3.5, h: 1.3, fontSize: 14, color: C.text1, margin: 0, valign: "top", paraSpaceAfter: 4, isTextBox: true, objectName: "Finding text " + (i + 1) });
});
const months = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"];
s.addChart(pres.ChartType.bar, [
  { name: "Not Hazardous", labels: months, values: [0.5, 0.6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0] },
  { name: "Caution", labels: months, values: [62.0, 29.3, 13.5, 1.9, 0, 0, 6.3, 2.8, 6.3, 3.2, 2.2, 34.6] },
  { name: "Extreme Caution", labels: months, values: [37.5, 70.1, 83.6, 86.0, 68.9, 78.1, 84.8, 89.9, 86.9, 96.1, 95.8, 64.4] },
  { name: "Danger", labels: months, values: [0, 0, 2.9, 12.1, 31.1, 21.9, 8.9, 7.3, 6.8, 0.8, 2.0, 0] },
], { x: 6.85, y: 2.2, w: 5.6, h: 4.35, barDir: "col", barGrouping: "percentStacked", barGapWidthPct: 35,
  chartColors: [HEX.nh, HEX.caution, HEX.ec, HEX.danger], showTitle: true, title: "Share of each level by month", titleFontSize: 14,
  titleColor: HEX.dark, titleFontFace: "+mn-lt", showLegend: true, legendPos: "b", legendFontSize: 11, legendFontFace: "+mn-lt", legendColor: HEX.dark,
  catAxisLabelColor: HEX.muted, valAxisLabelColor: HEX.muted, catAxisLabelFontSize: 11, valAxisLabelFontSize: 10,
  catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", valGridLine: { color: HEX.grid, size: 0.5 }, catGridLine: { style: "none" },
  valAxisLabelFormatCode: "0%", objectName: "Chart level by month" });
s.addNotes("MARC (about 1 minute 30)\n\nWe looked at the training days only, so nothing from the test year guided a decision. Three findings mattered most. " +
  "First, the levels are very unbalanced: Danger is only 7.9% of rows and Extreme Caution 78.5%, so a model that always says Extreme Caution would be 78% accurate. " +
  "That is why we judge the models with macro F1 and Danger recall, not accuracy, and why we tried class weights. " +
  "Second, the chart: Danger is seasonal. It peaks from April to June, 31% of May rows, and never happens from December to February. So our split follows time. " +
  "Third, cities differ a lot: Malabon, Navotas and Valenzuela have Danger on 17% of days, Muntinlupa and San Juan on 2%, so every city keeps its own row and the city is an input. " +
  "We also checked missing values and duplicates (none) and kept storm days, because they are real weather, not errors.");

// ================= 4. How we compared fairly =================
pres.addSection({ title: "Method" });
s = content("HOW WE COMPARED FAIRLY", "Method", "Same split, same folds and same scoring for every model", 6.6);
const x0 = 0.95, trainW = 9.05, testX = 10.12, testW = 2.28;
["2021", "2022", "2023", "2024"].forEach((yr, i) => s.addText(yr, { x: x0 + i * (trainW / 4), y: 2.2, w: 1.0, h: 0.3, fontSize: 12,
  color: HEX.muted, margin: 0, isTextBox: true }));
s.addText("2025", { x: testX, y: 2.2, w: 1.0, h: 0.3, fontSize: 12, color: HEX.muted, margin: 0, isTextBox: true });
s.addText("Training days: 2021-01-01 to 2024-12-27 (23,312 rows)", { x: x0, y: 2.55, w: trainW, h: 0.55, fill: { color: HEX.peach },
  fontSize: 15, color: C.text1, align: "center", valign: "middle", isTextBox: true, objectName: "Training bar" });
s.addText("Test: 2025, used once", { x: testX, y: 2.55, w: testW, h: 0.55, fill: { color: HEX.burnt }, fontSize: 15, color: "FFFFFF",
  bold: true, align: "center", valign: "middle", isTextBox: true, objectName: "Test bar" });
s.addText("one day skipped between them", { x: 8.1, y: 3.13, w: 3.6, h: 0.28, fontSize: 11, color: HEX.muted, align: "right", margin: 0, isTextBox: true });
const day = trainW / 1457;
for (let k = 1; k <= 5; k++) {
  const y = 3.5 + (k - 1) * 0.27, chk = 247 + 242 * (k - 1);
  s.addShape(pres.ShapeType.rect, { x: x0, y, w: (chk - 1) * day, h: 0.2, fill: { color: "EBC9A6" }, line: { type: "none" }, objectName: "Fold learn " + k });
  s.addShape(pres.ShapeType.rect, { x: x0 + chk * day, y, w: 242 * day, h: 0.2, fill: { color: HEX.ec }, line: { type: "none" }, objectName: "Fold check " + k });
}
s.addShape(pres.ShapeType.rect, { x: testX, y: 3.58, w: 0.22, h: 0.18, fill: { color: "EBC9A6" }, line: { type: "none" } });
s.addText("5 folds: learn from earlier days", { x: testX + 0.3, y: 3.5, w: 2.0, h: 0.32, fontSize: 11, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
s.addShape(pres.ShapeType.rect, { x: testX, y: 3.98, w: 0.22, h: 0.18, fill: { color: HEX.ec }, line: { type: "none" } });
s.addText("check on the next block", { x: testX + 0.3, y: 3.9, w: 2.0, h: 0.32, fontSize: 11, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
const cards = [["Primary metric", "Macro F1 over Caution, Extreme Caution and Danger, so every level counts equally."],
  ["Selection rule", "First catch more Danger days than the baseline; then the highest macro F1 wins."],
  ["Baseline to beat", "Copy today: tomorrow's level is today's level in the same city."]];
cards.forEach(([h, t], i) => {
  const x = 0.95 + i * 3.88;
  s.addShape(pres.ShapeType.rect, { x, y: 5.05, w: 3.69, h: 1.45, fill: { color: HEX.cream }, line: { type: "none" }, objectName: "Card " + h });
  s.addText([{ text: h, options: { fontFace: "Cambria", fontSize: 18, color: HEX.burnt, breakLine: true } }, { text: t, options: { fontSize: 14, color: HEX.dark } }],
    { x: x + 0.2, y: 5.15, w: 3.3, h: 1.25, margin: 0, valign: "top", paraSpaceAfter: 4, isTextBox: true });
});
s.addNotes("HARRY (about 1 minute)\n\nTo compare the models fairly, all three used exactly the same setup. " +
  "The data is time-ordered, so we split by date, never at random: 2021 to 2024 for training, and the last 365 days, 2025, for the final test, which we used only once. " +
  "One day is skipped between them so the last training label is not the first test day. " +
  "All tuning happened inside the training days, on five time-ordered folds: each fold learns from earlier days and is checked on the next block. " +
  "Our main score is macro F1 over Caution, Extreme Caution and Danger. The rule we fixed in advance: a model must first catch more Danger days than the baseline, " +
  "and among those the highest macro F1 wins. The baseline is simply copying today's level.");

// ================= 5. Three models =================
s = content("THREE MODELS VS. THE RULE", "Method", "Five-fold cross-validation on 2021 to 2024: mean over the folds", 6.6);
s.addChart(pres.ChartType.bar, [
  { name: "Macro F1 (core 3 levels)", labels: ["Copy-today rule", "Logistic Regression", "Random Forest", "Gradient Boosting"], values: [0.679, 0.632, 0.653, 0.643] },
  { name: "Danger recall", labels: ["Copy-today rule", "Logistic Regression", "Random Forest", "Gradient Boosting"], values: [0.518, 0.276, 0.672, 0.670] },
], { x: 0.85, y: 2.15, w: 6.7, h: 4.45, barDir: "col", barGrouping: "clustered", barGapWidthPct: 60, chartColors: ["E9A26B", HEX.burnt],
  showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.000", dataLabelFontSize: 12, dataLabelColor: HEX.dark, dataLabelFontFace: "+mn-lt",
  valAxisMinVal: 0, valAxisMaxVal: 1, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
  catAxisLabelColor: HEX.dark, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt", showLegend: true, legendPos: "t", legendFontSize: 12,
  legendFontFace: "+mn-lt", legendColor: HEX.dark, objectName: "Chart models" });
const models = [
  ["Logistic Regression", "Harry", "C = 10, no class weights", "Most precise, but caught only 28% of Danger days.", false],
  ["Random Forest", "Edrian", "500 trees, depth 12, balanced weights", "Best macro F1 of the three and 67% of Danger days caught.", true],
  ["Gradient Boosting", "Marc", "200 trees, depth 2, balanced weights", "Almost the same as Random Forest (0.643 vs 0.653).", false],
];
models.forEach(([n, who, set, res, sel], i) => {
  const y = 2.2 + i * 1.42;
  s.addShape(pres.ShapeType.rect, { x: 7.9, y, w: 4.5, h: 1.3, fill: { color: sel ? HEX.peach : HEX.cream }, line: { type: "none" }, objectName: "Model " + n });
  s.addText([{ text: n, options: { fontFace: "Cambria", fontSize: 18, bold: true, color: HEX.dark } }, { text: "   " + who, options: { fontSize: 12, color: HEX.muted, breakLine: true } },
    { text: set, options: { fontSize: 12, color: HEX.muted, breakLine: true } }, { text: res, options: { fontSize: 14, color: HEX.dark } }],
    { x: 8.1, y: y + 0.08, w: 3.2, h: 1.15, margin: 0, valign: "top", isTextBox: true });
  if (sel) s.addText("SELECTED", { x: 11.2, y: y + 0.12, w: 1.05, h: 0.32, fill: { color: HEX.burnt }, fontSize: 11, bold: true, color: "FFFFFF",
    align: "center", valign: "middle", charSpacing: 1, margin: 0, isTextBox: true, objectName: "Selected tag" });
});
s.addNotes("HARRY (about 1 minute 30, each of us says one line)\n\nHARRY: These are the cross-validation results. The light bars are macro F1, the dark bars Danger recall. " +
  "The copy-today rule, on the left, is hard to beat: macro F1 0.679. None of our models beat it on macro F1. " +
  "My model, Logistic Regression, was the most precise when it called Danger, but it caught only 28% of Danger days.\n" +
  "EDRIAN: Random Forest with balanced class weights caught 67% of Danger days, more than the rule, and had the best macro F1 of the three, so by our rule it was selected.\n" +
  "MARC: Gradient Boosting was almost the same as Random Forest, 0.643 against 0.653, which is within the spread between folds.\n" +
  "HARRY: So the trees trade a little overall score for many more Danger days caught.");

// ================= 6. Final test =================
pres.addSection({ title: "Results" });
s = content("FINAL TEST ON 2025", "Results", "The selected Random Forest, run once on 365 untouched days", 6.6);
const stats = [["84%", "of Danger days caught", "293 of 347  ·  copy-today rule: 60%", HEX.danger],
  ["36%", "of Danger warnings right", "293 of 816  ·  about 2 false alarms per hit", HEX.burnt],
  ["0.614", "macro F1 (core 3 levels)", "copy-today rule: 0.675  ·  accuracy 0.731 vs 0.824", HEX.dark]];
stats.forEach(([big, lab, sub, col], i) => {
  const x = 0.95 + i * 3.88;
  s.addShape(pres.ShapeType.rect, { x, y: 2.3, w: 3.69, h: 2.7, fill: { color: HEX.cream }, line: { type: "none" }, objectName: "Stat " + big });
  s.addText(big, { x: x + 0.25, y: 2.45, w: 3.2, h: 1.25, fontFace: "Cambria", fontSize: 66, color: col, margin: 0, valign: "middle", isTextBox: true });
  s.addText(lab, { x: x + 0.25, y: 3.75, w: 3.2, h: 0.45, fontSize: 17, bold: true, color: HEX.dark, margin: 0, valign: "top", isTextBox: true });
  s.addText(sub, { x: x + 0.25, y: 4.25, w: 3.2, h: 0.6, fontSize: 13, color: HEX.muted, margin: 0, valign: "top", isTextBox: true });
});
s.addText("An early-warning aid, not a better all-round forecaster: it catches far more Danger days than the rule, at the price of more false alarms.", {
  x: 0.95, y: 5.3, w: 11.45, h: 1.1, fill: { color: HEX.dark }, fontFace: "Cambria", italic: true, fontSize: 20, color: HEX.bg,
  align: "center", valign: "middle", margin: 18, isTextBox: true, objectName: "Takeaway" });
s.addNotes("MARC (about 1 minute)\n\nOnly after choosing the model did we touch the test year, and only once. On 2025 the Random Forest caught 293 of the 347 Danger days, 84%, " +
  "while copying today's level caught 60%. The cost: only 36% of its Danger warnings were right, about two false alarms for every real Danger day. " +
  "Its macro F1, 0.614, and accuracy, 0.731, are below the rule's 0.675 and 0.824. " +
  "So it is not a better all-round forecaster, but it is a useful early warning for users who would rather prepare for a Danger day that does not come than miss one.");

// ================= 7. Live demo =================
s = content("LIVE DEMO", "Results", "heatcast-ncr.streamlit.app", 4.0);
const steps = [["A hot day in Manila", "Heat index 45.5 °C, lowest 29 °C, no rain, 1,008 hPa, 7,000 Wh/m²: Danger, about 90%"],
  ["An impossible value", "Rain of −5 mm: an error with the accepted range, and no prediction"],
  ["An empty form", "Every missing value is named; nothing is filled in silently"]];
steps.forEach(([h, t], i) => {
  const y = 2.35 + i * 1.3;
  s.addShape(pres.ShapeType.ellipse, { x: 0.95, y, w: 0.62, h: 0.62, fill: { color: HEX.burnt }, line: { type: "none" }, objectName: "Step dot " + (i + 1) });
  s.addText(String(i + 1), { x: 0.95, y, w: 0.62, h: 0.62, fontFace: "Cambria", fontSize: 22, color: "FFFFFF", align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addText([{ text: h, options: { fontFace: "Cambria", fontSize: 19, color: HEX.dark, breakLine: true } }, { text: t, options: { fontSize: 14, color: HEX.muted } }],
    { x: 1.85, y: y - 0.05, w: 5.6, h: 1.15, margin: 0, valign: "top", isTextBox: true, objectName: "Step " + (i + 1) });
});
s.addText("The app loads the saved Random Forest (the model we tested) and checks every input; 51 automated tests cover valid, invalid and boundary values.", {
  x: 0.95, y: 6.25, w: 6.5, h: 0.55, fontSize: 12, color: HEX.muted, italic: true, margin: 0, valign: "top", isTextBox: true });
s.addImage({ path: path.join(IMG, "fig8_app.png"), x: 12.4 - 4.45 * 766 / 997, y: 2.15, w: 4.45 * 766 / 997, h: 4.45, altText: "Screenshot of the HeatCast NCR app: a Danger prediction for Manila, the map and the error messages", objectName: "App screenshot" });
s.addShape(pres.ShapeType.rect, { x: 12.4 - 4.45 * 766 / 997, y: 2.15, w: 4.45 * 766 / 997, h: 4.45, fill: { type: "none" }, line: { color: "E2CDBB", width: 0.75 }, objectName: "Screenshot frame" });
s.addNotes("EDRIAN (about 2 minutes, live)\n\nNow the app, live at heatcast-ncr.streamlit.app. (Open it before the talk; the first load can take a minute.)\n" +
  "1. Choose Manila and type a hot day: heat index 45.5, lowest temperature 29, rain 0, pressure 1008, sunshine 7000. Click the button: Danger, about 90%, and Manila turns red on the map. " +
  "Point out the probability bars and the note that it is a decision aid, not a PAGASA advisory.\n" +
  "2. Change rain to -5: the app refuses it and shows the accepted range, with no prediction.\n" +
  "3. Clear all boxes and click: every missing value is named.\n" +
  "If the internet fails, use this screenshot, or run it locally: streamlit run app/streamlit_app.py.");

// ================= 8. Conclusion =================
pres.addSection({ title: "Conclusion" });
s = content("CONCLUSION", "Conclusion", "What we learned", 3.2);
const concl = [["01", "The answer", "No model beat copying today's level on macro F1 or accuracy: tomorrow's heat is mostly today's heat."],
  ["02", "What ML adds", "With balanced class weights, the Random Forest caught 84% of the 2025 Danger days, so we deployed it as an early-warning aid."],
  ["03", "Limits and next steps", "Weather-model estimates, only five years. Next: month and recent-day inputs, a weather forecast input, more years, and a user-set Danger threshold."]];
concl.forEach(([n, h, t], i) => {
  const x = 0.95 + i * 3.88;
  s.addShape(pres.ShapeType.rect, { x, y: 2.3, w: 3.69, h: 3.95, fill: { color: i === 1 ? HEX.peach : HEX.cream }, line: { type: "none" }, objectName: "Conclusion " + n });
  s.addText(n, { x: x + 0.3, y: 2.5, w: 1.5, h: 0.85, fontFace: "Cambria", fontSize: 44, color: HEX.burnt, margin: 0, valign: "top", isTextBox: true });
  s.addText([{ text: h, options: { fontFace: "Cambria", fontSize: 20, color: HEX.dark, breakLine: true } }, { text: t, options: { fontSize: 15, color: HEX.dark } }],
    { x: x + 0.3, y: 3.5, w: 3.1, h: 2.6, margin: 0, valign: "top", paraSpaceAfter: 8, isTextBox: true });
});
s.addNotes("HARRY (about 1 minute)\n\nTo answer our question: no, none of the three models beat simply copying today's level on overall score. Tomorrow's heat is mostly today's heat. " +
  "But machine learning adds something specific: with balanced class weights, the Random Forest caught 84% of the Danger days in 2025, so we deployed it as an early-warning aid. " +
  "Its limits: the data are weather-model estimates, not station readings, and we used only five years. " +
  "Next we would add the month and the previous days' heat index, a weather forecast for tomorrow, more years of data, and let users choose their own Danger threshold.");

// ================= 9. Thank you =================
s = pres.addSlide({ masterName: "Cover", sectionTitle: "Conclusion" });
s.addText("THANK YOU", { x: 0.9, y: 2.5, w: W - 1.8, h: 1.2, fontFace: "Cambria", fontSize: 66, charSpacing: 16, color: C.text1,
  align: "center", valign: "middle", isTextBox: true, objectName: "Thank you" });
s.addText("Questions?", { x: 0.9, y: 3.7, w: W - 1.8, h: 0.7, fontFace: "Cambria", fontSize: 30, italic: true, color: HEX.burnt,
  align: "center", valign: "middle", isTextBox: true, objectName: "Questions" });
s.addText("heatcast-ncr.streamlit.app   ·   github.com/keyyum/heatcast-ncr-simple", { x: (W - 8.4) / 2, y: 5.0, w: 8.4, h: 0.45,
  shape: pres.ShapeType.roundRect, rectRadius: 0.08, fill: { color: "FFFFFF" }, fontSize: 15, color: C.text1, align: "center",
  valign: "middle", isTextBox: true, objectName: "Links" });
s.addNotes("ALL\n\nThank you. We are happy to take questions. Likely questions: why not accuracy (imbalance), why a chronological split (time-ordered data), " +
  "why Random Forest over Gradient Boosting (selection rule; the two are almost tied), and why the model did not beat the rule (tomorrow mostly equals today; only today's values are inputs).");

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
