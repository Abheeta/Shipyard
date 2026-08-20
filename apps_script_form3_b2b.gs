/**
 * Shipyard — Apps Script: creates the Messy Info Workflows (geeky/B2B)
 * interview screener form.
 * Run: script.google.com → New project → paste → Run createB2BForm →
 * authorize → check Execution log for the edit + live URLs.
 */

function createB2BForm() {
  var form = FormApp.create('Shipyard Interview — Messy Info Workflows');
  form.setDescription(
    'For anyone with a repetitive work task involving searching, comparing, ' +
    'reconciling, or organizing information. ~3 min, a real recent example ' +
    'over general opinions.'
  );

  addItems(form, [
    {type: 'text', title: 'Email', required: true},
    {type: 'text', title: 'Phone number (optional, for text scheduling)'},
    {type: 'paragraph', title: 'What\'s something you repeatedly have to search, compare, reconcile, or organize that you hate doing? Walk me through the last time you did it.'},
    {type: 'choice', title: 'What do you currently use to do this?', choices: ['Spreadsheet', 'Script', 'Checklist', 'Notion or similar', 'Manual process', 'Other']},
    {type: 'paragraph', title: 'How often does this happen, and what happens if you make a mistake?'},
    {type: 'choice', title: 'Have you ever paid for software or outsourced part of this?', choices: ['Yes', 'No']},
    {type: 'paragraph', title: 'If a tool could take the raw information and produce the finished result, what would you want it to produce — and what would you still want to check yourself?'},
    {type: 'choice', title: 'Open to a 15–20 min follow-up call this week?', choices: ['Yes', 'No']}
  ]);

  logUrls(form);
}

function addItems(form, items) {
  items.forEach(function (cfg) {
    var item =
      cfg.type === 'text' ? form.addTextItem() :
      cfg.type === 'paragraph' ? form.addParagraphTextItem() :
      form.addMultipleChoiceItem().setChoiceValues(cfg.choices);
    item.setTitle(cfg.title);
    if (cfg.required) item.setRequired(true);
  });
}

function logUrls(form) {
  Logger.log('Edit URL: ' + form.getEditUrl());
  Logger.log('Live URL: ' + form.getPublishedUrl());
}
