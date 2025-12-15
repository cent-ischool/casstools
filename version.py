history = lambda: [
    {"ver" : "0.2.0-20251215", "text": "Added interact_quiz module for UI rendering of self-check questions." },
    {"ver" : "0.1.3-20240204", "text": "Autosave before any validate or check is run." },
    {"ver" : "0.1.2-20240201", "text": "Added support for tests through python assert statement" },
    {"ver" : "0.1.1-20240125", "text": "Fixed bugs in code similatiry tests for homework checker." },
    {"ver" : "0.1.0-20240120", "text": "Customizable code similarity tests. Small issue with assignment submission" },
    {"ver" : "0.1.0-20240118", "text": "Change to synax tree lab compare drop similarity down to 25%" },
    {"ver" : "0.1.0-20240106", "text": "Initial release" }
]

current= lambda: history()[0]['ver']
