/**
 * Shipyard — Apps Script: creates the Saved Content interview screener form.
 * Run: script.google.com → New project → paste → Run createSavedContentForm →
 * authorize → check Execution log for the edit + live URLs.
 */

function createSavedContentForm() {
  var form = FormApp.create('Shipyard Interview — Saved Content');
  form.setDescription(
    'For anyone who saves recipes, articles, or other useful content from ' +
    'social media. ~3 min, a real recent example over general opinions.'
  );

  addItems(form, [
    {type: 'text', title: 'Email', required: true},
    {type: 'text', title: 'Phone number (optional, for text scheduling)'},
    {type: 'paragraph', title: 'What\'s the last useful thing you saved from Instagram, TikTok, YouTube or elsewhere — and have you actually used it yet?'},
    {type: 'paragraph', title: 'What usually happens after you save something?'},
    {type: 'paragraph', title: 'How do you find something you saved again when you actually need it?'},
    {type: 'choice', title: 'Do you save the same thing in multiple places, or screenshot/text things to yourself because saving isn\'t enough?', choices: ['Yes', 'No']},
    {type: 'choice', title: 'How often do saved items actually become something you do, buy, cook, learn, visit or create?', choices: ['Most of the time', 'Sometimes', 'Rarely', 'Almost never']},
    {type: 'paragraph', title: 'Would one place for content from every platform be useful to you? Why or why not?'},
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
