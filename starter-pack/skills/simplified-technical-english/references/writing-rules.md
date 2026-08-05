# STE writing rules — full, with examples

Pragmatic adaptation of ASD-STE100. Nine rule groups. Each has the rule, why, and a before/after.

## 1. Short sentences
Procedures ≤ 20 words. Descriptive text ≤ 25 words. Long sentences hide multiple ideas and multiple failure points.

- ❌ "After you have confirmed that the token is still valid, which you can do by checking the expiry field, run the sync script, and if it fails, retry."
- ✅ "Check the token expiry field. If the token is valid, run the sync script. If the sync fails, retry it."

## 2. One instruction per sentence
Each instruction is a separate sentence or a separate numbered step. A reader executes one action at a time.

- ❌ "Open the config and set `debug=true` and restart the service."
- ✅ "1. Open the config file. 2. Set `debug=true`. 3. Restart the service."

## 3. Active voice + correct mood/tense
Active voice names the actor. Present tense for descriptions. Imperative for instructions.

- ❌ "The cache should be cleared before the deploy is triggered." (passive, modal, vague actor)
- ✅ "Clear the cache. Then trigger the deploy." (imperative, one action each)
- ❌ "The response is returned by the endpoint." → ✅ "The endpoint returns the response."

## 4. One term, one meaning (consistent terminology)
Choose one word per concept and reuse it. Synonym variety — praised in literary writing — causes doubt in technical writing ("is a folder the same as a directory?").

- ❌ mixing "directory", "folder", "path" for the same thing.
- ✅ pick `directory` and use only `directory`.
- Also: never reuse one word for two concepts. If "key" means both an API key and a map key, rename one.

## 5. No ambiguous reference
A pronoun must have exactly one possible referent. When in doubt, repeat the noun.

- ❌ "Connect the client to the server and restart it." (restart which?)
- ✅ "Connect the client to the server. Then restart the server."

## 6. Limit noun clusters (max 3 words)
Long strings of stacked nouns are ambiguous. Break them with prepositions or a relative clause.

- ❌ "runtime cache invalidation policy handler"
- ✅ "the handler for the runtime cache-invalidation policy" — or better, name it and define it once.

## 7. Define abbreviations once, then be consistent
Spell out at first use with the abbreviation in parentheses. After that, use only the abbreviation.

- ✅ "Simplified Technical English (STE) reduces ambiguity. STE uses short sentences."
- ❌ switching between "STE" and "Simplified Technical English" at random.

## 8. Prefer positive, actionable statements
Tell the reader what to do. State conditions and consequences explicitly. Structure warnings as: condition → consequence → action.

- ❌ "Don't run this without a backup." → ✅ "Before you run this command, create a backup."
- ✅ warning form: "If you run `DROP TABLE`, you delete all rows permanently. Create a backup first."

## 9. Be concrete; keep lists parallel
Replace vague words with measurable facts. Keep every list item grammatically parallel.

- ❌ "The job runs quickly and handles errors gracefully."
- ✅ "The job completes within 5 seconds. On a non-zero exit code, it retries twice, then logs the error."
- Parallel list — all imperative:
  - ✅ "Install the dependencies. / Build the project. / Run the tests."
  - ❌ "Install the dependencies. / Building the project. / Tests should run."
