/**
 * Shipyard — Apps Script: creates the Fitness interview screener form.
 * Run: script.google.com → New project → paste → Run createFitnessForm →
 * authorize → check Execution log for the edit + live URLs.
 */

function createFitnessForm() {
  var form = FormApp.create('Shipyard Interview — Fitness');
  form.setDescription(
    'Thanks for taking a few minutes to help out! This is a short research ' +
    'survey — no right or wrong answers, we\'re just trying to understand ' +
    'how people actually save and use fitness content (workouts, yoga, ' +
    'calisthenics, cooking videos) from Instagram, YouTube and elsewhere. ' +
    'Takes about 3 minutes. Specific, honest answers are more useful to us ' +
    'than "ideal" ones.'
  );

  addItems(form, [
    {type: 'text', title: 'Email', required: true},
    {type: 'text', title: 'Phone number (optional, for text scheduling)'},
    {type: 'checkbox', title: 'What kind of fitness content do you save?', choices: ['Gym workouts', 'Yoga', 'Calisthenics', 'Cooking videos'], other: true},
    {type: 'checkbox', title: 'Where did you find it?', choices: ['Instagram', 'YouTube'], other: true},
    {type: 'choice', title: 'Do you save often? Would you say 10–12 videos a week?', choices: ['Yes, about that often', 'More often', 'Less often'], other: true},
    {type: 'choice', title: 'Where do you primarily save it?', choices: ['Instagram', 'YouTube'], other: true},
    {type: 'text', title: 'Roughly how many fitness content videos/posts do you think you have saved?'},
    {type: 'choice', title: 'Do you organize them somewhere else, like a notes app, for later?', choices: ['Yes', 'No']},
    {type: 'choice', title: 'Do you go back to the saved content in the moment of action — for example when planning to cook, or when at the gym?', choices: ['Yes', 'No', 'Sometimes']},
    {type: 'choice', title: 'Do you find the saved content you remembered and had in mind, or do you give up?', choices: ['Find it', 'Give up']},
    {type: 'choice', title: 'Do you use a separate fitness app while following a workout or cooking video?', choices: ['Yes', 'No']},
    {type: 'paragraph', title: 'What do you do when you cannot find the saved content you\'re looking for?'},
    {type: 'paragraph', title: 'Do you store the links of the content you want to use for later elsewhere, or do you have some other workflow?'},
    {type: 'paragraph', title: 'What is the most annoying part of your current workflow?'},
    {type: 'choice', title: 'Open to a 15–20 min follow-up call this week?', choices: ['Yes', 'No']}
  ]);

  logUrls(form);
}

function addItems(form, items) {
  items.forEach(function (cfg) {
    var item =
      cfg.type === 'text' ? form.addTextItem() :
      cfg.type === 'paragraph' ? form.addParagraphTextItem() :
      cfg.type === 'checkbox' ? form.addCheckboxItem().setChoiceValues(cfg.choices) :
      form.addMultipleChoiceItem().setChoiceValues(cfg.choices);
    item.setTitle(cfg.title);
    if (cfg.required) item.setRequired(true);
    if (cfg.other) item.showOtherOption(true);
  });
}

function logUrls(form) {
  Logger.log('Edit URL: ' + form.getEditUrl());
  Logger.log('Live URL: ' + form.getPublishedUrl());
}
